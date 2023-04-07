from django.shortcuts import render,redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView,DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from .models import Category, Product,ProductImage, ProductSize, WishlistItem
from .forms import CategoryForm, ProductForm, ProductImageFormSet, ProductSizeFormSet
from django.db.models import Q, F
from django_filters.views import FilterView
from .filters import ProductFilter
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.core import serializers
import json
from django.forms import inlineformset_factory
from django.db import transaction
from django.core.files.images import ImageFile


# Create your views here.
from django.http import JsonResponse
from django.views.generic import ListView

from django.http import JsonResponse
from django.views.generic import ListView

from django.http import JsonResponse
from django.views.generic import ListView
from PIL import Image
import io
from django.core.files.base import ContentFile
from django.contrib.auth.mixins import LoginRequiredMixin

class CategoryView(TemplateView):
    template_name = 'category_list.html'

class CategoryList(ListView):
    model = Category
    context_object_name = 'object_list'
    paginate_by = 5
    ordering = ['id']
    
    def render_to_response(self, context, **kwargs):
        data = {
            'categories': list(context['object_list'].values('id', 'category', 'parent', 'is_enabled',)),
            'num_pages': context['page_obj'].paginator.num_pages
        }
        return JsonResponse(data)

class CategoryDetail(DetailView):
    model = Category
    template_name = 'category_detail.html'

