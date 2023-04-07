from django.urls import path
from .views import (CartView,AddToCartView,UpdateCartItemView,RemoveFromCartView,CheckoutView,
                    OrderCreateView,CouponAdminView, ApplyCouponView, RemoveCouponView,
                    OrderSummaryView, OrderConfirmationView, OrderHistoryView,
                    RazorpayConfirmationView)
# AddToCartView, RemoveFromCartView, UpdateCartItemView, CheckoutView, OrderDetailView

app_name = 'cart_order'

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('add/<int:pk>/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove/<int:pk>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('update/<int:pk>/', UpdateCartItemView.as_view(), name='update_cart_item'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('coupons/', CouponAdminView.as_view(), name='coupon_admin'),
    path('coupons/create/', CouponAdminView.as_view(), name='create_coupon'),
    path('coupons/toggle/', CouponAdminView.as_view(), name='toggle_coupon'),
    path('apply_coupon/', ApplyCouponView.as_view(), name='apply_coupon'),
    path('remove_coupon/', RemoveCouponView.as_view(), name='remove_coupon'),
    path('order_create/', OrderCreateView.as_view(), name='order_create'),
    path('order_summary/<int:order_id>/', OrderSummaryView.as_view(), name='order_summary'),
    path('order_confirmation/<int:order_id>/', OrderConfirmationView.as_view(), name='order_confirmation'),
    path('razorpay_confirmation/<int:order_id>/', RazorpayConfirmationView.as_view(), name='razorpay_confirmation'),
    path('order_history/', OrderHistoryView.as_view(), name='order_history')
]
