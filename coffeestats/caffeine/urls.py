# -*- python -*-

from django.conf.urls import patterns, url

from .views import (
    AboutView,
    ActivationCompleteView,
    CaffeineRegistrationView,
    ExploreView,
    ImprintView,
    IndexView,
    OverallView,
    ProfileView,
    RegistrationClosedView,
    SettingsView,
)

urlpatterns = patterns(
    '',
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^auth/activate/complete/$', ActivationCompleteView.as_view(),
        name='registration_activation_complete'),
    url(r'^auth/register/$', CaffeineRegistrationView.as_view(),
        name='registration_register'),
    url(r'^auth/register/closed$', RegistrationClosedView.as_view(),
        name='registration_disallowed'),
    url(r'^about/$', AboutView.as_view(), name='about'),
    url(r'^explore/$', ExploreView.as_view(), name='explore'),
    url(r'^imprint/$', ImprintView.as_view(), name='imprint'),
    url(r'^overall/$', OverallView.as_view(), name='overall'),
    url(r'^settings/$', SettingsView.as_view(), name='settings'),
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
)
