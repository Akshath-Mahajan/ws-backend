from django.urls import path
from .views import (CategoryListView, 
ProductDetail, 
ProductQuery, ProductCategory,
ReviewCRUD,
FeaturedCollectionName, FeaturedCollectionProducts, NewProducts,
TrendingProducts)
urlpatterns = [
    path('products/', ProductQuery.as_view()),    #Request has text named 'query'
    path('products/<int:pk>', ProductDetail.as_view()),
    path('products/category/<int:pk>', ProductCategory.as_view()),
    path('products/collection/', FeaturedCollectionProducts.as_view()),
    path('products/new/', NewProducts.as_view()),
    path('reviews/<int:pk>', ReviewCRUD.as_view()),
    path('collection-name/', FeaturedCollectionName.as_view()),         #Base EP .
    path('trending-products/', TrendingProducts.as_view()),             #Base EP .
    path('category-list/', CategoryListView.as_view()), #Base EP .
    #Add Num of items in cart/wishlist to base ep
]

