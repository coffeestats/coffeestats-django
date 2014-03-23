from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin


class AboutView(LoginRequiredMixin, TemplateView):
    template_name = 'about.html'


class ActivationCompleteView(TemplateView):
    template_name = 'registration/activation_complete.html'


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


class RegistrationClosedView(TemplateView):
    template_name = 'registration/registration_closed.html'


class RegistrationCompleteView(TemplateView):
    template_name = 'registration/registration_complete.html'


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'settings.html'
