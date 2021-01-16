from django.db import models
from django.conf import settings 
from Accounts.models import Address
from Products.models import Product
from django.db.models.signals import post_save
# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered = models.BooleanField(default=False)
    address = models.TextField(default="")
    total = models.IntegerField(default=0)
    online_payment = models.BooleanField(default=False) #0 - COD, 1 - Online Pay
    paid = models.BooleanField(default=False)
class OrderItem(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    order = models.ForeignKey(Order, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    initial_price = models.IntegerField()
    discount = models.IntegerField(default=0)
    final_price = models.IntegerField()
    quantity = models.IntegerField(default=1)
    refund_requested = models.BooleanField(default=False)

class Payment(models.Model): #Payment is done for whole orders, even if the whole order has only 1 item
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL)
    amount = models.IntegerField()
    amt_paid = models.IntegerField()    #For offline transactions
    change = models.IntegerField()      #For offline transactions
    created_at = models.DateTimeField(auto_now_add=True)

class RefundRequest(models.Model): #Refund is given for individual items
    order_item = models.ForeignKey(OrderItem, null=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField(default=1)
    amount = models.IntegerField()
    granted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


def save_order_item(instance, created, **kwargs):
    if created:
        order = instance.order
        print(order)
        order.total += instance.final_price * instance.quantity
        order.save()
def save_payment(instance, created, **kwargs):
    if created:
        o = instance.order
        o.paid = True
        o.save()
def save_refund(instance, created, **kwargs):
    if created:
        oi = instance.order_item
        oi.refund_requested = True
        oi.save()
post_save.connect(save_order_item, sender=OrderItem)
post_save.connect(save_payment, sender=Payment)
post_save.connect(save_refund, sender=RefundRequest)