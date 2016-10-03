from django.conf import settings
from django.core.urlresolvers import (
    reverse,
    reverse_lazy,
)
from django.http import (
    HttpResponseRedirect,
)
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_GET
from django.views.generic import (
    RedirectView,
    TemplateView,
    View,
)
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import (
    BaseFormView,
    DeleteView,
    FormView,
    UpdateView,
)

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from braces.views import LoginRequiredMixin
from registration.backends.model_activation.views import (
    ActivationView,
    RegistrationView,
)
from pytz import common_timezones

from core.utils import json_response

from .forms import (
    CoffeestatsRegistrationForm,
    SelectTimeZoneForm,
    SettingsForm,
    SubmitCaffeineForm,
)

from .models import (
    ACTION_TYPES,
    Action,
    Caffeine,
    DRINK_TYPES,
    User,
)

ACTIVATION_SUCCESS_MESSAGE = _('Your account has been activated successfully.')
DELETE_ACCOUNT_MESSAGE = _(
    'Your account and all your caffeine submissions have been deleted.')
DELETE_CAFFEINE_SUCCESS_MESSAGE = _('Entry deleted successfully!')
EMAIL_CHANGE_SUCCESS_MESSAGE = _(
    'Your email address has been changed successfully.')
EXPORT_SUCCESS_MESSAGE = _(
    'Your data has been exported. You will receive an email with two CSV '
    'files with your coffee and mate registrations attached.'
)
REGISTRATION_SUCCESS_MESSAGE = _('You got it.')
REGISTRATION_MAILINFO_MESSAGE = _(
    'We have sent you an email with a link to activate your account')
SETTINGS_EMAIL_CHANGE_MESSAGE = _(
    'We sent an email with a link that you need to open to confirm the '
    'change of your email address.'
)
SELECT_TIMEZONE_SUCCESS_MESSAGE = _(
    'Your time zone has been set to %(timezone)s successfully.')
SETTINGS_PASSWORD_CHANGE_SUCCESS = _('Successfully changed your password!')
SETTINGS_SUCCESS_MESSAGE = _('Successfully updated your profile information!')
SUBMIT_CAFFEINE_SUCCESS_MESSAGE = _('Your %(caffeine)s has been registered')


class AboutView(LoginRequiredMixin, TemplateView):
    template_name = 'about.html'


class ExploreView(LoginRequiredMixin, TemplateView):
    template_name = 'explore.html'

    def get_context_data(self, **kwargs):
        context_data = super(ExploreView, self).get_context_data(**kwargs)
        context_data.update({
            'activities': Caffeine.objects.latest_caffeine_activity(10),
            'users': User.objects.random_users(4),
            'topcoffee': Caffeine.objects.top_consumers_total(
                DRINK_TYPES.coffee, 10),
            'topcoffeeavg': Caffeine.objects.top_consumers_average(
                DRINK_TYPES.coffee, 10),
            'topmate': Caffeine.objects.top_consumers_total(
                DRINK_TYPES.mate, 10),
            'topmateavg': Caffeine.objects.top_consumers_average(
                DRINK_TYPES.mate, 10),
            'topcoffeerecent': Caffeine.objects.top_consumers_recent(
                DRINK_TYPES.coffee, 10, '30 days'),
            'topmaterecent': Caffeine.objects.top_consumers_recent(
                DRINK_TYPES.mate, 10, '30 days'),
            'recentlyjoined': User.objects.recently_joined(5),
            'longestjoined': User.objects.longest_joined(
                count=5, days=365)})
        return context_data


class ExportActivityView(LoginRequiredMixin, RedirectView):
    permanent = False
    url = reverse_lazy('settings')

    def get_redirect_url(self, *args, **kwargs):
        self.request.user.export_csv()
        messages.add_message(
            self.request, messages.INFO,
            EXPORT_SUCCESS_MESSAGE)
        return super(ExportActivityView, self).get_redirect_url(
            *args, **kwargs)


