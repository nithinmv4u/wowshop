# Generated by Django 4.1.7 on 2024-03-29 08:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cart_order', '0004_alter_order_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_status',
            field=models.CharField(choices=[('completed', 'Completed'), ('failed', 'Failed'), ('pending', 'Pending')], max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='used_coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='cart_order.usedcoupon'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='cart_order.order'),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='shipping_address', to='cart_order.order'),
        ),
    ]