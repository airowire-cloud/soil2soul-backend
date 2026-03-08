from rest_framework import serializers
from .models import Category, Product, ProductImage, Wishlist

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'
        read_only_fields = ['created_at']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'name', 'slug', 'description',
            'short_description', 'price', 'mrp', 'discount_percentage',
            'image', 'images', 'stock', 'weight', 'status',
            'average_rating', 'total_reviews', 'in_stock', 'created_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'average_rating', 'total_reviews']


class ProductDetailSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            'meta_title', 'meta_description', 'meta_keywords', 'updated_at'
        ]


class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        many=True,
        source='products'
    )
    
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'products', 'product_ids', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
