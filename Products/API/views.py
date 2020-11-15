from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer
from ..models import Category, Product, Review, Collection
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

class ProductQuery(APIView):
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        products = Product.objects.filter(name__icontains = request.GET['query'])
        if products.exists():
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Error':['No such products found']}, status=status.HTTP_400_BAD_REQUEST)

class ProductCategory(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk, format=None):
        products = Product.objects.filter(category__id = pk)
        if products.exists():
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'Error':['No such products found']}, status=status.HTTP_400_BAD_REQUEST)

class ReviewCRUD(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request, pk): #Pk is product id
        reviews = Review.objects.filter(product__id = pk)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request, pk): #Pk is product id
        product = Product.objects.filter(pk=pk)
        if product.exists():
            product = product[0]
            review = Review.objects.filter(user=request.user, product=product)
            if review.exists():
                review = review[0]
                review.comment = request.data['comment']
                review.rating = request.data['rating']
                review.save()
            else:
                review = Review(user=request.user, product=product, comment=request.data['comment'], rating=request.data['rating'])
                review.save()
            serializer = ReviewSerializer(review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'Error':['No such products found']}, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):  #Pk is product id
        review = Review.objects.filter(product__id=pk, user=request.user)
        if review.exists():
            review=review[0]
            review.delete()
            return Response({"Succes":['Delete successful']}, status=status.HTTP_204_NO_CONTENT)
        return Response({"Error":['Product not found']}, status=status.HTTP_204_NO_CONTENT)

class FeaturedCollectionProducts(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        collection = Collection.objects.filter(is_featured = True)
        if collection.exists():
            if len(collection) > 1:
                return Response({'Error':['More than 1 featured collection present']})
            collection = collection[0]
            serializer = ProductSerializer(collection.products.all(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)
class FeaturedCollectionName(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        collection = Collection.objects.filter(is_featured = True)
        if collection.exists():
            if len(collection) > 1:
                return Response({'Error':['More than 1 featured collection present']})
            collection = collection[0]
            return Response({'Name':collection.name}, status=status.HTTP_200_OK)

class TrendingProducts(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        products = Product.objects.all().order_by('-avg_rating')[:30]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
