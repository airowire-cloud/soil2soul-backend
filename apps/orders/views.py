from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.text import slugify
import uuid
from .models import Order, OrderItem, OrderTracking
from .serializers import OrderSerializer, OrderTrackingSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')
    
    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        order.order_number = self.generate_order_number(order.id)
        order.save()
        
        # Create tracking record
        OrderTracking.objects.create(order=order)
        
        # Send confirmation email
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
