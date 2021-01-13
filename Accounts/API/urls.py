from django.urls import path
from .views import SignupView, CartView, ResetPassword, WishlistView, LoginView, AddressCRUD, UpdateUser, ContactUsCRUD
urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('login/', LoginView.as_view()),
    path('cart/', CartView.as_view()),
    path('wishlist/', WishlistView.as_view()),
    path('address/', AddressCRUD.as_view()),
    path('edit-user/', UpdateUser.as_view()),
    path('password/', ResetPassword.as_view()),
    path('contact-us/', ContactUsCRUD.as_view())
]

