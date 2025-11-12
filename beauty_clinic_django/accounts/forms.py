from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from .models import User
import re


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form for our custom User model"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    middle_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle Name (Optional)'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    phone = forms.CharField(
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '09123456789',
            'maxlength': '11',
            'pattern': '09[0-9]{9}',
            'title': 'Enter 11-digit Philippine phone number starting with 09'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'middle_name', 'email', 'phone', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
    
    def clean_phone(self):
        """Validate Philippine phone number format"""
        phone = self.cleaned_data.get('phone')
        
        if phone:  # Only validate if phone is provided
            # Remove any non-digit characters
            phone_digits = re.sub(r'\D', '', phone)
            
            # Check if it's exactly 11 digits and starts with 09
            if len(phone_digits) != 11 or not phone_digits.startswith('09'):
                raise ValidationError(
                    'Please enter a valid 11-digit Philippine phone number starting with 09 (e.g., 09123456789)'
                )
            
            return phone_digits  # Return cleaned phone number
        
        return phone  # Return empty string if no phone provided
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.middle_name = self.cleaned_data['middle_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.user_type = 'patient'  # Default to patient
        
        if commit:
            user.save()
        return user


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with enhanced styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })


class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with enhanced styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        })


class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middle_name', 'email', 'phone', 'address', 
                  'gender', 'civil_status', 'birthday', 'occupation', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '11'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'civil_status': forms.Select(attrs={'class': 'form-control'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def clean_phone(self):
        """Validate Philippine phone number format"""
        phone = self.cleaned_data.get('phone')
        
        if phone:
            phone_digits = re.sub(r'\D', '', phone)
            if len(phone_digits) != 11 or not phone_digits.startswith('09'):
                raise ValidationError(
                    'Please enter a valid 11-digit Philippine phone number starting with 09 (e.g., 09123456789)'
                )
            return phone_digits
        
        return phone
