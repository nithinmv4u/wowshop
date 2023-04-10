import django_filters
from .models import Order

class OrderFilter(django_filters.FilterSet):
    order_number = django_filters.CharFilter(lookup_expr='icontains')
    customer = django_filters.CharFilter(field_name='customer__username', lookup_expr='icontains')
    payment_status = django_filters.ChoiceFilter(choices=Order.PAYMENT_STATUS_CHOICES)
    date_ordered = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Order
        fields = ['order_number', 'customer', 'payment_status', 'date_ordered']
        order_by = ['date_ordered']  # descending order by date_ordered