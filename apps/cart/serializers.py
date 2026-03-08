from rest_framework import serializers
from apps.products.serializers import ProductSerializer
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_detail', 'quantity', 'price', 'total_price', 'added_at']
        read_only_fields = ['id', 'price', 'added_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'total_items', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
