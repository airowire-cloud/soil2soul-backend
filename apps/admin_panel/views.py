from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg
from django.contrib.auth.models import User
from django.utils import timezone
from apps.products.models import Product
from apps.orders.models import Order
from apps.reviews.models import Review
from .serializers import DashboardStatsSerializer, SalesReportSerializer

class AdminPermission(permissions.BasePermission):
    """Custom permission for admin users"""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class AdminPanelViewSet(viewsets.ViewSet):
    permission_classes = [AdminPermission]
    
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
                Order.objects.order_by('-created_at').values_list('order_number', flat=True)[:10]
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
        from django.utils import timezone
        
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
