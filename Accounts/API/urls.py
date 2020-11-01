from django.urls import path
from .views import SignupView, CartView, WishlistView
from rest_framework.authtoken import views
urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('login/', views.obtain_auth_token),
    path('cart/', CartView.as_view()),
    path('wishlist/', WishlistView.as_view()),
]

