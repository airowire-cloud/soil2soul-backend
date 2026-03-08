from rest_framework import serializers
from .models import Review, ReviewImage

class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_name', 'product', 'rating', 'title', 'comment',
            'verified_purchase', 'helpful_count', 'unhelpful_count',
            'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'helpful_count', 'unhelpful_count', 'created_at', 'updated_at']
