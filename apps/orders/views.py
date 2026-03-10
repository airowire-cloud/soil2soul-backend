from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.text import slugify
import uuid
from decimal import Decimal
from .models import Order, OrderItem, OrderTracking
from .serializers import OrderSerializer, OrderTrackingSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')
    
    def create(self, request, *args, **kwargs):
        """Create order with items from request data"""
        from apps.products.models import Product
        
        items_data = request.data.get('items', [])
        shipping_address_id = request.data.get('shipping_address')
        
        if not items_data:
            return Response({'detail': 'No items provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate totals
        subtotal = Decimal('0')
        order_items = []
        for item_data in items_data:
            try:
                product = Product.objects.get(id=item_data.get('product'))
                qty = int(item_data.get('quantity', 1))
                price = product.price
                item_total = price * qty
                subtotal += item_total
                order_items.append({
                    'product': product,
                    'product_name': product.name,
                    'quantity': qty,
                    'price_per_unit': price,
                    'total_price': item_total,
                })
            except Product.DoesNotExist:
                return Response({'detail': f'Product {item_data.get("product")} not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        shipping_cost = Decimal('0') if subtotal > 50 else Decimal('5')
        tax = subtotal * Decimal('0.18')
        total_amount = subtotal + shipping_cost + tax
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            order_number=f"ORD-TEMP-{uuid.uuid4().hex[:8].upper()}",
            shipping_address_id=shipping_address_id,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax=tax,
            total_amount=total_amount,
        )
        order.order_number = self.generate_order_number(order.id)
        order.save()
        
        # Create order items
        for item in order_items:
            OrderItem.objects.create(order=order, **item)
        
        # Create tracking record
        OrderTracking.objects.create(order=order)
        
        # Send confirmation email
        self.send_order_confirmation(order)
        
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        order.order_number = self.generate_order_number(order.id)
        order.save()
        OrderTracking.objects.create(order=order)
        self.send_order_confirmation(order)
    
    @staticmethod
    def generate_order_number(order_id):
        """Generate unique order number"""
        return f"ORD-{order_id}-{uuid.uuid4().hex[:8].upper()}"
    
    @staticmethod
    def send_order_confirmation(order):
        """Send order confirmation email"""
        try:
            subject = f"Order Confirmation - {order.order_number}"
            message = f"Your order {order.order_number} has been confirmed. Total: {order.total_amount}"
            send_mail(subject, message, 'noreply@soilandsoul.com', [order.user.email])
        except:
            pass
    
    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        """Get order tracking information"""
        order = self.get_object()
        tracking = order.tracking
        serializer = OrderTrackingSerializer(tracking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        
        if order.status in ['delivered', 'shipped', 'returned']:
            return Response(
                {'detail': f'Cannot cancel order with status: {order.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent_orders(self, request):
        """Get user's recent orders"""
        orders = self.get_queryset()[:10]
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def order_stats(self, request):
        """Get user's order statistics"""
        orders = self.get_queryset()
        
        stats = {
            'total_orders': orders.count(),
            'pending_orders': orders.filter(status='pending').count(),
            'completed_orders': orders.filter(status='delivered').count(),
            'total_spent': sum(o.total_amount for o in orders),
        }
        
        return Response(stats)
