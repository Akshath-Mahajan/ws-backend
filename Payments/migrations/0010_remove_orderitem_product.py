# Generated by Django 3.0.4 on 2021-01-16 16:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Payments', '0009_auto_20210116_1513'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='product',
        ),
    ]
