from rest_framework import serializers
from .models import Payment, Refund

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'user', 'amount', 'payment_method',
            'status', 'transaction_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = [
            'id', 'payment', 'user', 'reason', 'amount', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
