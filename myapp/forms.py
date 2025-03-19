from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    account_type = forms.ChoiceField(
        choices=[
            ('customer', 'Customer'),
            ('restaurant_admin', 'Restaurant Admin'),
        ],
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'account_type', 'password1', 'password2')

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