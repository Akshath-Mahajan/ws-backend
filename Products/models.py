from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 
from django.conf import settings
# Create your models here.
class Collection(models.Model):
    name = models.CharField()
    description = models.TextField()
    is_featured = models.BooleanField()
    date_created = models.DateTimeField()

class Category(models.Model):
    name = models.CharField()
    num_of_products = models.IntegerField()

class _Set(models.Model):
    name = models.CharField()
    is_featured = models.BooleanField()
    special_price = models.IntegerField()

class Product(models.Model):
    name = models.CharField()
    image = models.ImageField()
    description = models.TextField()
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    avg_rating = models.IntegerField(default=0)
    price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    _set = models.ForeignKey(_Set, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.SmallIntegerField()
    comment = models.TextField()