class DeleteAccountView(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy('home')

    def get_success_url(self):
        logout(self.request)
        messages.add_message(
            self.request, messages.INFO,
            DELETE_ACCOUNT_MESSAGE)
        return super(DeleteAccountView, self).get_success_url()

    def get_object(self):
        return self.request.user


class ImprintView(TemplateView):
    template_name = 'imprint.html'


class IndexView(TemplateView):
    template_name = 'index.html'


class OverallView(TemplateView):
    template_name = 'overall.html'

    def get_context_data(self, **kwargs):
        total = Caffeine.objects.total_caffeine()

        context_data = super(OverallView, self).get_context_data(**kwargs)
        context_data.update({
            'coffees': total[DRINK_TYPES.coffee],
            'mate': total[DRINK_TYPES.mate],
            'todaydata': Caffeine.objects.hourly_caffeine(),
            'monthdata': Caffeine.objects.daily_caffeine(),
            'yeardata': Caffeine.objects.monthly_caffeine_overall(),
            'byhourdata': Caffeine.objects.hourly_caffeine_overall(),
            'byweekdaydata': Caffeine.objects.weekdaily_caffeine_overall(),
        })
        return context_data


class PublicProfileView(TemplateView):
    template_name = 'profile.html'
    ownprofile = False
    profileuser = None

    def get_context_data(self, **kwargs):
        context = super(PublicProfileView, self).get_context_data(**kwargs)
        if 'username' in self.kwargs:
            self.profileuser = get_object_or_404(
                User, username=self.kwargs['username'])
        else:
            self.profileuser = self.request.user

        total = Caffeine.objects.total_caffeine_for_user(self.profileuser)
        todaydata = Caffeine.objects.hourly_caffeine_for_user(
            self.profileuser)
        monthdata = Caffeine.objects.daily_caffeine_for_user(
            self.profileuser)
        yeardata = Caffeine.objects.monthly_caffeine_for_user(
            self.profileuser)
        byhourdata = Caffeine.objects.hourly_caffeine_for_user_overall(
            self.profileuser)
        byweekdaydata = Caffeine.objects.weekdaily_caffeine_for_user_overall(
            self.profileuser)

        context.update({
            'byhourdata': byhourdata,
            'byweekdaydata': byweekdaydata,
            'coffees': total[DRINK_TYPES.coffee],
            'mate': total[DRINK_TYPES.mate],
            'monthdata': monthdata,
            'ownprofile': self.ownprofile,
            'profileuser': self.profileuser,
            'todaydata': todaydata,
            'yeardata': yeardata,
        })
        return context


class ProfileView(PublicProfileView):
    ownprofile = True

    def get(self, request, *args, **kwargs):
        if 'u' in request.GET:
            return HttpResponseRedirect(reverse('public', kwargs={
                'username': request.GET['u']}))
        if not request.user.is_authenticated():
            return HttpResponseRedirect(
                "%s?next=%s" % (settings.LOGIN_URL, request.path))
        return super(ProfileView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        entries = Caffeine.objects.latest_caffeine_for_user(
            self.profileuser)
        context.update({
            'entries': entries,
        })
        return context


class CaffeineActivationView(ActivationView):
    def get_success_url(self, user):
        messages.add_message(
            self.request, messages.SUCCESS, ACTIVATION_SUCCESS_MESSAGE)
        return reverse_lazy('home')


class CaffeineRegistrationView(RegistrationView):
    """
    Customized version of the RegistrationView.

    """
    form_class = CoffeestatsRegistrationForm

    def get_success_url(self, user):
        messages.add_message(
            self.request, messages.SUCCESS, REGISTRATION_SUCCESS_MESSAGE)
        messages.add_message(
            self.request, messages.INFO, REGISTRATION_MAILINFO_MESSAGE)
        return reverse_lazy('home')

    def register(self, form):
        new_user = super(CaffeineRegistrationView, self).register(form)
        new_user.first_name = form.cleaned_data['firstname']
        new_user.last_name = form.cleaned_data['lastname']
        new_user.location = form.cleaned_data['location']
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

    def get_context_data(self, **kwargs):
        context = super(SettingsView, self).get_context_data(**kwargs)
        user = self.request.user

        applications = user.caffeine_oauth2_coffeestatsapplication.count()
        tokens = user.accesstoken_set.count()

        context.update({
            'oauth2_applications': applications > 0,
            'oauth2_tokens': tokens > 0,
        })
        return context

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
            SETTINGS_EMAIL_CHANGE_MESSAGE)

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.SUCCESS,
            SETTINGS_SUCCESS_MESSAGE)
        if form.email_action:
            self.send_email_change_mail(form)
        form.save()
        if form.password_set:
            messages.add_message(
                self.request, messages.SUCCESS,
                SETTINGS_PASSWORD_CHANGE_SUCCESS)
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
                EMAIL_CHANGE_SUCCESS_MESSAGE)
            user.save()
            action.delete()
        return HttpResponseRedirect(reverse_lazy('home'))


