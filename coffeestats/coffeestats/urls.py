from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views.i18n import JavaScriptCatalog

admin.autodiscover()

urlpatterns = [
    url(r"^", include("caffeine.urls")),
    url(
        r"^api/v1/",
        include(("caffeine_api_v1.urls", "caffeine_api_v1"), namespace="apiv1"),
    ),
    # new API
    url(r"^api/v2/", include("caffeine_api_v2.urls")),
    # authentication
    url(
        r"^auth/login/$",
        auth_views.LoginView.as_view(template_name="django_registration/login.html"),
        name="auth_login",
    ),
    url(
        r"^auth/logout/$",
        auth_views.LogoutView.as_view(
            template_name="django_registration/logout.html", next_page="/"
        ),
        name="auth_logout",
    ),
    url(
        r"^auth/password/change/$",
        auth_views.PasswordChangeView.as_view(),
        name="auth_password_change",
    ),
    url(
        r"^auth/password/change/done/$",
        auth_views.PasswordChangeDoneView.as_view(),
        name="auth_password_change_done",
    ),
    url(
        r"^auth/password/reset/$",
        auth_views.PasswordResetView.as_view(
            template_name="django_registration/password_reset_form.html",
            email_template_name="django_registration/password_reset_email.txt",
            subject_template_name="django_registration/password_reset_subject.txt",
            success_url=reverse_lazy("auth_password_reset_done"),
        ),
        name="auth_password_reset",
    ),
    url(
        r"^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="django_registration/password_reset_confirm.html",
            success_url=reverse_lazy("auth_password_reset_complete"),
        ),
        name="auth_password_reset_confirm",
    ),
    url(
        r"^password/reset/complete/$",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="django_registration/password_reset_complete.html"
        ),
        name="auth_password_reset_complete",
    ),
    url(
        r"^password/reset/done/$",
        auth_views.PasswordResetDoneView.as_view(
            template_name="django_registration/password_reset_done.html"
        ),
        name="auth_password_reset_done",
    ),
    # javascript i18n
    url(
        r"^jsi18n/(?P<packages>\S+?)/$",
        JavaScriptCatalog.as_view(),
        name="jsi18n_catalog",
    ),
    # admin site
    url(r"^admin/", admin.site.urls),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    from django.contrib.staticfiles.views import serve as serve_static
    from django.views.decorators.cache import never_cache

    urlpatterns += [
        url(r"^__debug__/", include(debug_toolbar.urls)),
        url(r"^static/(?P<path>.*)$", never_cache(serve_static)),
    ]
