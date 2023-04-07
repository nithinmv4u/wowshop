from django.contrib import admin
from django.urls import path
from .import views


app_name = 'custom_admin'

urlpatterns = [
    path('',views.login_view,name='admin_login'),
    path('admin_home/',views.home,name='admin_home'),
    path("users", views.users, name="users"),
    path('<int:id>/<str:first_name>/', views.update_data, name="updatedata"),
    path('delete/<int:id>/', views.delete_data, name="deletedata"),
    path('disable/<int:id>/', views.disable_data, name="disabledata"),
    path('search', views.search_username, name="searchusername"),
    path('user_add', views.user_add, name="user_add"),
    path('logout',views.logout_view,name='logout'),
]