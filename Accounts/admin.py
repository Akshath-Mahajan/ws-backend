from django.contrib import admin
from .models import Cart, Wishlist, CartAndProduct, WishlistAndProduct

# Register your models here.
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(CartAndProduct)
admin.site.register(WishlistAndProduct)