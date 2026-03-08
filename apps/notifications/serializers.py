from rest_framework import serializers
from .models import Notification, EmailTemplate, EmailLog

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message', 'notification_type',
            'related_object_id', 'is_read', 'created_at', 'read_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'read_at']


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ['id', 'name', 'subject', 'body', 'variables', 'is_active', 'created_at', 'updated_at']


class EmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = ['id', 'recipient', 'subject', 'template', 'status', 'error_message', 'sent_at', 'created_at']
        read_only_fields = ['id', 'created_at', 'sent_at']
