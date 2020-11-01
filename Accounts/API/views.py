from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, CartSerializer, WishlistSerializer
from ..models import Cart, Wishlist

class WishlistView(APIView):
    def get(self, request, format=None):
        wishlist = Wishlist.objects.get(user=request.user)
        if wishlist:
            serializer = WishlistSerializer(wishlist)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse({'Wishlist':['Wishlist not found']}, status=status.HTTP_400_BAD_REQUEST)
class CartView(APIView):
    def get(self, request, format=None):
        cart = Cart.objects.get(user=request.user)
        if cart:
            serializer = CartSerializer(cart)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse({'Cart':['Cart not found']}, status=status.HTTP_400_BAD_REQUEST)
class SignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save_user(serializer.data)
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)