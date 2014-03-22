from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

from registration.backends.simple.views import RegistrationView
from caffeine.forms import CoffeestatsRegistrationForm

urlpatterns = patterns(
    '',
    url(r'^', include('caffeine.urls')),
    # registration
    url(r'^register/$', RegistrationView.as_view(
        form_class=CoffeestatsRegistrationForm),
        name='registration_register'),
    url(r'^register/closed$', RegistrationView.as_view(),
        name='registration_disallowed'),
    # authentication
    url(r'^login/$', 'django.contrib.auth.views.login',
        name='login'),
    url(r'^passwordreset/$', 'django.contrib.auth.views.password_reset',
        name='password_reset'),
    # admin site
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
