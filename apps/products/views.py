from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, ProductImage, Wishlist
from .serializers import (
    CategorySerializer, ProductSerializer, ProductDetailSerializer,
    ProductImageSerializer, WishlistSerializer
)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(status='active')
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['name', 'description', 'short_description']
    ordering_fields = ['price', 'created_at', 'average_rating']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        featured_products = Product.objects.filter(status='active')[:10]
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_to_wishlist(self, request, pk=None):
        """Add product to user's wishlist"""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        product = self.get_object()
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist.products.add(product)
        
        return Response({'detail': 'Added to wishlist.'})
    
    @action(detail=True, methods=['post'])
    def remove_from_wishlist(self, request, pk=None):
        """Remove product from user's wishlist"""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        product = self.get_object()
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist.products.remove(product)
            return Response({'detail': 'Removed from wishlist.'})
        except Wishlist.DoesNotExist:
            return Response(
                {'detail': 'Wishlist not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_wishlist(self, request):
        """Get current user's wishlist"""
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(wishlist)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_product(self, request):
        """Add product to wishlist"""
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response(
                {'detail': 'product_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
            wishlist.products.add(product)
            serializer = self.get_serializer(wishlist)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
