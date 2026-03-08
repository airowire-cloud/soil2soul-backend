from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, WishlistViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'', ProductViewSet, basename='product')
router.register(r'wishlists', WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),
]
