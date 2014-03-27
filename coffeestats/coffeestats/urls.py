from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib.auth import views as auth_views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^', include('caffeine.urls')),
    # authentication
    url(r'^auth/login/$', auth_views.login,
        name='auth_login'),
    url(r'^auth/logout/$', auth_views.logout,
        {'next_page': '/'}, name='auth_logout'),
    url(r'^auth/password/change/$', auth_views.password_change,
        name='auth_password_change'),
    url(r'^auth/password/change/done/$', auth_views.password_change_done,
        name='auth_password_change_done'),
    url(r'^auth/password/reset/$',
        auth_views.password_reset,
        {'post_reset_redirect': 'auth_password_reset_done'},
        name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {'post_reset_redirect': 'auth_password_reset_complete'},
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
