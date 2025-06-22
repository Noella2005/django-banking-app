from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser

# This is the form for the registration page
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email')


class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        """
        This method is called by Django's login view to check if a user is
        allowed to log in. We've added a check for the 'is_frozen' status.
        """
        super().confirm_login_allowed(user)
        
        # This check prevents a user with a frozen account from logging in
        if hasattr(user, 'account') and user.account.is_frozen:
            raise ValidationError(
                "Your account has been frozen. Please contact support for assistance.",
                code='account_frozen',
            )