from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib.auth import views as auth_views
from django.contrib import admin
admin.autodiscover()

from registration.backends.default.views import (
    ActivationView,
    RegistrationView,
)

from caffeine.forms import CoffeestatsRegistrationForm

urlpatterns = patterns(
    '',
    url(r'^', include('caffeine.urls')),
    # registration
    url(r'^auth/activate/(?P<activation_key>\w+)/$', ActivationView.as_view(),
        name='registration_activate'),
    url(r'^auth/register/$', RegistrationView.as_view(
        form_class=CoffeestatsRegistrationForm),
        name='registration_register'),
    # authentication
    url(r'^auth/login/$', auth_views.login,
        name='auth_login'),
    url(r'^auth/logout/$', auth_views.logout,
        {'next_page': '/'}, name='auth_logout'),
    url(r'^auth/password/change/$', auth_views.password_change,
        name='auth_password_change'),
    url(r'^auth/password/change/done/$', auth_views.password_change_done,
        name='auth_password_change_done'),
    url(r'^auth/password/reset/$', auth_views.password_reset,
        name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        name='auth_password_reset_done'),
    # admin site
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
