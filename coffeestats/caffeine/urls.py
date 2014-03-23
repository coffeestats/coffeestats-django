# -*- python -*-

from django.conf.urls import patterns, url

from .views import (
    AboutView,
    ExploreView,
    ImprintView,
    IndexView,
    OverallView,
    ProfileView,
    SettingsView,
)

urlpatterns = patterns(
    '',
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^about/$', AboutView.as_view(), name='about'),
    url(r'^explore/$', ExploreView.as_view(), name='explore'),
    url(r'^imprint/$', ImprintView.as_view(), name='imprint'),
    url(r'^overall/$', OverallView.as_view(), name='overall'),
    url(r'^settings/$', SettingsView.as_view(), name='settings'),
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
)
