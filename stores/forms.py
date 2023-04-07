from django import forms
from .models import Category, Product, ProductImage, ProductSize
from django.forms import inlineformset_factory, formset_factory, modelformset_factory
from django.forms.widgets import TextInput, Select


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category', 'parent',]
        exclude = ['is_enabled', 'created_date', 'modified_date']
        widgets = {
            'category': forms.TextInput(attrs={'class': 'form-control w-100'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }

class ReadOnlyTextInput(TextInput):
    def __init__(self, *args, **kwargs):
        kwargs['attrs'] = {'readonly': True}
        super().__init__(*args, **kwargs)

class ProductSizeForm(forms.ModelForm):
    class Meta:
        model = ProductSize
        fields = ('size', 'price', 'stock')
        widgets = {
            'size': ReadOnlyTextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['size'] = self.instance.size

ProductSizeFormSet = forms.inlineformset_factory(
    Product,
    ProductSize,
    fields=('size', 'price', 'stock'),
    extra=4, max_num=4,
    can_delete=True,
    form=ProductSizeForm,
)
ProductImageFormSet = forms.inlineformset_factory(
    Product,
    ProductImage,
    fields=('image',),
    extra=3, max_num=3,
    can_delete=True,
    widgets={'image': forms.FileInput(attrs={'class': 'form-control', 'id': 'id_image'})}
)
class ProductForm(forms.ModelForm):
    # x = forms.FloatField(widget=forms.HiddenInput())
    # y = forms.FloatField(widget=forms.HiddenInput())
    # width = forms.FloatField(widget=forms.HiddenInput())
    # height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Product
        fields = ['product', 'category', 'make','gender', 'description',]
        exclude = ['is_enabled', 'created_date', 'modified_date']
        widgets = {
            'product': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'make': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'style': 'height: 10vw'}),
            'is_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    
    sizes = forms.inlineformset_factory(
        Product,
        ProductSize,
        fields=('size', 'price', 'stock'),
        extra=4,
        can_delete=True,
        formset=ProductSizeFormSet,
        # widgets={'size': ProductSizeSelect(attrs={'class': 'form-control'})},
    )
    images = forms.inlineformset_factory(
        Product,
        ProductImage,
        fields=('image',),
        extra=3,
        can_delete=True,
        widgets={'image': forms.FileInput(attrs={'class': 'form-control', 'id': f'id_image{{ forloop.counter0 }}'})}
    )

    def save(self, commit=True):
        # Call the parent class's save method to save the main Product model.
        product = super().save(commit=commit)
        print("saving")
        # Save the ProductSizeFormSet and ProductImageFormSet forms.
        sizes_formset = self.sizes(instance=product, data=self.data)
        images_formset = self.images(instance=product, data=self.data, files=self.files)
        if sizes_formset.is_valid() and images_formset.is_valid():
            sizes_formset.save()
            images_formset.save()
        
        return product
    


# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['product', 'category', 'make', 'description']
    
# class ProductImageForm(forms.ModelForm):
#     class Meta:
#         model = ProductImage
#         fields = ['image']

# class ProductSizeForm(forms.ModelForm):
#     class Meta:
#         model = ProductSize
#         fields = ['size', 'price', 'stock']


