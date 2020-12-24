from django.urls import path
from .views import SignupView, CartView, WishlistView, LoginView, AddressCRUD, UserManagment
urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('login/', LoginView.as_view()),
    path('cart/', CartView.as_view()),
    path('wishlist/', WishlistView.as_view()),
    path('address/', AddressCRUD.as_view()),
    path('edit-user/', UserManagment.as_view())
]

