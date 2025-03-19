from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import CustomUser, Restaurant, Table, Booking

User = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    account_type = forms.ChoiceField(
        choices=[
            ('customer', 'Customer'),
            ('restaurant_admin', 'Restaurant Admin'),
        ],
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'account_type', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        account_type = self.cleaned_data['account_type']
        
        # Set user type flags
        user.is_customer = account_type == 'customer'
        user.is_restaurant_admin = account_type == 'restaurant_admin'
        
        if commit:
            user.save()
        return user 

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'description', 'address', 'phone_number', 'email', 'image', 
                 'opening_time', 'closing_time', 'max_capacity', 'cuisine_type', 'price_range']
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['restaurant', 'table_number', 'capacity', 'status']
        widgets = {
            'table_number': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'restaurant': forms.Select(attrs={'class': 'form-control'}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['user', 'table', 'date', 'time', 'number_of_guests', 'status', 'special_requests']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'number_of_guests': forms.NumberInput(attrs={'min': 1}),
            'special_requests': forms.Textarea(attrs={'rows': 3}),
        }

class ProfileForm(forms.ModelForm):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='Enter your current password to confirm changes'
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='Leave blank to keep current password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='Confirm your new password'
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        current_password = cleaned_data.get('current_password')

        if new_password or confirm_password:
            if not current_password:
                raise forms.ValidationError('Current password is required to change password')
            
            if not self.instance.check_password(current_password):
                raise forms.ValidationError('Current password is incorrect')
            
            if new_password != confirm_password:
                raise forms.ValidationError('New passwords do not match')
            
            if len(new_password) < 8:
                raise forms.ValidationError('New password must be at least 8 characters long')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('new_password'):
            user.set_password(self.cleaned_data['new_password'])
        if commit:
            user.save()
        return user 