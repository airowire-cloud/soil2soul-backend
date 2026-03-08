from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminPanelViewSet

router = DefaultRouter()
router.register(r'', AdminPanelViewSet, basename='admin')

urlpatterns = [
    path('', include(router.urls)),
]
