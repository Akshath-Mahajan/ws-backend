from rest_framework import serializers
from ..models import Cart, CartAndProduct, WishlistAndProduct, Wishlist, Address
# from Products.API.serializers import ProductSerializer
from django.conf import settings
from django.contrib import auth
from rest_framework.authtoken.models import Token
from ..models import User
from Products.API.serializers import ProductSerializer
class UserSerializer(serializers.ModelSerializer):
    numOfItemsInCart = serializers.SerializerMethodField()
    def get_numOfItemsInCart(self, obj):
        return CartAndProduct.objects.filter(cart__user=obj).count()  
    numOfItemsInWishlist = serializers.SerializerMethodField()
    def get_numOfItemsInWishlist(self, obj):
        return WishlistAndProduct.objects.filter(wishlist__user=obj).count()
    token = serializers.SerializerMethodField()
    def get_token(self, obj):
        return Token.objects.get(user=obj).key
    class Meta:
        model = User
        fields = ['id', 'token', 'email', 'full_name', 'numOfItemsInCart', 'numOfItemsInWishlist', 'mobile_no']

class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(read_only = True, many=True)
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'products'] 
class WishlistAndProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    in_cart = serializers.SerializerMethodField()
    def get_in_cart(self, obj):
        return CartAndProduct.objects.filter(product=obj.product, cart__user=obj.wishlist.user).exists()  
    class Meta:
        model = WishlistAndProduct
        fields = ['id', 'wishlist', 'product', 'in_cart']

class CartAndProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = CartAndProduct
        fields = ['id', 'cart', 'product', 'quantity']

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'password', 'full_name', 'email', 'mobile_no']
    def save_user(self, validated_data):
        user = User.objects.create_user( 
                                password=validated_data.get('password'), 
                                full_name=validated_data.get('full_name'),  
                                email=validated_data.get('email'),
                                mobile_no = validated_data.get('mobile_no'))
        user.save()

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address 
        fields = ['id', 'name', 'pincode', 'locality', 'details', 'city', 'landmark', 'address_type']