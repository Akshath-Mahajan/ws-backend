from rest_framework import serializers
from ..models import Cart, CartAndProduct, WishlistAndProduct, Wishlist
# from Products.API.serializers import ProductSerializer
from django.conf import settings
from django.contrib import auth
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['user', 'products'] 
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['user', 'products'] 

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']
    def save_user(self, validated_data):
        user = User.objects.create_user(username=validated_data.get('username'), 
                                password=validated_data.get('password'), 
                                first_name=validated_data.get('first_name'), 
                                last_name=validated_data.get('last_name'), 
                                email=validated_data.get('email'))
        user.save()