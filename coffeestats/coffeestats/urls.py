from django.conf.urls import include, url
from django.conf import settings
from django.views.i18n import javascript_catalog

from django.contrib.auth import views as auth_views
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^', include('caffeine.urls')),
    url(r'^api/v1/', include('caffeine_api_v1.urls', 'apiv1')),
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
    # javascript i18n
    url(r'^jsi18n/(?P<packages>\S+?)/$', javascript_catalog,
        name='jsi18n_catalog'),
    # admin site
    url(r'^admin/', include(admin.site.urls)),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    from django.contrib.staticfiles.views import serve as serve_static
    from django.views.decorators.cache import never_cache
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^static/(?P<path>.*)$', never_cache(serve_static)),
    ]
