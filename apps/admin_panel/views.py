from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Count, Sum, Avg
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from apps.products.models import Product, Category, ProductImage
from apps.orders.models import Order, OrderItem, OrderTracking
from apps.cart.models import Cart, CartItem
from apps.reviews.models import Review
from apps.orders.serializers import OrderSerializer, OrderTrackingSerializer
from .serializers import DashboardStatsSerializer, SalesReportSerializer

class AdminPermission(permissions.BasePermission):
    """Custom permission for admin users"""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class AdminPanelViewSet(viewsets.ViewSet):
    permission_classes = [AdminPermission]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics"""
        stats = {
            'total_users': User.objects.count(),
            'total_products': Product.objects.count(),
            'total_orders': Order.objects.count(),
            'total_revenue': Order.objects.filter(
                status='delivered'
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'pending_orders': Order.objects.filter(status='pending').count(),
            'top_products': list(
                Product.objects.order_by('-total_reviews').values_list('name', flat=True)[:5]
            ),
            'recent_orders': list(
                Order.objects.order_by('-created_at').values(
                    'id', 'order_number', 'status', 'total_amount', 'created_at'
                )[:10]
            ),
        }
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sales_report(self, request):
        """Get sales report"""
        date_range = request.query_params.get('days', 30)
        
        orders = Order.objects.filter(status='delivered').values('created_at__date').annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('id'),
            average_order_value=Avg('total_amount')
        ).order_by('-created_at__date')[:int(date_range)]
        
        serializer = SalesReportSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_insights(self, request):
        """Get user insights"""
        insights = {
            'total_users': User.objects.count(),
            'new_users_this_month': User.objects.filter(
                date_joined__month=timezone.now().month
            ).count(),
            'active_users': User.objects.filter(orders__isnull=False).distinct().count(),
            'top_customers': list(
                User.objects.annotate(total_spent=Sum('orders__total_amount')).order_by(
                    '-total_spent'
                ).values('username', 'total_spent')[:10]
            ),
        }
        return Response(insights)
    
    @action(detail=False, methods=['get'])
    def product_insights(self, request):
        """Get product insights"""
        insights = {
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(status='active').count(),
            'low_stock_products': Product.objects.filter(stock__lt=10).count(),
            'top_rated': list(
                Product.objects.order_by('-average_rating').values(
                    'id', 'name', 'average_rating', 'total_reviews'
                )[:10]
            ),
            'least_rated': list(
                Product.objects.filter(average_rating__gt=0).order_by(
                    'average_rating'
                ).values('id', 'name', 'average_rating', 'total_reviews')[:10]
            ),
        }
        return Response(insights)
    
    @action(detail=False, methods=['get'])
    def order_insights(self, request):
        """Get order insights"""
        insights = {
            'total_orders': Order.objects.count(),
            'pending': Order.objects.filter(status='pending').count(),
            'processing': Order.objects.filter(status='processing').count(),
            'shipped': Order.objects.filter(status='shipped').count(),
            'delivered': Order.objects.filter(status='delivered').count(),
            'cancelled': Order.objects.filter(status='cancelled').count(),
            'average_order_value': Order.objects.aggregate(
                Avg('total_amount')
            )['total_amount__avg'] or 0,
        }
        return Response(insights)

    @action(detail=False, methods=['get'])
    def orders(self, request):
        """List all orders with filters"""
        orders = Order.objects.select_related('user', 'shipping_address').prefetch_related('items').order_by('-created_at')
        
        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        search = request.query_params.get('search')
        if search:
            orders = orders.filter(order_number__icontains=search)
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='orders/(?P<order_id>[^/.]+)')
    def order_detail(self, request, order_id=None):
        """Get single order detail"""
        try:
            order = Order.objects.select_related('user', 'shipping_address').prefetch_related('items').get(id=order_id)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['patch'], url_path='orders/(?P<order_id>[^/.]+)/update_status')
    def update_order_status(self, request, order_id=None):
        """Update order status"""
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')
        valid_statuses = [s[0] for s in Order.ORDER_STATUS]
        if new_status not in valid_statuses:
            return Response({'detail': f'Invalid status. Choose from: {valid_statuses}'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = new_status
        order.save()
        
        # Update tracking status too
        try:
            tracking = order.tracking
            tracking_map = {
                'confirmed': 'confirmed',
                'processing': 'processing',
                'shipped': 'shipped',
                'delivered': 'delivered',
                'cancelled': 'failed_delivery',
            }
            if new_status in tracking_map:
                tracking.status = tracking_map[new_status]
                if new_status == 'delivered':
                    tracking.actual_delivery = timezone.now()
                tracking.save()
        except OrderTracking.DoesNotExist:
            pass
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def products(self, request):
        """List all products for admin"""
        from apps.products.serializers import ProductSerializer
        products = Product.objects.all().order_by('-created_at')
        
        status_filter = request.query_params.get('status')
        if status_filter:
            products = products.filter(status=status_filter)
        
        search = request.query_params.get('search')
        if search:
            products = products.filter(name__icontains=search)
        
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], url_path='products/(?P<product_id>[^/.]+)/update')
    def update_product(self, request, product_id=None):
        """Update product details"""
        from apps.products.serializers import ProductSerializer
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data.copy()
        for field in ('discount_percentage', 'stock'):
            if field in data and data[field] == '':
                data[field] = 0
        for field in ('mrp',):
            if field in data and data[field] == '':
                data[field] = None
        serializer = ProductSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def users(self, request):
        """List all users"""
        users = User.objects.annotate(
            order_count=Count('orders'),
            total_spent=Sum('orders__total_amount')
        ).order_by('-date_joined')
        
        data = [{
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'is_staff': u.is_staff,
            'is_active': u.is_active,
            'date_joined': u.date_joined,
            'order_count': u.order_count,
            'total_spent': u.total_spent or 0,
        } for u in users]
        
        return Response(data)

    # ─── PRODUCT CRUD ──────────────────────────────────────

    @action(detail=False, methods=['post'], url_path='products/create')
    def create_product(self, request):
        """Create a new product"""
        from apps.products.serializers import ProductSerializer
        data = request.data.copy()
        if not data.get('slug') and data.get('name'):
            base_slug = slugify(data['name'])
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            data['slug'] = slug
        for field in ('discount_percentage', 'stock'):
            if field in data and data[field] == '':
                data[field] = 0
        for field in ('mrp',):
            if field in data and data[field] == '':
                data[field] = None
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], url_path='products/(?P<product_id>[^/.]+)/delete')
    def delete_product(self, request, product_id=None):
        """Delete a product"""
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return Response({'detail': 'Product deleted.'}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='products/(?P<product_id>[^/.]+)/detail')
    def product_detail(self, request, product_id=None):
        """Get single product detail"""
        from apps.products.serializers import ProductDetailSerializer
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductDetailSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='products/(?P<product_id>[^/.]+)/upload_image')
    def upload_product_image(self, request, product_id=None):
        """Upload image for a product"""
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        image = request.FILES.get('image')
        if not image:
            return Response({'detail': 'No image provided.'}, status=status.HTTP_400_BAD_REQUEST)

        is_primary = request.data.get('is_primary', 'false').lower() == 'true'
        set_main = request.data.get('set_main', 'false').lower() == 'true'

        if set_main:
            product.image = image
            product.save()
            return Response({'detail': 'Main product image updated.', 'image': product.image.url})

        alt_text = request.data.get('alt_text', product.name)
        if is_primary:
            ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
        product_image = ProductImage.objects.create(
            product=product, image=image, alt_text=alt_text, is_primary=is_primary
        )
        return Response({
            'id': product_image.id,
            'image': product_image.image.url,
            'alt_text': product_image.alt_text,
            'is_primary': product_image.is_primary,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'], url_path='products/images/(?P<image_id>[^/.]+)/delete')
    def delete_product_image(self, request, image_id=None):
        """Delete a product image"""
        try:
            img = ProductImage.objects.get(id=image_id)
            img.delete()
            return Response({'detail': 'Image deleted.'}, status=status.HTTP_204_NO_CONTENT)
        except ProductImage.DoesNotExist:
            return Response({'detail': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)

    # ─── CATEGORY MANAGEMENT ──────────────────────────────

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """List all categories"""
        cats = Category.objects.all().order_by('name')
        data = [{
            'id': c.id, 'name': c.name, 'slug': c.slug,
            'description': c.description, 'is_active': c.is_active,
            'image': c.image.url if c.image else None,
            'product_count': c.products.count(),
        } for c in cats]
        return Response(data)

    @action(detail=False, methods=['post'], url_path='categories/create')
    def create_category(self, request):
        """Create a new category"""
        name = request.data.get('name', '').strip()
        if not name:
            return Response({'detail': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        slug = slugify(name)
        if Category.objects.filter(slug=slug).exists():
            return Response({'detail': 'Category already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        cat = Category.objects.create(
            name=name, slug=slug,
            description=request.data.get('description', ''),
            is_active=request.data.get('is_active', True),
        )
        return Response({'id': cat.id, 'name': cat.name, 'slug': cat.slug}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'], url_path='categories/(?P<cat_id>[^/.]+)/update')
    def update_category(self, request, cat_id=None):
        """Update a category"""
        try:
            cat = Category.objects.get(id=cat_id)
        except Category.DoesNotExist:
            return Response({'detail': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)
        for field in ['name', 'description', 'is_active']:
            if field in request.data:
                setattr(cat, field, request.data[field])
        cat.save()
        return Response({'id': cat.id, 'name': cat.name, 'slug': cat.slug, 'is_active': cat.is_active})

    # ─── ORDER TRACKING ───────────────────────────────────

    @action(detail=False, methods=['patch'], url_path='orders/(?P<order_id>[^/.]+)/update_tracking')
    def update_order_tracking(self, request, order_id=None):
        """Update order tracking details (carrier, tracking number, location, estimated delivery)"""
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        tracking, _ = OrderTracking.objects.get_or_create(order=order)
        for field in ['tracking_number', 'carrier', 'location', 'estimated_delivery', 'status']:
            if field in request.data:
                setattr(tracking, field, request.data[field])
        if request.data.get('status') == 'delivered':
            tracking.actual_delivery = timezone.now()
        tracking.save()

        serializer = OrderTrackingSerializer(tracking)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], url_path='orders/(?P<order_id>[^/.]+)/update_notes')
    def update_order_notes(self, request, order_id=None):
        """Update order admin notes"""
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        order.notes = request.data.get('notes', '')
        order.save()
        return Response({'detail': 'Notes updated.', 'notes': order.notes})

    # ─── CART MANAGEMENT ──────────────────────────────────

    @action(detail=False, methods=['get'])
    def carts(self, request):
        """List all active carts with items"""
        carts = Cart.objects.prefetch_related('items__product').select_related('user').all()
        data = []
        for cart in carts:
            items = cart.items.all()
            if not items.exists():
                continue
            data.append({
                'id': cart.id,
                'user': {
                    'id': cart.user.id,
                    'username': cart.user.username,
                    'first_name': cart.user.first_name,
                    'email': cart.user.email,
                },
                'total_items': cart.total_items,
                'total_price': str(cart.total_price),
                'items': [{
                    'id': item.id,
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'product_image': item.product.image.url if item.product.image else None,
                    'quantity': item.quantity,
                    'price': str(item.price),
                    'total_price': str(item.total_price),
                } for item in items],
            })
        return Response(data)

    @action(detail=False, methods=['delete'], url_path='carts/(?P<cart_id>[^/.]+)/clear')
    def clear_cart(self, request, cart_id=None):
        """Clear all items from a user's cart"""
        try:
            cart = Cart.objects.get(id=cart_id)
            cart.items.all().delete()
            return Response({'detail': 'Cart cleared.'})
        except Cart.DoesNotExist:
            return Response({'detail': 'Cart not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'], url_path='carts/items/(?P<item_id>[^/.]+)/remove')
    def remove_cart_item(self, request, item_id=None):
        """Remove a specific item from a cart"""
        try:
            item = CartItem.objects.get(id=item_id)
            item.delete()
            return Response({'detail': 'Item removed.'})
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)
