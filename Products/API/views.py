from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer
from ..models import Category, Product, Review
from rest_framework.response import Response
from Accounts.models import Cart, CartAndProduct, Wishlist, WishlistAndProduct
from django.contrib.auth.models import User

class CategoryListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        cats = Category.objects.all()
        if cats.exists():
            serializer = CategorySerializer(cats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Error':['No categories found']}, status=status.HTTP_400_BAD_REQUEST)

class ProductDetail(APIView):
    permission_classes = [AllowAny]
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404
    def get(self, request, pk, format=None):
        product = self.get_object(pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductListQuery(APIView):
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        products = Product.objects.filter(name__icontains = request.GET['query'])
        if products.exists():
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Error':['No such products found']}, status=status.HTTP_400_BAD_REQUEST)

class ProductListCategory(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk, format=None):
        products = Product.objects.filter(category__id = pk)
        if products.exists():
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Error':['No such products found']}, status=status.HTTP_400_BAD_REQUEST)

class AddToCart(APIView):
    def post(self, request, pk, format=None):
        product, cart  = Product.objects.get(pk=pk), request.user.cart
        if request.data['quantity'] <= 0:
            return Response({'Error':["You can't do that"]}, status=status.HTTP_400_BAD_REQUEST)
        if product:
            if CartAndProduct.objects.filter(cart=cart, product=product).exists():
                rel = CartAndProduct.objects.get(cart=cart, product=product)
                rel.quantity = request.data['quantity']
                rel.save()
            else:
                rel = CartAndProduct(cart=cart, product=product, quantity=request.data['quantity'])
                rel.save()
            serializer = ProductSerializer(product)
            data = serializer.data
            data['quantity'] = request.data['quantity']
            return Response(data, status=status.HTTP_200_OK)
        return Response({'Error':['No such products found']}, status=status.HTTP_400_BAD_REQUEST)

class AddToWishlist(APIView):
    def post(self, request, pk, format=None):
        product, wishlist  = Product.objects.get(pk=pk), request.user.wishlist
        if product:
            if not WishlistAndProduct.objects.filter(wishlist=wishlist, product=product).exists():
                rel = WishlistAndProduct(wishlist=wishlist, product=product)
                rel.save()
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Error':['No such products found']}, status=status.HTTP_400_BAD_REQUEST)

class DeleteFromCart(APIView):
    def delete(self, request, pk, format=None):
        product, cart  = Product.objects.get(pk=pk), request.user.cart
        if product:
            rel = CartAndProduct.objects.get(cart=cart, product=product)
            if rel:
                rel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DeleteFromWishlist(APIView):
    def delete(self, request, pk, format=None):
        product, wishlist  = Product.objects.get(pk=pk), request.user.wishlist
        if product:
            rel = WishlistAndProduct.objects.get(wishlist=wishlist, product=product)
            if rel:
                rel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReviewList(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        reviews = Review.objects.filter(product__id = pk)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateReview(APIView):
    def post(self, request, pk):
        product = Product.objects.get(pk=pk)
        if product:
            if Review.objects.filter(user=request.user, product=product).exists():
                return Response({'Error':['Did you mean to edit your review?']}, status=status.HTTP_400_BAD_REQUEST)
            else:
                r = Review(user=request.user, product=product, comment=request.data['comment'], rating=request.data['rating'])
                r.save()
                serializer = ReviewSerializer(r)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'Error':['No such products found']}, status=status.HTTP_400_BAD_REQUEST)
class UpdateReview(APIView):
    def put(self, request, pk):
        review = Review.objects.filter(pk=pk, user=request.user)
        if review.exists():
            review = review[0]
            review.comment = request.data['comment']
            review.rating = request.data['rating']
            review.save()
            serializer = ReviewSerializer(review)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response({'Error':['No such review found']}, status=status.HTTP_400_BAD_REQUEST)
class DeleteReview(APIView):
    def delete(self, request, pk):
        review = Review.objects.filter(pk=pk, user=request.user)
        if review.exists():
            review=review[0]
            review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
