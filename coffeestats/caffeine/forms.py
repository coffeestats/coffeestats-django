from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationFormUniqueEmail
from captcha.fields import ReCaptchaField

from .models import (
    ACTION_TYPES,
    Action,
    User,
)


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


class SettingsForm(forms.ModelForm):
    password1 = forms.CharField(required=False)
    password2 = forms.CharField(required=False)
    password_set = False
    email_action = None

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'location']

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password2 and password1 and password1 != password2:
            raise forms.ValidationError(_('Passwords must match!'))
        return password2

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        emailuser = User.objects.filter(
            email__iexact=self.cleaned_data['email']).first()
        if emailuser is not None and emailuser != self.instance:
            raise forms.ValidationError(
                _("This email address is already in use. "
                  "Please supply a different email address."))
        if self.cleaned_data['email'] != self.instance.email:
            self.email_action = Action.objects.create_action(
                self.instance, ACTION_TYPES.change_email,
                self.cleaned_data['email'],
                settings.EMAIL_CHANGE_ACTION_VALIDITY)
            self.cleaned_data['email'] = self.instance.email
        return self.cleaned_data['email']

    def clean(self):
        cleaned_data = super(SettingsForm, self).clean()
        if self.cleaned_data['password2']:
            self.password_set = True
            self.instance.set_password(
                self.cleaned_data['password2'])
        return cleaned_data
