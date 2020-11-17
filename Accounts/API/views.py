from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, WishlistSerializer, CartAndProductSerializer, UserSerializer
from ..models import Cart, Wishlist, CartAndProduct, WishlistAndProduct
from Products.API.serializers import ProductSerializer
from Products.models import Product
from django.contrib.auth import authenticate
class WishlistView(APIView):
    def get(self, request, format=None):
        wishlist = Wishlist.objects.get(user=request.user)
        if wishlist:
            serializer = WishlistSerializer(wishlist)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse({'Wishlist':['Wishlist not found']}, status=status.HTTP_400_BAD_REQUEST)
    def post(self, request,format=None):
        pk = request.data['product_id']
        product, wishlist = Product.objects.filter(pk=pk), request.user.wishlist
        if product.exists():
            product = product[0]
            if not WishlistAndProduct.objects.filter(wishlist=wishlist, product=product).exists():
                rel = WishlistAndProduct(wishlist=wishlist, product=product)
                rel.save()
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Error':['No such products found']}, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, format=None):
        pk = request.data['product_id']
        product, wishlist  = Product.objects.filter(pk=pk), request.user.wishlist
        if product.exists():
            product = product[0]
            rel = WishlistAndProduct.objects.filter(wishlist=wishlist, product=product)
            if rel.exists():
                rel = rel[0]
                rel.delete()
                return Response({"Succes":['Delete successful']}, status=status.HTTP_204_NO_CONTENT)
        return Response({"Error":['Product not found']}, status=status.HTTP_204_NO_CONTENT)
class CartView(APIView):
    def get(self, request, format=None):
        cart = Cart.objects.get(user=request.user)
        if cart:
            cart_products = CartAndProduct.objects.filter(cart=cart)
            serializer = CartAndProductSerializer(cart_products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Cart':['Cart not found']}, status=status.HTTP_400_BAD_REQUEST)
    def post(self, request, format=None):
        if request.data['quantity'] <= 0:
            return Response({'Error':["You can't do that"]}, status=status.HTTP_400_BAD_REQUEST)
        pk = request.data['product_id']
        product, cart  = Product.objects.filter(pk=pk), request.user.cart
        if product.exists():
            product=product[0]
            rel = CartAndProduct.objects.filter(cart=cart, product=product)
            if rel.exists():
                rel = rel[0]
                rel.quantity = request.data['quantity']
                rel.save()
            else:
                rel = CartAndProduct(cart=cart, product=product, quantity=request.data['quantity'])
                rel.save()
            serializer = CartAndProductSerializer(rel)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Error':['No such products found']}, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, format=None):
        pk = request.data['product_id']
        product, cart  = Product.objects.filter(pk=pk), request.user.cart
        if product.exists():
            product = product[0]
            rel = CartAndProduct.objects.filter(cart=cart, product=product)
            if rel.exists():
                rel = rel[0]
                rel_id = rel.id
                rel.delete()
                return Response({"id":rel_id}, status=status.HTTP_202_ACCEPTED)
        return Response({"Error":['Product not found']}, status=status.HTTP_204_NO_CONTENT)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        user = authenticate(username=request.data['email'], password=request.data['password'])
        if user is not None:
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"Error":["Invalid Credentials"]}, status=status.HTTP_400_BAD_REQUEST)

class SignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save_user(serializer.data)
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)