import django_filters
from stores.models import Product

class ProductFilterUser(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = [ 'category', 'make',]