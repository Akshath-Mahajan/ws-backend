from django.contrib import admin
from .models import Order, OrderItem, Payment, RefundRequest
# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(RefundRequest)
