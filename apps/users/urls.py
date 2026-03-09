from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, UserProfileViewSet, AddressViewSet, UserActivityViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'activities', UserActivityViewSet, basename='activity')

urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
