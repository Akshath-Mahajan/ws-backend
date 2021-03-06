from django.db import models
from django.conf import settings
from Products.models import Product
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MinLengthValidator
SIZE_CHOICES = (
    ('XS', 'Extra Small'),
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large'),
    ('XL', 'Extra Large'),
)
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), **kwargs)
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
    mobile_no = models.CharField(max_length=10, validators=[MinLengthValidator(10)], blank=True, null=True)
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

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, blank=True, null=True)
    pincode = models.CharField(max_length=6, blank=False, null=False)
    locality = models.CharField(max_length=64, blank=False, null=False)
    details = models.TextField(blank=False, null=False)
    city = models.CharField(max_length=64, blank=False, null=False)
    landmark = models.CharField(max_length=128, blank=True, null=True)
    address_type = models.BooleanField(default=None, null=True, blank=True) #0 - Home, 1 - work
    def __str__(self):
        return str(self.id)+self.user.email+"'s address"

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
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, default='M')
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

class ContactUs(models.Model):
    email = models.EmailField(max_length=255)
    first_name = models.CharField(max_length=127)
    last_name = models.CharField(max_length=127)
    text = models.TextField()