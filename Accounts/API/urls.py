from django.urls import path
from .views import SignupView, CartView, WishlistView, LoginView
urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('login/', LoginView.as_view()),
    path('cart/', CartView.as_view()),
    path('wishlist/', WishlistView.as_view()),
]

