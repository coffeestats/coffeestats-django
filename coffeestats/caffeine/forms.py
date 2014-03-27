from django import forms
from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationFormUniqueEmail
from captcha.fields import ReCaptchaField

from .models import User


class CoffeestatsRegistrationForm(RegistrationFormUniqueEmail):
    firstname = forms.CharField(label=_("First name"))
    lastname = forms.CharField(label=_("Last name"))
    location = forms.CharField(label=_("Location"))
    captcha = ReCaptchaField()

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        existing = User.objects.filter(
            username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(
                _("A user with that username already exists."))
        else:
            return self.cleaned_data['username']

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(
                _("This email address is already in use. "
                  "Please supply a different email address."))
        return self.cleaned_data['email']
