from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='base.html')),

urlpatterns = patterns(
    '',
    url(r'^', include('caffeine.urls')),
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
