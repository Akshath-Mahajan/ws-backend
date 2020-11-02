from django.urls import path
from .views import (CategoryListView, 
ProductDetail, 
ProductListQuery, ProductListCategory,
ReviewCRUD,
FeaturedCollectionName, FeaturedCollectionProducts,
TrendingProducts)
urlpatterns = [
    path('category-list/', CategoryListView.as_view()),
    path('product-detail/<int:pk>', ProductDetail.as_view()),
    path('product-list-query/', ProductListQuery.as_view()),    #Request has text named 'query'
    path('product-list-category/<int:pk>', ProductListCategory.as_view()),
    path('reviews/<int:pk>', ReviewCRUD.as_view()),
    path('collection-products/', FeaturedCollectionProducts.as_view()), 
    path('collection-name/', FeaturedCollectionName.as_view()), 
    path('trending-products/', TrendingProducts.as_view()), 
]

