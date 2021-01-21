# Generated by Django 3.0.4 on 2021-01-19 05:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Payments', '0013_remove_order_rp_payment_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='rp_order_id',
        ),
        migrations.CreateModel(
            name='RP_Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rp_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Payments.Order')),
            ],
        ),
    ]