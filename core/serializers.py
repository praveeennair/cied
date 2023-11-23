from rest_framework import serializers
from core.models import (
    Product,
    Order,
)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'products', 'total_amount', 'status')
        read_only_fields = ('total_amount', 'status')
