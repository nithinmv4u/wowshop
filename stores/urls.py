from django.urls import path
from .views import (ProductView,ProductCreate, ProductUpdate,ProductStockView, ProductList, ProductDelete, CategoryCreate,
                    CategoryUpdate, CategoryView,CategoryList, CategoryDelete, ProductDetail, ProductDisable,
                    ProductSearch,CategoryDisable, CategorySearch, ProductOverview, AddToWishlistView, WishlistView)
from django.conf.urls.static import static
from django.conf import settings
from .import views

app_name = 'stores'

urlpatterns = [
    path('product/', ProductView.as_view(), name='product'),
    path('product_list/', ProductList.as_view(), name='product_list'),
    path('product/create/', ProductCreate.as_view(), name='product_create'),
    path('product/<int:pk>/update/', ProductUpdate.as_view(), name='product_update'),
    path('product/<int:pk>/stock/', ProductStockView.as_view(), name='product-stock'),
    path('product/<int:pk>/delete/', ProductDelete.as_view(), name='product_delete'),
    path('product/<int:pk>/disable/', ProductDisable.as_view(), name='product_disable'),
    path('search-products/', ProductSearch.as_view(), name='product_search'),
    path('product_detail/<int:pk>/', ProductDetail.as_view(), name='product_detail'),

    path('category', CategoryView.as_view(), name='category'),
    path('categories/', CategoryList.as_view(), name='category_list'),
    path('category/create/', CategoryCreate.as_view(), name='category_create'),
    path('category/<int:pk>/update/', CategoryUpdate.as_view(), name='category_update'),
    path('category/<int:pk>/delete/', CategoryDelete.as_view(), name='category_delete'),
    path('category/<int:pk>/disable/', CategoryDisable.as_view(), name='category_disable'),
    path('search-categories/', CategorySearch.as_view(), name='category_search'),

    #users
    path('product_overview/', ProductOverview.as_view(), name='product_overview'),
    path('wishlist', WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/', AddToWishlistView.as_view(), name='wishlist_add')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
