# Generated by Django 3.0.4 on 2020-12-01 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0003_address_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='mobile_no',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
