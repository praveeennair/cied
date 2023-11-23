from rest_framework import serializers
from core.models import (
    DeliveryAgent,
    Customer,
    Order,
)
from django.db.models import Sum

class DeliveryAgentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username') 

    class Meta:
        model = DeliveryAgent
        fields = ['id', 'name', 'email', 'phone_number', 'is_blocked', 'is_active', 'username']

class CustomerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username') 

    class Meta:
        model = Customer
        fields =  ['id', 'name', 'email',  'username']


class BlockCustomerSerializer(serializers.ModelSerializer):
    class Meta:
            model = Customer
            fields =  ['is_blocked', ]


class OrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Order
        fields = ('id', 'total_amount', 'status', 'products')


class CustomerListSerializer(serializers.ModelSerializer):
    orders = serializers.SerializerMethodField()
    total_gross_amount = serializers.SerializerMethodField()

    def get_orders(self, obj):
        orders = Order.objects.filter(customer_id=obj.id)
        return OrderSerializer(orders, many=True).data

    def get_total_gross_amount(self, obj):
        total_amount = Order.objects.filter(customer_id=obj.id).aggregate(total=Sum('total_amount')).get('total')
        return total_amount if total_amount else 0

    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'orders', 'total_gross_amount']


class UpdateDeliveryStatusSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)