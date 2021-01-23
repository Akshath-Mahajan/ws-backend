from rest_framework import serializers
from ..models import Order, OrderItem
from Products.API.serializers import ProductSerializer

class OrderSerializer(serializers.ModelSerializer):
    # products = ProductSerializer(read_only = True, many=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'updated_at', 'delivered', 'address', 'total', 'online_payment', 'paid']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'name', 'initial_price', 'discount', 'final_price', 'quantity', 'size']

# class PaymentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=Payment
#         fields=['id', 'order', 'amount', 'amt_paid', 'change', 'created_at'] 

# class RefundSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=RefundRequest
#         fields=['id', 'quantity', 'granted', 'order_item', 'amount', 'created_at']
