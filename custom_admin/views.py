
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
# from authentication.forms import SignUp
from django.http import HttpResponse
from authentication.views import home
from .models import UserProfile
from .forms import UserUpdateForm, LoginForm, UserAddForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings



# Create your views here.
@never_cache
def login_view(request):
    print('at login')
    if request.session.get('logged_in', False):
        print("login",request.session.get('logged_in', False))
        return redirect('custom_admin:admin_home')
    else:
        form = LoginForm()
        if request.method == 'POST':
            print('post')
            form = LoginForm(request.POST)
            if form.is_valid():
                print('is valid')
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    response = redirect('custom_admin:admin_home')
                    response.set_cookie('admin_home', 'admin_home')
                    print('after cookie')
                    request.session['logged_in'] = True
                    return response
                else:
                    print('credential')
                    return render(request,'admin_login.html',{'form': form, 'messages':'Invalid Credentials..! / User disabled'})
            else:
                print("form invalid")
                return render(request, 'admin_login.html', {'form': form})
        else:
            form = LoginForm()
        return render(request, 'admin_login.html', {'form': form})

@never_cache
@user_passes_test(lambda u: u.is_superuser,login_url='custom_admin:admin_login')
@login_required(login_url='signin')
def home(request):
    # if request.session.get('logged_in', False):
    #     print("home ",request.session.get('logged_in', False))
    #     return redirect('custom_admin:admin_login')
    print("home ",request.session.get('logged_in', False))
    return render(request, 'admin_home.html')

@never_cache
@user_passes_test(lambda u: u.is_superuser,login_url=home)
@login_required(login_url='signin')
def users(request):
    print('admin users')
    User = get_user_model()
    users = User.objects.exclude(is_superuser=True).order_by('-date_joined')
    # Render the user list as a string
    # user_list = render_to_string('user_list.html', {'users': users})

    # Return the user list as an AJAX response
    # return HttpResponse(user_list)
    context={
        'users':users,
    }
    return render(request, 'users.html', context)
    

@never_cache
@user_passes_test(lambda u: u.is_superuser,login_url=home)
@login_required(login_url='signin')
def update_data(request, id, first_name):
    user=get_user_model()
    if request.method == 'POST':
        pi = user.objects.get(pk=id)
        
        fm = UserUpdateForm(request.POST, instance=pi)
        # fm = UserUpdateForm(instance=pi, initial={'password1': None, 'password2': None})
        
        if fm.is_valid():
            fm.save()
            messages.info(request, 'Edited Succefully')
        
    else:
        pi = user.objects.get(pk = id)
        fm = UserUpdateForm(instance=pi)
        
    return render(request, 'update_user.html', {'form' : fm})

@never_cache
@user_passes_test(lambda u: u.is_superuser,login_url=home)
@login_required(login_url='signin')
def delete_data(request, id):
    user=get_user_model()
    if request.method == 'POST':
        pi = user.objects.get(pk = id)
        pi.delete()
        messages.info(request, 'Deleted Succefully')
    return redirect('custom_admin:users')

@never_cache
@user_passes_test(lambda u: u.is_superuser,login_url=home)
@login_required(login_url='signin')
def disable_data(request, id):
    user = get_user_model()
    try:
        user_selected = user.objects.get(id=id)
        if user_selected.is_active == True:
            user_selected.is_active = False
            status = "Disabled"
        else:
            user_selected.is_active = True
            status = "Enabled"
        user_selected.save()
        messages.info(request, f'{user_selected.first_name} {user_selected.last_name} has been {status}.')
    except user.DoesNotExist:
        messages.error(request, 'User not found')
    return redirect('custom_admin:users')

@never_cache
@user_passes_test(lambda u: u.is_superuser,login_url=home)
@login_required(login_url='signin')
def search_username(request):
    searched = request.GET['search']
    user = get_user_model()
    searchnames = user.objects.filter(first_name__contains = searched)
    print(searchnames)
    return render(request, 'users.html', {'users' : searchnames})

    
@never_cache
@user_passes_test(lambda u: u.is_superuser,login_url=home)
def user_add(request):
    fmsp = UserAddForm()
    if request.user.is_authenticated:
        user=get_user_model()
    if request.method == 'POST':
        fmsp = UserAddForm(request.POST)
        if fmsp.is_valid():
            ftnm = fmsp.cleaned_data['first_name']
            ltnm = fmsp.cleaned_data['last_name']
            email = fmsp.cleaned_data['username']
            pw = fmsp.cleaned_data['password1']
            pw2 = fmsp.cleaned_data['password2']
            if pw == pw2:
                if user.objects.filter(username=email).exists():
                    messages.info(request, 'email already exists')
                    return redirect('custom_admin:user_add')
                else:
                    registration = user.objects.create_user(
                        username=email, first_name=ftnm, last_name=ltnm, password=pw)
                    registration.save()

                    # send verification email
                    verification_url = request.build_absolute_uri(reverse('authentication:verify_email', kwargs={'user_id': registration.pk}))
                    subject = 'Verify your email'
                    message = render_to_string('verification.html', {'verification_url': verification_url})
                    plain_message = strip_tags(message)
                    from_email = settings.EMAIL_HOST_USER
                    recipient_list = [registration.username]
                    sent = send_mail(subject, plain_message, from_email, recipient_list, html_message=message)
                    print(f"Sent {sent} email(s)")

                    messages.info(request, 'Succefully Added your User')
                    return redirect('custom_admin:admin_home')
            else:
                messages.info(request, 'password not match.....!')
                fmsp = UserAddForm()
                return redirect('custom_admin:user_add',)
        else:
            fmsp = UserAddForm()
    return render(request, 'user_add.html', {'form': fmsp})

@never_cache
def logout_view(request):
    response = redirect('custom_admin:admin_login')
    response.delete_cookie('admin_home')
    # if request.session.get('logged_in', False):
    #     del request.session['logged_in']
    #     request.session.flush() # this line will delete the session
    logout(request)
    print("logout ",request.session.get('logged_in', False))
    return response

    