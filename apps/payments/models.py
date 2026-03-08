from django.db import models
from django.contrib.auth.models import User
from apps.orders.models import Order

class Payment(models.Model):
    """Payment records"""
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
        ('wallet', 'Wallet'),
        ('cod', 'Cash on Delivery'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='credit_card')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        db_table = 'payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment for {self.order.order_number}"


class Refund(models.Model):
    """Refund requests"""
    REFUND_STATUS = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='refund')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refunds')
    
    reason = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=REFUND_STATUS, default='requested')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        db_table = 'refunds'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund for {self.payment.order.order_number}"
