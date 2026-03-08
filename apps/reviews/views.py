from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Review, ReviewImage
from .serializers import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return Review.objects.filter(product_id=product_id)
        return Review.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """Mark review as helpful"""
        review = self.get_object()
        review.helpful_count += 1
        review.save()
        
        serializer = self.get_serializer(review)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_unhelpful(self, request, pk=None):
        """Mark review as unhelpful"""
        review = self.get_object()
        review.unhelpful_count += 1
        review.save()
        
        serializer = self.get_serializer(review)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Get current user's reviews"""
        reviews = Review.objects.filter(user=request.user)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def product_reviews(self, request):
        """Get reviews for a product"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'detail': 'product_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reviews = Review.objects.filter(product_id=product_id).order_by('-helpful_count')
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