class OnTheRunView(TemplateView):
    template_name = "ontherun.html"

    def get_context_data(self, *args, **kwargs):
        get_object_or_404(
            User, username=self.kwargs['username'],
            token=self.kwargs['token'])
        return super(OnTheRunView, self).get_context_data(*args, **kwargs)


class OnTheRunOldView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        user = get_object_or_404(
            User, username=self.request.GET.get('u'),
            token=self.request.GET.get('t'))
        return reverse('ontherun', kwargs={
            'username': user.username,
            'token': user.token})


class BaseSubmitCaffeineView(BaseFormView):
    form_class = SubmitCaffeineForm
    http_method_names = ['post']

    def form_valid(self, form):
        caffeine = form.save()
        messages.add_message(
            self.request, messages.SUCCESS,
            SUBMIT_CAFFEINE_SUCCESS_MESSAGE % {
                'caffeine': caffeine},
            extra_tags='registerdrink')
        return super(BaseSubmitCaffeineView, self).form_valid(form)

    def form_invalid(self, form):
        for field in form.errors:
            for error in form.errors[field]:
                messages.add_message(
                    self.request, messages.ERROR, error,
                    extra_tags='registerdrink')
        return HttpResponseRedirect(self.get_success_url())


class SubmitCaffeineView(LoginRequiredMixin, BaseSubmitCaffeineView):
    def get_form_kwargs(self):
        kwargs = super(SubmitCaffeineView, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'ctype': getattr(DRINK_TYPES, self.kwargs['drink']),
        })
        return kwargs

    def get_success_url(self):
        return reverse('profile')


class SubmitCaffeineOnTheRunView(BaseSubmitCaffeineView):
    def get_form_kwargs(self):
        user = get_object_or_404(
            User, username=self.kwargs['username'], token=self.kwargs['token'])
        kwargs = super(SubmitCaffeineOnTheRunView, self).get_form_kwargs()
        kwargs.update({
            'user': user,
            'ctype': getattr(DRINK_TYPES, self.kwargs['drink']),
        })
        return kwargs

    def get_success_url(self):
        return reverse_lazy('ontherun', kwargs={
            'username': self.kwargs['username'],
            'token': self.kwargs['token']})


class DeleteCaffeineView(LoginRequiredMixin, DeleteView):
    """
    View for deleting caffeine instances.

    """
    model = Caffeine
    success_url = reverse_lazy('profile')

    def get_queryset(self):
        """
        Make sure that only own caffeine can be deleted.
        """
        return super(DeleteCaffeineView, self).get_queryset().filter(
                user=self.request.user)

    def get_success_url(self):
        """
        Return the success URL and add a message about the successful deletion.

        """
        messages.add_message(
            self.request, messages.SUCCESS, DELETE_CAFFEINE_SUCCESS_MESSAGE)
        return super(DeleteCaffeineView, self).get_success_url()


class SelectTimeZoneView(LoginRequiredMixin, UpdateView):
    form_class = SelectTimeZoneForm
    template_name = 'selecttimezone.html'

    def get_context_data(self, **kwargs):
        context = super(SelectTimeZoneView, self).get_context_data(**kwargs)
        context.update({
            'tzlist': common_timezones
        })
        return context

    def form_valid(self, form):
        form.save()
        messages.add_message(
            self.request, messages.SUCCESS,
            SELECT_TIMEZONE_SUCCESS_MESSAGE % {
                'timezone': form.cleaned_data['timezone']})
        return super(SelectTimeZoneView, self).form_valid(form)

    def get_success_url(self):
        success_url = self.request.GET.get('next', reverse('profile'))
        if success_url == reverse('selecttimezone'):
            success_url = reverse('profile')
        return success_url

    def get_object(self):
        return self.request.user


@require_GET
@login_required
@json_response
def random_users(request):
    data = []
    for user in User.objects.random_users(int(request.GET.get('count', 5))):
        data.append({
            'username': user.username,
            'name': user.get_full_name(),
            'location': user.location,
            'profile': request.build_absolute_uri(
                reverse('public', kwargs={'username': user.username})),
            'coffees': user.coffees,
            'mate': user.mate})
    return data
