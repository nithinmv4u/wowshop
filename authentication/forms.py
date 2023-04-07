from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserChangeForm
from .models import User, Address, PhoneNumber

class Login(forms.Form):
    email = forms.EmailField(label='Email:', max_length=240, required=True, widget=forms.TextInput(attrs={'class': 'stext-111 cl2 plh3 size-116 p-l-62 p-r-30 m-b-20', 'placeholder': 'Your Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder': 'Your Password'}), label='Password:', required=True)

class SignUp(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder': 'Last Name'}))
    username = forms.EmailField(label='Email:', max_length=240, required=True, widget=forms.TextInput(attrs={'class': 'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder': 'Your Email Address'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder': 'Your Password'}), label='Password:', required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'stext-111 cl2 plh3 size-116 p-l-62 p-r-30', 'placeholder': 'Confirm Password'}), label='Confirm Password:', required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password1', 'password2', 'email_verified')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class AddressForm(forms.ModelForm):
    default = forms.BooleanField(label='Set as default address', required=False)
    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'h_name', 'street_address', 'city', 'state', 'zip_code','phone', 'default']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'h_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter house name'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter street address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter state'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter zip code'}),
            'phone':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
        }
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'h_name': 'House Name',
            'street_address': 'Street Address',
            'city': 'City',
            'state': 'State',
            'zip_code': 'Zip Code',
            'phone':'Phone Number',
        }

AddressFormSet = inlineformset_factory(User, Address, form=AddressForm, extra=4,max_num=4, can_delete=True)

class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        fields = ['phone_number', 'default']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
        }
        labels = {
            'phone_number': 'Phone Number',
        }

PhoneNumberFormSet = inlineformset_factory(User, PhoneNumber, form=PhoneNumberForm, extra=2,max_num=2, can_delete=True)




# class ProfileForm(UserChangeForm):
#     class Meta(UserChangeForm.Meta):
#         model = User
#         fields = ['first_name', 'last_name']

# AddressFormSet = inlineformset_factory(
#     User, Address, fields=('h_name', 'street_address', 'city', 'state', 'zip_code'),
#     extra=4, can_delete=True
# )

# PhoneNumberFormSet = inlineformset_factory(
#     User, PhoneNumber, fields=('phone_number',), extra=2, can_delete=True
# )


# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User


# class Login(forms.Form):
#     email=forms.EmailField(label='Email:',max_length=240,required=True,)
#     password = forms.CharField(widget=forms.PasswordInput,label='Password:',required=True)

# class SignUp(UserCreationForm):
#     username = forms.EmailField(max_length=240, required=True, help_text='',label='Email:')
#     email_verified = forms.BooleanField(initial=False, widget=forms.HiddenInput(),required=False)

#     class Meta:
#         model = User
#         fields = ('first_name', 'last_name', 'username', 'password1', 'password2', 'email_verified')

# class SignUp(UserCreationForm):
#     username = forms.EmailField(max_length=240, required=True, help_text='',label='Email:',)
#     # last_name = forms.CharField(max_length=30, required=True, help_text='Required.')

#     class Meta:
#         model = User
#         fields = ('first_name', 'last_name','username', 'password1', 'password2', )
#         # labels = {
#         #     'first_name': '',
#         #     'last_name': '',
#         #     'username' : '',
#         #     'password1': '',
#         #     'password2': '',
#         # }