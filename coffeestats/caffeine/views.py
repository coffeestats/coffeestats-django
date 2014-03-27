from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from django.contrib import messages

from braces.views import LoginRequiredMixin
from registration.backends.default.views import (
    ActivationView,
    RegistrationView,
)

from .forms import CoffeestatsRegistrationForm


class AboutView(LoginRequiredMixin, TemplateView):
    template_name = 'about.html'


class ExploreView(LoginRequiredMixin, TemplateView):
    template_name = 'explore.html'


class ImprintView(TemplateView):
    template_name = 'imprint.html'


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'


class OverallView(LoginRequiredMixin, TemplateView):
    template_name = 'overall.html'


class ProfileView(TemplateView):
    template_name = 'profile.html'


class CaffeineActivationView(ActivationView):
    def get_success_url(self, request, user):
        messages.add_message(
            request, messages.SUCCESS,
            _('Your account has been activated successfully.'))
        return reverse_lazy('home')


class CaffeineRegistrationView(RegistrationView):
    """
    Customized version of the RegistrationView.

    """
    form_class = CoffeestatsRegistrationForm

    def form_valid(self, form, request=None):
        return super(
            CaffeineRegistrationView, self).form_valid(form, request)

    def get_success_url(self, request, user):
        messages.add_message(
            request, messages.SUCCESS,
            _('You got it. Yes we hate CAPTCHAs too.'))
        messages.add_message(
            request, messages.INFO,
            _('We have sent you an email with a link to activate your '
              'account'))
        return reverse_lazy('home')

    def register(self, request, **cleaned_data):
        new_user = super(CaffeineRegistrationView, self).register(
            request, **cleaned_data)
        new_user.first_name = cleaned_data['firstname']
        new_user.last_name = cleaned_data['lastname']
        new_user.location = cleaned_data['location']
        new_user.save()
        return new_user


class RegistrationClosedView(TemplateView):
    template_name = 'registration/registration_closed.html'


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'settings.html'
