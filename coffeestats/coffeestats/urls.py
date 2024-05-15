from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, re_path, reverse_lazy
from django.views.i18n import JavaScriptCatalog

admin.autodiscover()

urlpatterns = [
    re_path(r"^", include("caffeine.urls")),
    re_path(
        r"^api/v1/",
        include(("caffeine_api_v1.urls", "caffeine_api_v1"), namespace="apiv1"),
    ),
    # new API
    re_path(r"^api/v2/", include("caffeine_api_v2.urls")),
    # authentication
    re_path(
        r"^auth/login/$",
        auth_views.LoginView.as_view(template_name="django_registration/login.html"),
        name="auth_login",
    ),
    re_path(
        r"^auth/logout/$",
        auth_views.LogoutView.as_view(
            template_name="django_registration/logout.html", next_page="/"
        ),
        name="auth_logout",
    ),
    re_path(
        r"^auth/password/change/$",
        auth_views.PasswordChangeView.as_view(),
        name="auth_password_change",
    ),
    re_path(
        r"^auth/password/change/done/$",
        auth_views.PasswordChangeDoneView.as_view(),
        name="auth_password_change_done",
    ),
    re_path(
        r"^auth/password/reset/$",
        auth_views.PasswordResetView.as_view(
            template_name="django_registration/password_reset_form.html",
            email_template_name="django_registration/password_reset_email.txt",
            subject_template_name="django_registration/password_reset_subject.txt",
            success_url=reverse_lazy("auth_password_reset_done"),
        ),
        name="auth_password_reset",
    ),
    re_path(
        r"^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="django_registration/password_reset_confirm.html",
            success_url=reverse_lazy("auth_password_reset_complete"),
        ),
        name="auth_password_reset_confirm",
    ),
    re_path(
        r"^password/reset/complete/$",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="django_registration/password_reset_complete.html"
        ),
        name="auth_password_reset_complete",
    ),
    re_path(
        r"^password/reset/done/$",
        auth_views.PasswordResetDoneView.as_view(
            template_name="django_registration/password_reset_done.html"
        ),
        name="auth_password_reset_done",
    ),
    # javascript i18n
    re_path(
        r"^jsi18n/(?P<packages>\S+?)/$",
        JavaScriptCatalog.as_view(),
        name="jsi18n_catalog",
    ),
    # admin site
    re_path(r"^admin/", admin.site.urls),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    from django.contrib.staticfiles.views import serve as serve_static
    from django.views.decorators.cache import never_cache

    urlpatterns += [
        re_path(r"^__debug__/", include(debug_toolbar.urls)),
        re_path(r"^static/(?P<path>.*)$", never_cache(serve_static)),
    ]
