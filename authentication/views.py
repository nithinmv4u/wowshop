from django.shortcuts import render,redirect,HttpResponseRedirect,get_object_or_404
from django.http import HttpResponse
from .forms import *
from stores.models import *
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.views.decorators.cache import cache_control
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from authentication.models import User
from django.views.generic import ListView,DetailView,UpdateView
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.serializers import serialize
import logging
from django_filters.views import FilterView
from .filters import ProductFilterUser
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin

def about_view(request):
    return render(request,'login_Copy.html',)

# Create your views here.
@cache_control(no_cache=True)
def index(request):
    if request.session.get('logged_in', False):
        print("inside session check")
        return redirect('authentication:home')   
    print("index cus")
    products=Product.objects.all()
    return render(request,'index.html',{'products':products})


@cache_control(no_cache=True)
def signup(request):
    if request.session.get('logged_in', False):
        return redirect('authentication:home')
    else:
        if request.method == 'POST':
            form = SignUp(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                if User.objects.filter(username=form.cleaned_data['username']).exists():
                    form.add_error('username', 'This email has already been already registered.') #custom error is not passed check later
                    return render(request, 'signup.html', {'form': form})
                user.set_password(form.cleaned_data['password1'])
                user.save()

                # send verification email
                verification_url = request.build_absolute_uri(reverse('authentication:verify_email', kwargs={'user_id': user.pk}))
                subject = 'Verify your email'
                message = render_to_string('verification.html', {'verification_url': verification_url})
                plain_message = strip_tags(message)
                from_email = settings.EMAIL_HOST_USER
                print(user.email+' & '+user.username)
                recipient_list = [user.username]
                sent = send_mail(subject, plain_message, from_email, recipient_list, html_message=message)
                print(f"Sent {sent} email(s)")
                # print(user.email_verified)
                return redirect('authentication:login')
        else:
            form = SignUp()

        return render(request, 'signup.html', {'form': form})

@cache_control(no_cache=True)
def verify_email(request, user_id):
    # Get the user object from the database
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        print('verify',User)
    except User.DoesNotExist:
        return render(request, 'verification_failed.html')

    # Verify the user's email and update the email_verified field
    user.email_verified = True
    user.save()

    # Redirect the user to the home page
    return redirect('authentication:login')


@cache_control(no_cache=True)
def login_view(request):
    print("login customer")
    if request.session.get('logged_in', False):
        return redirect('authentication:home')
    else:
        # if 'home' in request.COOKIES:
        #     return redirect('home')
        form= Login()
        if request.method=='POST':
            print('post')
            form=Login(request.POST)
            if form.is_valid():
                print('form valid')
                #check for authentication and redirect to user home page
                email =form.cleaned_data.get('email')
                password=form.cleaned_data.get('password')
                user= authenticate(username=email,password=password)
                print(user)
                if user is not None and user.email_verified:
                    # print(user.is_superuser) # Debugging line to print user's superuser status
                    # print(user.is_active)   # Debugging line to print user's active status
                    login(request,user) # default cookie setting is done
                    # if request.user.is_superuser:
                    #     print(redirect('custom_admin:index'))
                    #     return redirect('custom_admin:admin')
                    # else:
                    print('after login')
                    response = redirect('authentication:home')
                    response.set_cookie('home', 'home')
                    print('after cookie')
                    # response['cache-control'] = 'no-cache, no-store, must-revalidate'
                    request.session['logged_in'] = True
                    print('after session')
                    return response
                elif user is not None and not user.email_verified:
                    messages.error(request, 'Your email is not verified. Please check your email and follow the instructions to verify your email before logging in.')
                    return redirect('authentication:login')
                # return redirect('home')
                else:
                    print('credential')
                    # messages.warning(request,'')
                    return render(request,'login.html',{'form': form, 'messages':'Invalid Credentials..! / User disabled'})
            else:
                print('form not valid')
                return render(request, 'login.html', {'form': form})
        else:
            print('no post done')
            return render(request, 'login.html', {'form': form})

def home(request):
    f = ProductFilterUser(request.GET, queryset=Product.objects.all())
    paginator = Paginator(f.qs, 8)  # Show 8 products per page
    page = request.GET.get('page')  # Get the current page number
    products = paginator.get_page(page)
    return render(request, 'home.html', {'products': products, 'filter': f})



    # -----------ajax didn't work----------
    # def is_ajax(self):
    #     return self.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    # request.is_ajax = is_ajax.__get__(request)

    # if request.is_ajax():
    #     # If the request is an AJAX request, return a JsonResponse containing the filtered products
    #     filtered_products = list(products.object_list.values())
    #     return {'products': products, 'filter': f}

    # # If the request is not an AJAX request, return the filtered products using the home.html template


# class ProfileView(LoginRequiredMixin, UpdateView):
#     model = User
#     template_name = 'user_profile.html'
#     # success_url = reverse_lazy('user_profile')
#     fields = '__all__'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user = self.request.user
#         if self.request.POST:
#             print("post")
#             context['address_formset'] = AddressFormSet(self.request.POST, instance=user)
#             context['phone_number_formset'] = PhoneNumberFormSet(self.request.POST, instance=user)

#         else:
#             context['address_formset'] = AddressFormSet(instance=user)
#             context['phone_number_formset'] = PhoneNumberFormSet(instance=user)

#         # set default address to first position
#         default_address = user.addresses.filter(default=True).first()
#         if default_address:
#             addresses = user.addresses.exclude(pk=default_address.pk).order_by('-default')
#             addresses = [default_address] + list(addresses)
#         else:
#             addresses = user.addresses.order_by('-default')
#             print(addresses)

#         context['addresses'] = addresses
#         context['phone_numbers'] = user.phone_numbers.all()
#         print(context)
#         return context

#     def form_valid(self, form):
#         context = self.get_context_data()
#         address_formset = context['address_formset']
#         phone_number_formset = context['phone_number_formset']

#         # Check if a formset form was submitted
#         if any(form in formset.forms for formset in [address_formset, phone_number_formset] for form in formset.forms):
#             # Save the formset form that was submitted
#             print("if any")
#             if form in address_formset.forms:
#                 instance = form.save(commit=False)
#                 instance.user = self.request.user
#                 instance.save()
#             elif form in phone_number_formset.forms:
#                 instance = form.save(commit=False)
#                 instance.user = self.request.user
#                 instance.save()

#             # Return a success response indicating that the form was saved
#             data = {
#                 'success': True,
#                 'message': 'Form saved successfully!'
#             }
#             return JsonResponse(data)

#         # Save the main form and the formsets if they are valid
#         with transaction.atomic():
#             self.object = form.save()

#             if address_formset.is_valid():
#                 address_formset.instance = self.object
#                 address_formset.save()

#             if phone_number_formset.is_valid():
#                 phone_number_formset.instance = self.object
#                 phone_number_formset.save()

#             # Return a success response indicating that the main form and formsets were saved
#             data = {
#                 'success': True,
#                 'message': 'Addresses & Phone Numbers updated successfully!'
#             }
#             return JsonResponse(data)





    #     if address_formset.is_valid() and phone_number_formset.is_valid():
    #         self.object = form.save()
    #         address_formset.instance = self.object
    #         address_formset.save()
    #         phone_number_formset.instance = self.object
    #         phone_number_formset.save()
    #         address_list_html = render_to_string('address_list.html', {'addresses': self.object.addresses.all()})
    #         return JsonResponse({'success': True, 'message': 'Address saved successfully', 'address_list_html': address_list_html})
    #     else:
    #         print("failed")
    #         return JsonResponse({'success': False, 'message': 'Invalid form data'})

    # def get_object(self, queryset=None):
    #     return get_object_or_404(User, pk=self.request.user.pk)



class ProfileView(UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'user_profile.html'

    def get_context_data(self, **kwargs):
        data = super(ProfileView, self).get_context_data(**kwargs)
        #data['first_name'] = self.request.user.first_name
        #data['last_name'] = self.request.user.last_name
        if self.request.POST:
            data['address_formset'] = AddressFormSet(self.request.POST, instance=self.object)
            data['phone_number_formset'] = PhoneNumberFormSet(self.request.POST, instance=self.object)
        else:
            data['address_formset'] = AddressFormSet(instance=self.object)
            data['phone_number_formset'] = PhoneNumberFormSet(instance=self.object)
        # print(data)
        # set default address to first position
        user = self.request.user
        default_address = user.addresses.filter(default=True).first()
        if default_address:
            addresses = user.addresses.exclude(pk=default_address.pk).order_by('-default')
            addresses = [default_address] + list(addresses)
        else:
            addresses = user.addresses.order_by('-default')
            print(addresses)

        data['addresses'] = addresses
        data['phone_numbers'] = user.phone_numbers.all()
        data['messages'] = ''
        return data

    def form_valid(self, form):
        print("form valid")
        context = self.get_context_data()
        addresses = context['address_formset']
        phone_numbers = context['phone_number_formset']
        # print(addresses)
        # print(phone_numbers)
        with transaction.atomic():
            self.object = form.save()

            if addresses.is_valid():
                print("address valid")
                addresses.instance = self.object
                # addresses.save(commit=False)
                # for address_form in addresses.forms:
                #     if address_form.has_changed():
                #         address = address_form.save(commit=False)
                #         address.user = self.request.user
                #         address.save()
                addresses.save()
            else:
                print(addresses.errors)
                # # Save the addresses first
                # address_instances = addresses.save(commit=False)
                # for address in address_instances:
                #     # If the default checkbox is selected, set it as the default address for the user
                #     if address.default:
                #         # Clear the previous default address for the user
                #         default_address = self.object.get_default_address()
                #         if default_address:
                #             default_address.default = False
                #             default_address.save()
                #         # Set the new default address
                #         address.default

            if phone_numbers.is_valid():
                print("phone valid")
                phone_numbers.instance = self.object
                phone_numbers.save()
            
            messages.success(self.request, 'Addresses & Phone Numbers updated successfully!')

        success_url = reverse_lazy('authentication:user_profile', kwargs={'pk': self.object.pk})    
        return redirect(success_url)
            
        #     data = {
        #         'success': True,
        #         'message': 'Addresses & Phone Numbers updated successfully!',
                
        #     }

        # return JsonResponse(data)
    #     #return super(ProfileView, self).form_valid(form)

# def home(request):
#     f = ProductFilterUser(request.GET, queryset=Product.objects.all())
#     paginator = Paginator(f.qs, 8)  # Show 8 products per page
#     page = request.GET.get('page')  # Get the current page number
#     products = paginator.get_page(page)
#     # return render(request, 'home.html', {'products': products, 'filter': f})

#     def is_ajax(self):
#         return self.headers.get('x-requested-with') == 'XMLHttpRequest'

#     request.is_ajax = is_ajax.__get__(request)

#     if request.is_ajax():
#         return JsonResponse({'products': products})

#     return render(request, 'home.html', {'products': products, 'filter': f})


# def home(request):
#     f = ProductFilterUser(request.GET, queryset=Product.objects.all())
#     paginator = Paginator(f.qs, 8)  # Show 8 products per page
#     page = request.GET.get('page')  # Get the current page number
#     products = paginator.get_page(page)
#     return render(request, 'home.html', {'products': products, 'filter': f})

# class Home(FilterView):
#     model = Product
#     template_name = 'home.html'
#     context_object_name = 'products'
#     filterset_class = ProductFilterUser
#     paginate_by = 10 

class ProductDetail(DetailView):
    model = Product
    template_name = 'product_quick_view.html'

# class ProductListUser(FilterView):
#     model = Product
#     filterset_class = ProductFilterUser
#     paginate_by = 10

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['products'] = self.get_queryset()
#         return context

# def home(request):
#     if request.user.is_authenticated:
#         products=Product.objects.all()
#         return render(request,'home.html',)
#         return render(request,'home.html')
#     else:
#         return redirect('authentication:index')

@cache_control(no_cache=True)
def logout_view(request):
    response = redirect('authentication:home')
    # response.delete_cookie('home')
    #  BELOW 2 LINES ARE TO CLEAR SESSION, BUT ALREDY WE ARE USING DJANGO logout(request) FUNCTION
    # if request.session.get('logged_in', False):
    #     del request.session['logged_in']
    logout(request)
    return response

# class ProductSearch(ListView):
#     model = Product
#     context_object_name = 'products'
#     paginate_by = 10

#     def get(self, request, *args, **kwargs):
#         query = request.GET.get('product-search')
#         if query:
#             queryset = self.get_queryset().filter(
#                 Q(product__icontains=query) |
#                 Q(category__category__icontains=query)
#             ).distinct()
#         else:
#             queryset = self.get_queryset()

#         data = list(queryset.values())
#         return JsonResponse(data, safe=False)

logger = logging.getLogger(__name__)

class ProductSearch(ListView):
    model = Product #not required here
    template_name = 'home.html'
    context_object_name = 'products'
    # paginate_by = 10

    def get_queryset(self):
        print(self.request)
        logger.debug('ProductSearch view called')
        query = self.request.GET.get('product_search')
        logger.debug(f'query={query}')
        print(query)
        if query:
            queryset= Product.objects.filter(
                Q(product__icontains=query) |
                Q(category__category__icontains=query)
            ).distinct()
            print(queryset)
            return queryset
        else:
            pass

