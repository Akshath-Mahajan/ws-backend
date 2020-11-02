from django.urls import path
from .views import (CategoryListView, 
ProductDetail, 
ProductListQuery, ProductListCategory,
AddToCart, AddToWishlist, 
DeleteFromCart, DeleteFromWishlist,
ReviewList, CreateReview, UpdateReview, DeleteReview)
urlpatterns = [
    path('category-list/', CategoryListView.as_view()),
    path('product-detail/<int:pk>', ProductDetail.as_view()),
    path('product-list-query/', ProductListQuery.as_view()),    #Request has text named 'query'
    path('product-list-category/<int:pk>', ProductListCategory.as_view()),
    path('add-to-cart/<int:pk>', AddToCart.as_view()),
    path('add-to-wishlist/<int:pk>', AddToWishlist.as_view()),
    path('delete-from-cart/<int:pk>', DeleteFromCart.as_view()),
    path('delete-from-wishlist/<int:pk>', DeleteFromWishlist.as_view()),
    path('get-review-list/<int:pk>', ReviewList.as_view()),
    path('create-review/<int:pk>', CreateReview.as_view()),    
    path('update-review/<int:pk>', UpdateReview.as_view()),
    path('delete-review/<int:pk>', DeleteReview.as_view()), 
]

