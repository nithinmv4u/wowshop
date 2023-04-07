from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from authentication.models import User

# Create your models here.

class Category(models.Model):
    category = models.CharField(max_length=255,)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    is_enabled = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.category
    
    def toggle_enabled(self):
        self.is_enabled = not self.is_enabled
        self.save()



class Product(models.Model):

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
    ]

    MAKE_CHOICES = [
        ('BATA', 'Bata'),
        ('ADIDAS', 'Adidas'),
        ('PUMA', 'Puma'),
        ('REEBOK', 'Reebok'),
        ('NIKE', 'Nike'),
        ('WOODLAND', 'Woodland'),
        ('RED_CHIEF', 'Red Chief'),
        ('LEE_COOPER', 'Lee Cooper'),
        ('FILA', 'Fila'),
        ('SKECHERS', 'Skechers'),
        ('CONVERSE', 'Converse'),
        ('CLARKS', 'Clarks'),
        ('CROCS', 'Crocs'),
        ('HUSH_PUPPIES', 'Hush Puppies'),
        ('LIBERTY', 'Liberty'),
        ('SPARX', 'Sparx'),
        ('ACTION', 'Action'),
        ('LANCER', 'Lancer'),
        ('LOTTO', 'Lotto'),
        ('MOCHI', 'Mochi'),
    ]

    product = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    make = models.CharField(max_length=255, choices=MAKE_CHOICES)
    description = models.TextField(default='', blank=True)
    is_enabled = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default='MALE')

    def __str__(self):
        return self.product
    
    def toggle_enabled(self):
        self.is_enabled = not self.is_enabled
        self.save()
    
    def get_total_stock(self):
        total_stock = sum([size.stock for size in self.sizes.all()])
        return total_stock
    
    def get_price_range(self):
        sizes = self.sizes.all()
        if sizes:
            min_price = min(size.price for size in sizes)
            max_price = max(size.price for size in sizes)
            return f"₹ {min_price} - ₹ {max_price}"
        return "No price information available"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products', null=True, blank=True)

class ProductSize(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=255, choices=SIZE_CHOICES)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product} - {self.size}"
    
    def delete(self, *args, **kwargs):
        self.stock = 0
        self.price = 0
        self.save(update_fields=['stock', 'price'])

    class Meta:
        unique_together = ('product', 'size')

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    added_at = models.DateTimeField(auto_now_add=True)

    