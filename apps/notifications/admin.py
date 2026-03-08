from django.contrib import admin
from .models import Notification, EmailTemplate, EmailLog

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    list_filter = ['notification_type', 'is_read', 'created_at']
    readonly_fields = ['created_at', 'read_at']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    search_fields = ['name', 'subject']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'subject', 'status', 'sent_at', 'created_at']
    search_fields = ['recipient', 'subject']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'sent_at']
