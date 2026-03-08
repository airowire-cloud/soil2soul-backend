from rest_framework import serializers

class DashboardStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_orders = serializers.IntegerField()
    top_products = serializers.ListField()
    recent_orders = serializers.ListField()


class SalesReportSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    order_count = serializers.IntegerField()
    average_order_value = serializers.DecimalField(max_digits=12, decimal_places=2)
