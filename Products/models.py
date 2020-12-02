from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 
from django.conf import settings
from django.db.models.signals import pre_save, post_delete, pre_delete
# Create your models here.
class Collection(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    is_featured = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField('Product', through='ProductAndCollection')
    def __str__(self):
        return self.name+":"+self.description
class Category(models.Model):
    name = models.CharField(max_length=256)
    def __str__(self):
        return self.name
class ProductSet(models.Model):
    name = models.CharField(max_length=256)
    is_featured = models.BooleanField(default=False)
    special_price = models.IntegerField()
    products = models.ManyToManyField('Product', through='ProductAndProductSet')
    def __str__(self):
        return self.name
class Product(models.Model):
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='Products/ProductImages')
    description = models.TextField(null=True, blank=True)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    price = models.IntegerField()
    avg_rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    def __str__(self):
        return "Product("+str(self.product.id)+"):"+str(self.id)+" "+self.user.email+" : "+str(self.rating)+":"+self.comment

class ProductAndCollection(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
class ProductAndProductSet(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_set = models.ForeignKey(ProductSet, on_delete=models.CASCADE)

def review_save(instance, **kwargs):
    product = instance.product
    qs = Review.objects.filter(id=instance.id)
    created = not qs.exists()
    if created:
        current_rating = product.avg_rating
        current_count = Review.objects.filter(product=product).count()
        new_rating = ((current_count*current_rating) + instance.rating)/(current_count+1)
        product.avg_rating = new_rating
        product.save()
    if not created:
        old_review = qs[0]
        count = Review.objects.filter(product=product).count()
        product.avg_rating = ((product.avg_rating * count) - old_review.rating + instance.rating)/count
        product.save()
def review_delete(instance, **kwargs):
    product = instance.product
    count = Review.objects.filter(product=product).count()
    product.avg_rating = ((product.avg_rating*count) - instance.rating)/(count-1)
    product.save()
pre_save.connect(review_save, sender=Review)
pre_delete.connect(review_delete, sender=Review)