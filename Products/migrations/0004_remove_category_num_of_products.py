# Generated by Django 3.0.4 on 2020-10-31 20:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0003_remove_product_avg_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='num_of_products',
        ),
    ]
