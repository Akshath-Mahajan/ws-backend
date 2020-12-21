from django.db import models
from django.conf import settings 
from Accounts.models import Address
from Products.models import Product
# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered = models.BooleanField(default=False)
    address = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
    total = models.IntegerField()

class OrderItem(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=256)
    initial_price = models.IntegerField()
    discount = models.IntegerField(default=0)
    final_price = models.IntegerField()

class Payment(models.Model): #Payment is done for whole orders, even if the whole order has only 1 item
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL)
    amount = models.IntegerField()
    payment_method = models.BooleanField(default=False) #0 - COD, 1 - Online Pay
    amt_paid = models.IntegerField()    #For offline transactions
    change = models.IntegerField()      #For offline transactions
    created_at = models.DateTimeField(auto_now_add=True)

class Refund(models.Model): #Refund is given for individual items
    order_item = models.ForeignKey(OrderItem, null=True, on_delete=models.SET_NULL)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)