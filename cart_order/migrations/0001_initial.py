# Generated by Django 4.1.7 on 2023-04-01 05:19

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stores', '0002_remove_product_price_remove_product_product_image_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount', models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100)])),
                ('valid_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('valid_to', models.DateTimeField()),
                ('active', models.BooleanField(default=True)),
                ('is_single_use', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=20, unique=True)),
                ('grand_total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('date_ordered', models.DateTimeField(auto_now_add=True)),
                ('payment_status', models.CharField(choices=[('completed', 'Completed'), ('pending', 'Pending'), ('failed', 'Failed')], max_length=20)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UsedCoupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cart_order.coupon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'coupon')},
            },
        ),
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('h_name', models.CharField(max_length=100)),
                ('email', models.EmailField(default='', max_length=254)),
                ('street_address', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('zip_code', models.CharField(max_length=10)),
                ('phone', models.CharField(default='', max_length=20)),
                ('order_note', models.TextField(blank=True, null=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='cart_order.order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('total_price', models.PositiveIntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cart_order.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stores.product')),
                ('size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stores.productsize')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='used_coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cart_order.usedcoupon'),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stores.product')),
                ('size', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='stores.productsize')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_checked_out', models.BooleanField(default=False)),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('grand_total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cart_order.coupon')),
                ('items', models.ManyToManyField(to='cart_order.cartitem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
