from django.conf import settings
from django.core.urlresolvers import (
    reverse,
    reverse_lazy,
)
from django.http import (
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
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

from django.contrib import messages

from braces.views import LoginRequiredMixin
from registration.backends.default.views import (
    ActivationView,
    RegistrationView,
)
from pytz import common_timezones

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
            'recentlyjoined': User.objects.recently_joined(5),
            'longestjoined': User.objects.longest_joined(5)})
        return context_data


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
            return HttpResponseBadRequest(_('Invalid request!'))
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


class OnTheRunView(TemplateView):
    template_name = "ontherun.html"


class OnTheRunOldView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user = get_object_or_404(
            User, username=self.request.GET['u'], token=self.request.GET['t'])
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
            _('Your %(caffeine)s has been registered') % {
                'caffeine': caffeine},
            extra_tags='registerdrink')
        return super(BaseSubmitCaffeineView, self).form_valid(form)

    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.add_message(
                self.request, messages.ERROR, error,
                extra_tags='registerdrink')
        return HttpResponseRedirect(self.get_success_url())


class SubmitCaffeineView(LoginRequiredMixin, BaseSubmitCaffeineView):
    def get_form_kwargs(self):
        kwargs = super(SubmitCaffeineView, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'ctype': self.kwargs['drink'],
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
            'ctype': self.kwargs['drink'],
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

    def get_object(self, queryset=None):
        """
        Make sure that only own caffeine can be deleted.

        :param queryset queryset: the original query set or None

        """
        if queryset is None:
            queryset = self.get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return super(DeleteCaffeineView, self).get_object(queryset)

    def get_success_url(self):
        """
        Return the success URL and add a message about the successful deletion.

        """
        messages.add_message(
            self.request, messages.SUCCESS,
            _('Entry deleted successfully!'))
        return super(DeleteCaffeineView, self).get_success_url()


class SelectTimeZoneView(UpdateView):
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
            _('Your time zone has been set to %(timezone)s successfully.') % {
                'timezone': form.cleaned_data['timezone']})
        return super(SelectTimeZoneView, self).form_valid(form)

    def get_success_url(self):
        return self.request.GET['next']

    def get_object(self):
        return self.request.user
