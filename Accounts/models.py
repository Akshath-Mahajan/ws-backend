from django.db import models
from django.conf import settings
from Products.models import Product
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # amount = models.IntegerField(default=0)
    products = models.ManyToManyField(Product, through="CartAndProduct")
    def __str__(self):
        return self.user.username+"'s cart"
class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="WishlistAndProduct")
    def __str__(self):
        return self.user.username+"'s wishlist"
class CartAndProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
class WishlistAndProduct(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

'''
    Connect user creation with creation of cart and wishlist.
'''
def save_user(instance, created, **kwargs):
    if created:
        Cart(user=instance).save()
        Wishlist(user=instance).save()
        Token.objects.create(user=instance)

post_save.connect(save_user, sender=settings.AUTH_USER_MODEL)