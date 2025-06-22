from django.core.exceptions import ValidationError
import re

class SpecialCharacterValidator:
    def validate(self, password, user=None):
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                "This password must contain at least one special character.",
                code='password_no_special_char',
            )

    def get_help_text(self):
        return "Your password must contain at least one special character."