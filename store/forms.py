import json
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    specifications_text = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':5}), label='Specifications (JSON)')
    class Meta:
        model = Product
        fields = ['name','category','subcategory','brand','sku','price','cost','description','image','inventory','lifecycle']
        widgets = {'description': forms.Textarea(attrs={'rows':5})}
    def clean_specifications_text(self):
        value = self.cleaned_data.get('specifications_text','').strip() or '{}'
        try: return json.loads(value)
        except json.JSONDecodeError: raise forms.ValidationError('Enter valid JSON, for example {"ram":"8 GB"}.')
    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.specifications = self.cleaned_data.get('specifications_text', {})
        if commit: obj.save()
        return obj
