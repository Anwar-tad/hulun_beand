# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _ # 1. Import translation function
from .models import Product, Profile

# ================================
# ==== 1. Authentication Forms ====
# ================================

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email Address"), # Translatable Label
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Enter your email')})
    )
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': _('Enter your username')}
        )
        self.fields['username'].label = _("Username")
        self.fields['password1'].label = _("Password")
        self.fields['password2'].label = _("Confirm Password")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')


# ==========================
# ==== 2. Product Form ====
# ==========================
class RetailProductForm(forms.ModelForm):
    # ይህ ፎርም ለችርቻሮ ንግድ የሚያስፈልጉትን መስኮች ብቻ ይይዛል
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'condition', 'brand', 'location', 
            'price', 'description'
        ]

class WholesaleProductForm(forms.ModelForm):
    # ይህ ፎርም ለጅምላ ንግድ የሚያስፈልጉትን ሁሉንም መስኮች ይይዛል
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'condition', 'brand', 'location', 
            'price', 'description', 'is_wholesale', 'minimum_order'
        ]

        
        # 2. Define translatable labels for each field
        labels = {
            'name': _('Product Name'),
            'category': _('Category'),
            'brand': _('Brand'),
            'condition': _('Condition'),
            'location': _('Location'),
            'price': _('Price (in Birr)'),
            'description': _('Description'),
        }
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g., Samsung Galaxy S22')}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g., Samsung')}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g., Addis Ababa, Bole')}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Price in Birr')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': _('Provide a detailed description...')}),
        }

# ============================
# ==== 3. Update Forms ====
# ============================

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': _('Username'),
            'email': _('Email Address'),
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'phone_number']
        labels = {
            'profile_picture': _('Profile Picture'),
            'bio': _('Bio'),
            'phone_number': _('Phone Number'),
        }
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g., 0911....')}),
        }