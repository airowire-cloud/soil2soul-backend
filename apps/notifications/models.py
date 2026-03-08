from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPES = [
        ('order', 'Order Update'),
        ('product', 'Product Available'),
        ('price', 'Price Drop'),
        ('review', 'New Review Response'),
        ('promotion', 'Promotion Offer'),
        ('system', 'System Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)  # 'order', 'product', etc.
    
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"


class EmailTemplate(models.Model):
    """Email notification templates"""
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    variables = models.TextField(blank=True)  # Comma-separated list of variables
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
        db_table = 'email_templates'
    
    def __str__(self):
        return self.name


class EmailLog(models.Model):
    """Log of sent emails"""
    recipient = models.EmailField()
    subject = models.CharField(max_length=200)
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=[('sent', 'Sent'), ('failed', 'Failed'), ('pending', 'Pending')],
        default='pending'
    )
    error_message = models.TextField(blank=True)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        db_table = 'email_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Email to {self.recipient} - {self.status}"
