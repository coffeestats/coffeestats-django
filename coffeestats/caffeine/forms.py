from django import forms
from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationFormUniqueEmail
from captcha.fields import ReCaptchaField


class CoffeestatsRegistrationForm(RegistrationFormUniqueEmail):
    firstname = forms.CharField(label=_("First name"))
    lastname = forms.CharField(label=_("Last name"))
    location = forms.CharField(label=_("Location"))
    captcha = ReCaptchaField()
