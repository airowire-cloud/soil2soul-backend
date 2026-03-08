from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Notification, EmailTemplate, EmailLog
from .serializers import NotificationSerializer, EmailTemplateSerializer, EmailLogSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read"""
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True, read_at=timezone.now())
        
        return Response({'detail': f'{notifications.count()} notifications marked as read.'})
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent notifications"""
        seven_days_ago = timezone.now() - timedelta(days=7)
        notifications = Notification.objects.filter(
            user=request.user,
            created_at__gte=seven_days_ago
        ).order_by('-created_at')
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def clear_old(self, request):
        """Delete notifications older than 30 days"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        deleted_count, _ = Notification.objects.filter(
            user=request.user,
            created_at__lt=thirty_days_ago
        ).delete()
        
        return Response({'detail': f'{deleted_count} old notifications deleted.'})


class EmailTemplateViewSet(viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAdminUser]


class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def recent_failures(self, request):
        """Get recent failed emails"""
        logs = EmailLog.objects.filter(status='failed').order_by('-created_at')[:20]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
