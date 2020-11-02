from django.db import models
from django.conf import settings
# Create your models here.
class Bill(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField()
    is_paid = models.BooleanField()
    date_created = models.DateTimeField()
    date_paid = models.DateTimeField(null=True, blank=True)
    payment_method = models.PositiveSmallIntegerField()
    #products