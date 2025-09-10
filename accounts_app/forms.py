from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

class CustomLoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _(
            "Invalid username or password."
        ),
        'inactive': _("This account is inactive."),
    }
