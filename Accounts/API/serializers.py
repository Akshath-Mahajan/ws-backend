from rest_framework import serializers
from ..models import Cart, CartAndProduct, WishlistAndProduct, Wishlist
# from Products.API.serializers import ProductSerializer
from django.conf import settings
from django.contrib import auth
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from Products.API.serializers import ProductSerializer
class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(read_only = True, many=True)
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'products'] 

class CartAndProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = CartAndProduct
        fields = ['id', 'cart', 'product', 'quantity']

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email']
    def save_user(self, validated_data):
        user = User.objects.create_user(username=validated_data.get('username'), 
                                password=validated_data.get('password'), 
                                first_name=validated_data.get('first_name'), 
                                last_name=validated_data.get('last_name'), 
                                email=validated_data.get('email'))
        user.save()