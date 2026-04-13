
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, UserProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=10, min_length=10 , required=True)
    aadhaar_number = forms.CharField(max_length=12,min_length=12, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'title', 'description', 'brand', 'model', 
            'condition', 'price_per_day', 'security_deposit', 
            'max_lending_days', 'image1', 'image2', 'image3'
        ]
        
    def clean_category(self):
        category = self.cleaned_data.get('category')
        if category not in ['camera', 'laptop']:
            raise forms.ValidationError('Only cameras and laptops are allowed!')
        return category
    
    def clean_max_lending_days(self):
        days = self.cleaned_data.get('max_lending_days')
        if days > 7:
            raise forms.ValidationError('Maximum lending period is 7 days!')
        return days