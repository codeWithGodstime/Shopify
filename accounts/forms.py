from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, BillingAddress

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username',)

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'username', "first_name", "last_name", "profile_image")

class BillingAddressForm(forms.ModelForm):
    class Meta:
        model = BillingAddress
        fields = ("address_line_1", "address_line_2", "city", "state", "postal_code", "country")