from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, EmailTemplateViewSet, EmailLogViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'email-templates', EmailTemplateViewSet, basename='email-template')
router.register(r'email-logs', EmailLogViewSet, basename='email-log')

urlpatterns = [
    path('', include(router.urls)),
]
