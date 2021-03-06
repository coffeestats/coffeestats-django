from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView
from oauth2_provider.views import ApplicationRegistration
from oauth2_provider.views.application import ApplicationDetail

from caffeine_oauth2.forms import CoffeestatsApplicationApprovalForm, \
    CoffeestatsApplicationForm, CoffeestatsApplicationRejectionForm
from caffeine_oauth2.models import CoffeestatsApplication


class MailContextMixin(object):
    def get_mail_context(self, application):
        current_site = get_current_site(self.request)
        return {
            'application': application,
            'site': current_site,
            'site_url': '{}://{}'.format(
                self.request.scheme, current_site.domain),
            'request': self.request,
        }


class CoffeestatsApplicationRegistration(MailContextMixin,
                                         ApplicationRegistration):
    mail_subject_template = 'caffeine_oauth2/mail_registered_subject.txt'
    mail_body_html_template = 'caffeine_oauth2/mail_registered_body.html'
    mail_body_text_template = 'caffeine_oauth2/mail_registered_body.txt'

    def get_form_class(self):
        """
        Returns a customized form class for the coffeestats application model.

        """
        return CoffeestatsApplicationForm

    def form_valid(self, form):
        application = form.save(commit=False)
        application.user = self.request.user
        application.save()
        self._send_new_application_mail(application)
        return super(CoffeestatsApplicationRegistration, self).form_valid(form)

    def _send_new_application_mail(self, application):
        mail_context = self.get_mail_context(application)
        mail_context.update({
            'approval_url': '{}{}'.format(
                mail_context['site_url'], reverse_lazy(
                    'oauth2_provider:approve', kwargs={'pk': application.id}))
        })

        send_mail(
            render_to_string(self.mail_subject_template, mail_context),
            render_to_string(self.mail_body_text_template, mail_context),
            settings.DEFAULT_FROM_EMAIL,
            [admin[1] for admin in settings.ADMINS],
            html_message=render_to_string(
                self.mail_body_html_template, mail_context)
        )


class CoffeestatsApplicationDetail(ApplicationDetail):

    def get_template_names(self):
        application = self.get_object()
        names = super(CoffeestatsApplicationDetail, self).get_template_names()
        if not application.approved:
            names.insert(0, 'caffeine_oauth2/pending_approval.html')
        return names


class ApproverRequiredMixin(PermissionRequiredMixin):
    permission_required = 'coffeestatsapplication.can_approve'


class CoffeestatsApplicationApproval(ApproverRequiredMixin, MailContextMixin,
                                     UpdateView):
    template_name = 'caffeine_oauth2/approve.html'
    context_object_name = 'application'
    queryset = CoffeestatsApplication.objects.filter(approved=False)
    form_class = CoffeestatsApplicationApprovalForm
    success_url = reverse_lazy('oauth2_provider:list_all')
    mail_subject_template = 'caffeine_oauth2/mail_approval_subject.txt'
    mail_body_html_template = 'caffeine_oauth2/mail_approval_body.html'
    mail_body_text_template = 'caffeine_oauth2/mail_approval_body.txt'

    def form_valid(self, form):
        application = form.save(commit=False)
        application.approve(self.request.user)
        application.save()
        self._send_approval_mail(application)
        return redirect(self.get_success_url())

    def _send_approval_mail(self, application):
        mail_context = self.get_mail_context(application)
        mail_context.update({
            'api_details': '{}{}'.format(
                mail_context['site_url'], reverse_lazy(
                    'oauth2_provider:detail', kwargs={'pk': application.id}))
        })

        send_mail(
            render_to_string(self.mail_subject_template, mail_context),
            render_to_string(self.mail_body_text_template, mail_context),
            settings.DEFAULT_FROM_EMAIL,
            [application.user.email],
            html_message=render_to_string(
                self.mail_body_html_template, mail_context)
        )


class CoffeestatsApplicationRejection(ApproverRequiredMixin, MailContextMixin,
                                      UpdateView):
    template_name = 'caffeine_oauth2/reject.html'
    context_object_name = 'application'
    queryset = CoffeestatsApplication.objects.filter(approved=False)
    form_class = CoffeestatsApplicationRejectionForm
    success_url = reverse_lazy('oauth2_provider:list_all')
    mail_subject_template = 'caffeine_oauth2/mail_reject_subject.txt'
    mail_body_html_template = 'caffeine_oauth2/mail_reject_body.html'
    mail_body_text_template = 'caffeine_oauth2/mail_reject_body.txt'

    def form_valid(self, form):
        application = self.get_object()
        self._send_rejection_mail(form.cleaned_data['reasoning'])
        application.reject()
        return redirect(self.get_success_url())

    def _send_rejection_mail(self, reasoning):
        application = self.get_object()
        mail_context = self.get_mail_context(application)
        mail_context.update({
            'reasoning': reasoning
        })

        send_mail(
            render_to_string(self.mail_subject_template, mail_context),
            render_to_string(self.mail_body_text_template, mail_context),
            settings.DEFAULT_FROM_EMAIL,
            [application.user.email],
            html_message=render_to_string(
                self.mail_body_html_template, mail_context)
        )


class CoffeestatsApplicationFullList(ApproverRequiredMixin, ListView):
    model = CoffeestatsApplication
    template_name = 'caffeine_oauth2/list_all.html'
    context_object_name = 'applications'
