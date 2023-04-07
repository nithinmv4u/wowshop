from django.contrib import admin
from django.urls import path
from .import views
from .views import ProductSearch,ProductDetail,ProfileView

app_name = 'authentication'

urlpatterns = [
    path('',views.home,name='home'),
    path('signup',views.signup,name='signup'),
    path('verify-email/<int:user_id>/', views.verify_email, name='verify_email'),
    path('login',views.login_view,name='login'),
    # path('home',views.home,name='home'),
    path('logout',views.logout_view,name='logout'),
    path('product_search', ProductSearch.as_view(), name='product_search'),
    # path('product_filter', ProductListUser.as_view(), name='product_filter'),
    path('product/<int:pk>/', ProductDetail.as_view(), name='product_quick_view'),
    path('about',views.about_view,name='about'),
    path('user_profile/<int:pk>/', ProfileView.as_view(), name='user_profile'),
]