from rest_framework import serializers
from apps.users.serializers import AddressSerializer
from .models import Order, OrderItem, OrderTracking

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price_per_unit', 'total_price']


class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTracking
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tracking = OrderTrackingSerializer(read_only=True)
    shipping_address_detail = AddressSerializer(source='shipping_address', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'shipping_address', 'shipping_address_detail',
            'subtotal', 'shipping_cost', 'tax', 'discount', 'total_amount',
            'status', 'items', 'tracking', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'user', 'created_at', 'updated_at']


class OrderDetailSerializer(OrderSerializer):
    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields
