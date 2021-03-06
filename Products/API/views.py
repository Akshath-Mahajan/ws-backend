from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer, ProductImageSerializer
from ..models import Category, Product, Review, Collection, ProductImage
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
        auth = request.headers.get('Authorization', None)
        serializer = ProductSerializer(product)
        reviews = Review.objects.filter(product=product)
        pImages = ProductImage.objects.filter(product=product)
        pImageSerializer = ProductImageSerializer(pImages, many=True)
        if auth:
            reviews = reviews.exclude(user=request.user)
        reviews = reviews[:4]
        r_ser = ReviewSerializer(reviews, many=True)
        userReviewSerializer = None
        resp = {'product': serializer.data, 'images': pImageSerializer.data,'reviews': r_ser.data, 'user_review': userReviewSerializer, 'in_cart': False, 'in_wishlist': False}
        if auth:
            user_review = Review.objects.filter(product=product, user=request.user).first()
            userReviewSerializer = ReviewSerializer(user_review)
            in_cart = CartAndProduct.objects.filter(cart__user=request.user, product=product).exists()
            in_wishlist = WishlistAndProduct.objects.filter(wishlist__user = request.user, product=product).exists()
            resp = {'product': serializer.data, 'images': pImageSerializer.data, 'reviews': r_ser.data, 'user_review': userReviewSerializer.data, 'in_cart': in_cart, 'in_wishlist': in_wishlist}
        
        return Response(resp, status=status.HTTP_200_OK)

class ProductQuery(APIView):
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        products = Product.objects.filter(name__icontains = request.GET['query'])
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

class Home(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        new_products = Product.objects.all().order_by('-created')[:12]
        trending_products = Product.objects.all().order_by('-avg_rating')[:12]
        collection = Collection.objects.filter(is_featured = True)
        if collection.exists():
            collection = collection[0]
        collection_products = collection.products.all()[:12]
        new_serializer = ProductSerializer(new_products, many=True)
        trending_serializer = ProductSerializer(trending_products, many=True)
        collection_serializer = ProductSerializer(collection_products, many=True)
        return Response({'trending':trending_serializer.data, 'new': new_serializer.data, 'collection': collection_serializer.data}, status=status.HTTP_200_OK)
class NewProducts(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        products = Product.objects.all().order_by('-created')[:50]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)