class CategoryCreate(CreateView):
    model = Category
    form_class= CategoryForm
    template_name = 'category_form.html'
    # fields = ['category', 'parent']
    # success_url = reverse_lazy('stores:category_list')

    def form_valid(self, form):
        print("form valid")
        # response = super().form_valid(form) -- error since default form_valid should have a success url
        self.object = form.save()
        data = {
            'success': True,
            'message': 'Category '+ self.object.category +' created successfully!',
            # 'category_name': self.object.category
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {
            'success': False,
            'message': 'An error occurred while creating the category.',
        }
        return JsonResponse(data)

class CategoryUpdate(UpdateView):
    model = Category
    form_class= CategoryForm
    template_name = 'category_form.html'
    # success_url = reverse_lazy('stores:category')
    # fields = ['category', 'parent_id']

    def form_valid(self, form):
        print("form valid")
        # response = super().form_valid(form) -- error since default form_valid should have a success url
        self.object = form.save()
        data = {
            'success': True,
            'message': 'Category '+ self.object.category +' updated successfully!',
            # 'category_name': self.object.category
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {
            'success': False,
            'message': 'An error occurred while updating the category.',
        }
        return JsonResponse(data)

class CategoryDelete(DeleteView):
    model = Category
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('stores:category_list')

class CategoryDisable(ListView):
    context_object_name = 'object_list'
    paginate_by = 5
    
    def get(self, request, pk):
        category = Category.objects.get(pk=pk)
        category.toggle_enabled()
        print(pk,"at toggle")
        message = 'Category "' +category.category+ '" disabled successfully!' if not category.is_enabled else 'Category "' +category.category+ '" enabled successfully!'
        data = {'status': 'success', 'message': message}
        
        return JsonResponse(data)
        # return redirect(reverse_lazy('stores:category'))
    
    #event listener for disable not working
    # def render_to_response(self, context, **kwargs):
    #     data = {
    #         'categories': list(context['object_list'].values('id', 'category', 'parent', 'is_enabled',))
    #     }
    #     return JsonResponse(data)

class CategorySearch(ListView):
    model =Category
    context_object_name = 'categories'
    paginate_by = 5
    # data = None

    #since we don't need template name, we need render to response to return JSON response directly from get_queryset    
    def render_to_response(self, context, **response_kwargs):
        print("render: ")
        data = {
                'categories': self.get_queryset(),
                'num_pages': self.paginator.num_pages,
            }
        return JsonResponse(data, safe=False)

    def get_queryset(self):
        query = self.request.GET.get('search')
        print("query: ",query)
        if query:
            search_term = query.split()[0]  # extract search term from query string
            print(search_term)
            categories_search = Category.objects.filter(category__icontains=search_term, is_enabled=True)
            categories = list(categories_search.values('id', 'category', 'parent', 'is_enabled'))
            #we need paginatior instance to be passed to render to response
            self.paginator = Paginator(categories, self.paginate_by)
            print(categories)
            return categories
        else:
            return Category.objects.none()
        
class ProductView(FilterView):
    template_name = 'product_list.html'
    filterset_class = ProductFilter

class ProductList(FilterView):
    model = Product
    context_object_name = 'object_list'
    filterset_class = ProductFilter
    paginate_by = 10  # set the number of products to display per page

    def render_to_response(self, context, **kwargs):
        products = context['object_list'].annotate(category_name=F('category__category')).values('id','product', 'category_name', 'make','is_enabled')
        data = {
            'products': list(products),
            'num_pages': context['page_obj'].paginator.num_pages
        }
        return JsonResponse(data)
    
class ProductOverview(FilterView):
    model = Product
    context_object_name = 'products'
    filterset_class = ProductFilter
    paginate_by = 8
    template_name = 'product_overview.html'

class ProductDetail(DetailView):
    model = Product
    template_name = 'product_detail.html'

class ProductCreate(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    # success_url = reverse_lazy('stores:product_list')

    def form_valid(self, form):
        print("form valid")
        # response = super().form_valid(form) -- error since default form_valid should have a success url
        self.object = form.save()
        data = {
            'success': True,
            'message': 'Product '+ self.object.product +' created successfully!',
            # 'category_name': self.object.category
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        print(form.errors)
        data = {
            'success': False,
            'message': 'An error occurred while creating the product.',
        }
        return JsonResponse(data)
    
class ProductUpdate(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('stores:product')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['form'] = ProductForm(self.request.POST, instance=self.object)
            data['form'].sizes = ProductSizeFormSet(self.request.POST, instance=self.object)
            data['form'].images = ProductImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['form'] = ProductForm(instance=self.object)
            data['form'].sizes = ProductSizeFormSet(instance=self.object)
            data['form'].images = ProductImageFormSet(instance=self.object)
        return data
    
    def form_valid(self, form):
        print("form valid")
        # response = super().form_valid(form) -- error since default form_valid should have a success url
        # get the crop coordinates from the form
        x = form.cleaned_data.get('x')
        y = form.cleaned_data.get('y')
        width = form.cleaned_data.get('width')
        height = form.cleaned_data.get('height')

        # open the uploaded image file
        image = Image.open(io.BytesIO(self.request.FILES['image'].read()))

        # crop the image
        cropped_image = image.crop((x, y, x+width, y+height))

        # save the cropped image to a temporary file
        with io.BytesIO() as output:
            cropped_image.save(output, format='JPEG')
            output.seek(0)
            self.object.image.save('temp.jpg', ContentFile(output.read()), save=False)
        self.object = form.save()
        data = {
            'success': True,
            'message': 'Product '+ self.object.product +' updated successfully!',
            # 'category_name': self.object.category
        }
        return JsonResponse(data)

    def form_invalid(self, form):
        data = {
            'success': False,
            'message': 'An error occurred while updating the product.',
        }
        return JsonResponse(data)


class ProductStockView(UpdateView):
    model = Product
    fields = ['stock']
    success_url = reverse_lazy('stores:product_list') # replace with your desired success url

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.save() # save the updated object
        return response

class ProductDelete(DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('stores:product_list')

class ProductDisable(ListView):
    model = Product
    context_object_name = 'object_list'

    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        product.toggle_enabled()
        print(pk,"at toggle")
        message = 'Product "' +product.product+ '" disabled successfully!' if not product.is_enabled else 'Product "' +product.product+ '" enabled successfully!'
        data = {'status': 'success', 'message': message}
        return JsonResponse(data)
    
class ProductSearch(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    paginate_by=10

    def render_to_response(self, context, **response_kwargs):
        print("render: ")
        data = {
                'products': self.get_queryset(),
                'num_pages': self.paginator.num_pages,
            }
        return JsonResponse(data, safe=False)

    def get_queryset(self):
        query = self.request.GET.get('search')
        print(query)
        if query:
            search_term = query.split()[0]
            print(search_term)
            if search_term:
                queryset= Product.objects.filter(
                    Q(product__icontains=search_term) |
                    Q(category__category__icontains=search_term)
                ).distinct()
                print(queryset)
                products=list(queryset.annotate(category_name=F('category__category')).values('product', 'category_name', 'make'))
                self.paginator = Paginator(products, self.paginate_by)
                print(products)
                return products
            else:
                return Product.objects.none()
            
class AddToWishlistView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        wishlist, created = WishlistItem.objects.get_or_create(user=request.user)
        if product in wishlist.products.all():
            wishlist.products.remove(product)
            message = f"{product.product} removed from your wishlist."
            info = "Removed"
        else:
            wishlist.products.add(product)
            message = f"{product.product} added to your wishlist!"
            info = "Added"
        response_data = {
            'message': message,
            'info' : info,
            }
        return JsonResponse(response_data)

class WishlistView(LoginRequiredMixin, ListView):
    model = WishlistItem
    template_name = 'wishlist.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        wishlist = WishlistItem.objects.filter(user=self.request.user)

        return {
            'wishlist' : wishlist,
        }