from django.db import models
from django.conf import settings
from Products.models import Product
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_staffuser(self, email, password):
        user = self.create_user(email, password=password)
        user.staff = True
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user
class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True, default="")
    full_name = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    confirmed_email = models.BooleanField(default=False)
    
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] #Default required is USERNAME_FIELD and password
    
    def get_full_name(self):
        return self.full_name
    def get_short_name(self):
        return self.full_name
    def __str__(self):
        return self.email
    def has_perm(self, perm, obj=None):
        return True
    def has_module_perms(self, app_label):
        return True
    @property
    def is_staff(self):
        return self.staff
    @property
    def is_admin(self):
        return self.admin
    @property
    def is_active(self):
        return self.active
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # amount = models.IntegerField(default=0)
    products = models.ManyToManyField(Product, through="CartAndProduct")
    def __str__(self):
        return self.user.email+"'s cart"
class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="WishlistAndProduct")
    def __str__(self):
        return self.user.email+"'s wishlist"
class CartAndProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    def __str__(self):
        return self.cart.user.email+":"+self.product.name
class WishlistAndProduct(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    def __str__(self):
        return self.wishlist.user.email+":"+self.product.name

'''
    Connect user creation with creation of cart and wishlist.
'''
def save_user(instance, created, **kwargs):
    if created:
        Cart(user=instance).save()
        Wishlist(user=instance).save()
        Token.objects.create(user=instance)

post_save.connect(save_user, sender=settings.AUTH_USER_MODEL)