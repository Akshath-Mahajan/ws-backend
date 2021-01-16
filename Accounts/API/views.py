from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, WishlistSerializer, CartAndProductSerializer, UserSerializer, AddressSerializer, WishlistAndProductSerializer
from ..models import User, Cart, Wishlist, CartAndProduct, WishlistAndProduct, Address, ContactUs
from Products.API.serializers import ProductSerializer
from Products.models import Product
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
class WishlistView(APIView):
    def get(self, request, format=None):
        wishlist = Wishlist.objects.get(user=request.user)
        if wishlist:
            wishlist_products = WishlistAndProduct.objects.filter(wishlist=wishlist)
            serializer = WishlistAndProductSerializer(wishlist_products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Wishlist':['Wishlist not found']}, status=status.HTTP_400_BAD_REQUEST)
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
                rel_id = rel.id
                rel.delete()
                return Response({"id":rel_id}, status=status.HTTP_202_ACCEPTED)
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
        return Response({"token": None}, status=status.HTTP_200_OK)

class SignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():   #Takes care of validation using params on model.
            user = serializer.save_user(serializer.data)
            token = Token.objects.get(user=user)
            send_mail("Webshop: Confirm Email", "Please confirm your email by clicking the link below\n"+settings.FRONT_END_HOST+"/verify-user/user-id="+str(token.key), settings.EMAIL_HOST_USER, [user.email])
            return JsonResponse({'status': 'created'}, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateUser(APIView):
    def post(self, request):
        # Need to validate
        u = request.user
        full_name = request.data.get('full_name', request.user.full_name)
        email = request.data.get('email', request.user.email)
        mobile = request.data.get('mobile', request.user.mobile_no)
        u.full_name = full_name
        u.mobile_no = mobile
        if u.email != email:
            u.active = False
        u.email = email
        u.save()
        u_ser = UserSerializer(u)
        return Response(u_ser.data, status.HTTP_200_OK)
class ResetPassword(APIView):
    def post(self, request):
        old_pw = request.data.get('old_pw')
        new_pw1 = request.data.get('new_pw1')
        new_pw2 = request.data.get('new_pw2')
        if request.user.check_password(old_pw) and new_pw1 == new_pw2:
            request.user.set_password(new_pw1)
            request.user.save()
            return Response({'status':True, 'message': 'Changed password'}, status.HTTP_200_OK)
        return Response({'status': False, 'message': 'Could not password'}, status.HTTP_400_BAD_REQUEST)
class AddressCRUD(APIView):
    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        A_serializer = AddressSerializer(addresses, many=True)
        return Response(A_serializer.data, status.HTTP_200_OK)
    def post(self, request):
        address_id = request.data.get('id', False)
        if address_id:
            a = Address.objects.get(id=address_id, user=request.user) #Edit existing
            a.name = request.data.get('name', a.name)
            a.pincode = request.data.get('pincode', a.pincode)
            a.locality=request.data.get('locality', a.locality)
            a.details=request.data.get('details', a.details)
            a.city=request.data.get('city', a.city)
            a.landmark=request.data.get('landmark', a.landmark)
            a.address_type=request.data.get('address_type', a.address_type)
        else:
            #Create new
            a = Address(
                user=request.user,
                name=request.data.get('name', ''),
                pincode=request.data.get('pincode'),
                locality=request.data.get('locality', ''),
                details=request.data.get('details'),
                city=request.data.get('city'),
                landmark=request.data.get('landmark', ''),
                address_type=request.data.get('address_type', False)
            )
        a.save()
        A_serializer = AddressSerializer(a)
        return Response(A_serializer.data, status.HTTP_200_OK)
    def delete(self, request):
        pk = request.data['pk']
        a = Address.objects.filter(pk=pk, user=request.user)
        a.delete()
        return Response({'status': 'deleted'}, status.HTTP_200_OK)

class ContactUsCRUD(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        ContactUs(
            email = request.data['email'],
            first_name = request.data['first_name'],
            last_name = request.data['last_name'],
            text = request.data['text']
        ).save()
        return Response({'Created': True}, status.HTTP_200_OK)

class VerifyEmail(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        tok = Token.objects.filter(key=request.data['confirmation-id'])
        if tok.exists():
            tok = tok.first()
            user = tok.user
            user.active = True
            user.save()
            tok.delete()
            Token.objects.create(user=user)
        else:
            return Response({'verified':False}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'verified':True}, status=status.HTTP_200_OK)
