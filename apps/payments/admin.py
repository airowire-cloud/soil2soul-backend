from django.contrib import admin
from .models import Payment, Refund

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'payment_method', 'status', 'created_at']
    search_fields = ['order__order_number', 'transaction_id', 'user__username']
    list_filter = ['status', 'payment_method', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['payment', 'amount', 'status', 'created_at']
    search_fields = ['payment__order__order_number', 'user__username']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
