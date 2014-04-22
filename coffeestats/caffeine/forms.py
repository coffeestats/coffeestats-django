from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import override as override_timezone

from registration.forms import RegistrationFormUniqueEmail
from captcha.fields import ReCaptchaField

from .models import (
    ACTION_TYPES,
    Action,
    Caffeine,
    DRINK_TYPES,
    User,
)

DUPLICATE_USER_ERROR = _("A user with that username already exists.")
DUPLICATE_EMAIL_ERROR = _(
    "This email address is already in use. "
    "Please supply a different email address."
)
PASSWORD_MISMATCH_ERROR = _('Passwords must match!')
INVALID_TIMEZONE_ERROR = _("Invalid time zone name")
EMPTY_TIMEZONE_ERROR = _("Time zone must not be empty.")


class CoffeestatsRegistrationForm(RegistrationFormUniqueEmail):
    firstname = forms.CharField(label=_("First name"), required=False)
    lastname = forms.CharField(label=_("Last name"), required=False)
    location = forms.CharField(label=_("Location"), required=False)
    captcha = ReCaptchaField()

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        existing = User.objects.filter(
            username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(DUPLICATE_USER_ERROR)
        else:
            return self.cleaned_data['username']

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(DUPLICATE_EMAIL_ERROR)
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

        if (password2 or password1) and password1 != password2:
            raise forms.ValidationError(PASSWORD_MISMATCH_ERROR)
        return password2

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        emailuser = User.objects.filter(
            email__iexact=self.cleaned_data['email']).first()
        if emailuser is not None and emailuser != self.instance:
            raise forms.ValidationError(DUPLICATE_EMAIL_ERROR)
        if self.cleaned_data['email'] != self.instance.email:
            self.email_action = Action.objects.create_action(
                self.instance, ACTION_TYPES.change_email,
                self.cleaned_data['email'],
                settings.EMAIL_CHANGE_ACTION_VALIDITY)
            self.cleaned_data['email'] = self.instance.email
        return self.cleaned_data['email']

    def clean(self):
        cleaned_data = super(SettingsForm, self).clean()
        if 'password2' in self.cleaned_data and \
                self.cleaned_data['password2']:
            self.password_set = True
            self.instance.set_password(
                self.cleaned_data['password2'])
        return cleaned_data


class SelectTimeZoneForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['timezone']
        error_messages = {
            'timezone': {
                'required': EMPTY_TIMEZONE_ERROR,
            },
        }

    def __init__(self, *args, **kwargs):
        super(SelectTimeZoneForm, self).__init__(*args, **kwargs)
        self.fields['timezone'].required = True

    def clean_timezone(self):
        timezone = self.cleaned_data['timezone']
        try:
            with override_timezone(timezone):
                return timezone
        except:
            raise forms.ValidationError(INVALID_TIMEZONE_ERROR)


class SubmitCaffeineForm(forms.ModelForm):
    class Meta:
        model = Caffeine
        fields = ['date']

    def __init__(self, user, ctype, *args, **kwargs):
        super(SubmitCaffeineForm, self).__init__(*args, **kwargs)
        self.instance.ctype = ctype
        self.instance.user = user
        self.instance.timezone = user.timezone

    def clean_date(self):
        recent_caffeine = Caffeine.objects.find_recent_caffeine(
            self.instance.user, self.cleaned_data['date'],
            self.instance.ctype)
        if recent_caffeine:
            raise forms.ValidationError(
                _('Your last %(drink)s was less than %(minutes)d minutes '
                  'ago at %(date)s %(timezone)s'),
                code='drinkfrequency',
                params={
                    'drink': DRINK_TYPES[self.instance.ctype],
                    'minutes': settings.MINIMUM_DRINK_DISTANCE,
                    'date': recent_caffeine.date,
                    'timezone': recent_caffeine.timezone
                }
            )
        return self.cleaned_data['date']
