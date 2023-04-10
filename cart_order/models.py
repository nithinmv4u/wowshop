from django.db import models
from authentication.models import User
from stores.models import Product, ProductSize
from django.utils import timezone
from django.core.validators import MaxValueValidator
from decimal import Decimal

# Create your models here.
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE,default=0)

    def total_price(self):
        return self.size.price * self.quantity

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    is_single_use = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        return self.active and self.valid_from <= timezone.now() <= self.valid_to

    def discount_amount(self, total):
        total = Decimal(str(total))
        return (self.discount / Decimal('100')) * total

    @classmethod
    def create(cls, code, discount, valid_from, valid_to, active=True):
        coupon = cls(code=code, discount=discount, valid_from=valid_from, valid_to=valid_to, active=active)
        coupon.save()
        return coupon
    
    def toggle_enabled(self):
        self.active = not self.active
        self.save()
        return self.active
    
    def coupon_used(self):
        self.is_single_use = True
    
class UsedCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'coupon')

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(CartItem)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_checked_out = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    grand_total= models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())
    
    def calculate_tax(self):
        tax_rate = 0.1  # 10% tax rate
        subtotal = self.total_price()
        tax_amount = subtotal * tax_rate
        return round(tax_amount,2)

    def total_after_tax(self):
        total = self.total_price()
        tax_amount = self.calculate_tax()
        sub_total = total + tax_amount
        return sub_total
    
    def calculate_grand_total(self, coupon=None):
        subtotal = self.total_after_tax()
        if coupon:
            discount_amount = coupon.discount_amount(subtotal)
            grand_total = Decimal(subtotal) - discount_amount
        else:
            grand_total = Decimal(subtotal)
        return round(grand_total,2) 

    def add_item(self, product_object, quantity, product_size_object):
        print("product_object.id",product_object.id)
        item, created = CartItem.objects.get_or_create(user=self.user, product=product_object, size=product_size_object)
        print(item.id)
        item.quantity += quantity
        print("item.quantity",item.quantity)
        item.save()
        self.items.add(item)

    def remove_item(self, item):
        self.items.remove(item)

    def clear(self):
        self.items.clear()

PAYMENT_METHOD_CHOICES = (
    ('COD', 'Cash on Delivery'),
    ('RAZORPAY', 'Razorpay Payment'),
)
class Order(models.Model):
    PAYMENT_STATUS_CHOICES = {
        ('pending','Pending'),
        ('completed','Completed'),
        ('failed','Failed'),
    }
    order_number = models.CharField(max_length=20, unique=True)
    grand_total = models.DecimalField(max_digits=20, decimal_places=2, null=False, blank=False)
    date_ordered = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    used_coupon = models.ForeignKey(UsedCoupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    razorpay_order_id = models.CharField(max_length=255, default='')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)

class OrderItem(models.Model):
    quantity = models.IntegerField()
    total_price = models.PositiveIntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')

class ShippingAddress(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    h_name = models.CharField(max_length=100)
    email = models.EmailField(default='')
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=20, default='')
    order_note = models.TextField(blank=True, null=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_address')

class RazorpayPayment(models.Model):
    payment_id = models.CharField(max_length=100)
    order_id = models.CharField(max_length=100)
    signature = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
