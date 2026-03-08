from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from apps.products.models import Product
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """Get current user's cart"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        if not product_id:
            return Response(
                {'detail': 'product_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity, 'price': product.price}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from cart"""
        cart_item_id = request.data.get('cart_item_id')
        
        if not cart_item_id:
            return Response(
                {'detail': 'cart_item_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart__user=request.user)
            cart = cart_item.cart
            cart_item.delete()
            
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response(
                {'detail': 'Cart item not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Update cart item quantity"""
        cart_item_id = request.data.get('cart_item_id')
        quantity = request.data.get('quantity')
        
        if not cart_item_id or quantity is None:
            return Response(
                {'detail': 'cart_item_id and quantity are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart__user=request.user)
            
            if quantity <= 0:
                cart = cart_item.cart
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
                cart = cart_item.cart
            
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response(
                {'detail': 'Cart item not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def clear_cart(self, request):
        """Clear entire cart"""
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response(
                {'detail': 'Cart not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
