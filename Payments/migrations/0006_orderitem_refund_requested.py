# Generated by Django 3.0.4 on 2021-01-12 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Payments', '0005_refundrequest_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='refund_requested',
            field=models.BooleanField(default=False),
        ),
    ]
