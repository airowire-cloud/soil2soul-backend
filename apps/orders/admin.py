from django.contrib import admin
from .models import Order, OrderItem, OrderTracking

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'created_at']
    search_fields = ['order_number', 'user__username']
    list_filter = ['status', 'created_at']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'created_at', 'updated_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'order', 'quantity', 'price_per_unit', 'total_price']
    search_fields = ['product_name', 'order__order_number']


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'tracking_number', 'carrier', 'estimated_delivery']
    search_fields = ['order__order_number', 'tracking_number']
    list_filter = ['status', 'carrier']
