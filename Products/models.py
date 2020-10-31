from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 
from django.conf import settings
# Create your models here.
class Collection(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    is_featured = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name+":"+self.description

class Category(models.Model):
    name = models.CharField(max_length=256)
    num_of_products = models.IntegerField(default=0)
    def __str__(self):
        return self.name
class ProductSet(models.Model):
    name = models.CharField(max_length=256)
    is_featured = models.BooleanField(default=False)
    special_price = models.IntegerField()
    def __str__(self):
        return self.name
class Product(models.Model):
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='Products/ProductImages')
    description = models.TextField(null=True, blank=True)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    avg_rating = models.IntegerField(default=0)
    price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    product_set = models.ForeignKey(ProductSet, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    def __str__(self):
        return self.name
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.user.username+":"+self.rating+":"+self.comment