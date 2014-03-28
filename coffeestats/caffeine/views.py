from django.conf import settings
from django.core.urlresolvers import (
    reverse,
    reverse_lazy,
)
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.views.generic import (
    TemplateView,
    View,
)
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView

from django.contrib import messages

from braces.views import LoginRequiredMixin
from registration.backends.default.views import (
    ActivationView,
    RegistrationView,
)

from .forms import (
    CoffeestatsRegistrationForm,
    SettingsForm,
)

from .models import (
    ACTION_TYPES,
    Action,
)


class AboutView(LoginRequiredMixin, TemplateView):
    template_name = 'about.html'


class ExploreView(LoginRequiredMixin, TemplateView):
    template_name = 'explore.html'


class ExportActivityView(LoginRequiredMixin, View):
    def get(self, request):
        # TODO: perform the export
        return HttpResponseRedirect(reverse_lazy('settings'))


class DeleteAccountView(LoginRequiredMixin, View):
    def get(self, request):
        # TODO: perform deletion
        return HttpResponseRedirect(reverse_lazy('settings'))


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


class SettingsView(LoginRequiredMixin, FormView):
    template_name = 'settings.html'
    form_class = SettingsForm
    success_url = reverse_lazy('settings')

    def get_form_kwargs(self):
        kwargs = super(SettingsView, self).get_form_kwargs()
        kwargs.update({
            'instance': self.request.user,
        })
        return kwargs

    def send_email_change_mail(self, form):
        ctx_dict = {
            'email': form.email_action.data,
            'expiration_days': settings.EMAIL_CHANGE_ACTION_VALIDITY,
            'action_link': self.request.build_absolute_uri(
                reverse('confirm_action',
                        kwargs={'code': form.email_action.code})),
            'user': self.request.user,
        }
        subject = render_to_string(
            'registration/email_change_email_subject.txt', ctx_dict)
        subject = ''.join(subject.splitlines())
        body = render_to_string('registration/email_change_email.txt',
                                ctx_dict)
        form.instance.email_user(subject, body, settings.DEFAULT_FROM_EMAIL)
        messages.add_message(
            self.request, messages.INFO,
            _('We sent an email with a link that you need to open to '
              'confirm the change of your email address.'))

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.SUCCESS,
            _('Successfully updated your profile information!'))
        if form.email_action:
            self.send_email_change_mail(form)
        form.save()
        if form.password_set:
            messages.add_message(
                self.request, messages.SUCCESS,
                _('Successfully changed your password!'))
        return super(SettingsView, self).form_valid(form)


class ConfirmActionView(SingleObjectMixin, View):
    model = Action
    slug_field = 'code'
    slug_url_kwarg = 'code'

    def get(self, request, *args, **kwargs):
        action = self.get_object()
        data, user = action.data, action.user
        if action.atype == ACTION_TYPES.change_email:
            user.email = data
            messages.add_message(
                request, messages.SUCCESS,
                _('Your email address has been changed successfully.'))
            user.save()
            action.delete()
        return HttpResponseRedirect(reverse_lazy('home'))
