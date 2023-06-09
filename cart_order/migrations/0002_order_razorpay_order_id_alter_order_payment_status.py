# Generated by Django 4.1.7 on 2023-04-02 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart_order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='razorpay_order_id',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_status',
            field=models.CharField(choices=[('failed', 'Failed'), ('pending', 'Pending'), ('completed', 'Completed')], max_length=20),
        ),
    ]
