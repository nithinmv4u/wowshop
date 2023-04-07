from django import forms

class UpdateCartItemForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)