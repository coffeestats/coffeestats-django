"""
Forms for coffeestats.

"""

from datetime import datetime

from django import forms
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_registration.forms import RegistrationFormUniqueEmail

from .models import ACTION_TYPES, Action, Caffeine, User

DUPLICATE_USER_ERROR = _("A user with that username already exists.")
DUPLICATE_EMAIL_ERROR = _(
    "This email address is already in use. " "Please supply a different email address."
)
PASSWORD_MISMATCH_ERROR = _("Passwords must match!")
INVALID_TIMEZONE_ERROR = _("Invalid time zone name")
EMPTY_TIMEZONE_ERROR = _("Time zone must not be empty.")


class CoffeestatsRegistrationForm(RegistrationFormUniqueEmail):
    """
    This is the form for registering new users.

    """

    firstname = forms.CharField(label=_("First name"), required=False)
    lastname = forms.CharField(label=_("Last name"), required=False)
    location = forms.CharField(label=_("Location"), required=False)

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        existing = User.objects.filter(username__iexact=self.cleaned_data["username"])
        if existing.exists():
            raise forms.ValidationError(DUPLICATE_USER_ERROR)
        else:
            return self.cleaned_data["username"]

    class Meta(RegistrationFormUniqueEmail.Meta):
        model = User


class SettingsForm(forms.ModelForm):
    """
    This is the form for changing a user's settings.

    """

    password1 = forms.CharField(required=False)
    password2 = forms.CharField(required=False)
    password_set = False
    email_action = None

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "location"]

    def clean_password2(self):
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]

        if (password2 or password1) and password1 != password2:
            raise forms.ValidationError(PASSWORD_MISMATCH_ERROR)
        return password2

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        emailuser = User.objects.filter(
            email__iexact=self.cleaned_data["email"]
        ).first()
        if emailuser is not None and emailuser != self.instance:
            raise forms.ValidationError(DUPLICATE_EMAIL_ERROR)
        if self.cleaned_data["email"] != self.instance.email:
            self.email_action = Action.objects.create_action(
                self.instance,
                ACTION_TYPES.change_email,
                self.cleaned_data["email"],
                settings.EMAIL_CHANGE_ACTION_VALIDITY,
            )
            self.cleaned_data["email"] = self.instance.email
        return self.cleaned_data["email"]

    def clean(self):
        cleaned_data = super(SettingsForm, self).clean()
        if "password2" in self.cleaned_data and self.cleaned_data["password2"]:
            self.password_set = True
            self.instance.set_password(self.cleaned_data["password2"])
        return cleaned_data


class SelectTimeZoneForm(forms.ModelForm):
    """
    This is the form for selecting a user's time zone.

    """

    class Meta:
        model = User
        fields = ["timezone"]
        error_messages = {
            "timezone": {
                "required": EMPTY_TIMEZONE_ERROR,
            },
        }

    def __init__(self, *args, **kwargs):
        super(SelectTimeZoneForm, self).__init__(*args, **kwargs)
        self.fields["timezone"].required = True

    def clean_timezone(self):
        cleantimezone = self.cleaned_data["timezone"]
        try:
            with timezone.override(cleantimezone):
                return cleantimezone
        except:
            raise forms.ValidationError(INVALID_TIMEZONE_ERROR)


class SubmitCaffeineForm(forms.ModelForm):
    """
    This is the form for new caffeine submissions.

    """

    date = forms.DateField(required=False)
    time = forms.TimeField(required=False)

    class Meta:
        model = Caffeine
        fields = []

    def __init__(self, user, ctype, *args, **kwargs):
        super(SubmitCaffeineForm, self).__init__(*args, **kwargs)
        self.instance.ctype = ctype
        self.instance.user = user
        self.instance.timezone = user.timezone

    def clean(self):
        if self.cleaned_data["date"] is None or self.cleaned_data["time"] is None:
            servertz = timezone.get_default_timezone()
            with timezone.override(self.instance.timezone):
                usertz = timezone.get_current_timezone()
                self.instance.date = timezone.make_naive(
                    timezone.localtime(
                        timezone.make_aware(timezone.now(), servertz), usertz
                    ),
                    usertz,
                )
        else:
            self.instance.date = datetime.combine(
                self.cleaned_data["date"], self.cleaned_data["time"]
            )
        return super(SubmitCaffeineForm, self).clean()
