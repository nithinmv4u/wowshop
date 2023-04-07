from django import forms
from .models import  UserProfile
from django.core import validators
from authentication.models import User
from authentication.forms import SignUp



class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100,widget=forms.TextInput(attrs={'class':"form-control form-control-lg", 'placeholder':"Username"}))
    password = forms.CharField(max_length=100,widget=forms.PasswordInput(attrs={'class':"form-control form-control-lg", 'placeholder':"Password"}))

class UserUpdateForm(SignUp):
    password1 = forms.CharField(widget=forms.HiddenInput(), required=False)
    password2 = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',)

class UserAddForm(SignUp):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password1', 'password2', 'email_verified')

# class StudentRegistration(forms.ModelForm):
#     username = forms.EmailField(max_length=240, required=True, help_text='', label='Email:')
#     email_verified = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)
#     # password = forms.CharField(widget=forms.PasswordInput(attrs={ 'placeholder' : 'Enter Password','class' : 'form-control col-3'}))
#     class Meta:
#         model = UserProfile
#         fields = [ 'first_name', 'last_name','username',]
#         widgets = {
#             'first_name' : forms.TextInput(attrs={'class' : 'form-control col-3'}),
#             'last_name' : forms.TextInput(attrs={'class' : 'form-control col-3'}),
#             'username' : forms.TextInput(attrs={'class' : 'form-control col-3'}),
#             # 'password' : forms.PasswordInput(render_value=True ,attrs={'class':'form-control col-3'}),
#             # 'Confirm_password' : forms.PasswordInput(render_value=True ,attrs={'class':'form-control col-3'})
#         }