from django.contrib import admin
from .models import Category, Collection, Product, ProductSet, Review, ProductAndCollection, ProductAndProductSet, ProductImage
# Register your models here.
admin.site.register(Category)
admin.site.register(Collection)
admin.site.register(ProductAndCollection)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductSet)
admin.site.register(Review)