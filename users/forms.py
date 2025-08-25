from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, Profile, ProductImage

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']
    
class ProductForm(forms.ModelForm):
    # ፎቶዎችን ለመቀበል አዲስ መስክ እንጨምራ
    class Meta:
        model = Product
        # 'image' የሚለውን ከዝርዝሩ እናውጣዋለን
        fields = ['name', 'description', 'price', 'category', 'brand', 'condition', 'location']
        
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'phone_number']