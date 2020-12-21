# Generated by Django 3.0.4 on 2020-12-21 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Payments', '0002_auto_20201221_1808'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='payment_method',
        ),
        migrations.AddField(
            model_name='order',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]