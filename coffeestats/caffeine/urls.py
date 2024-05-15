# -*- python -*-

from django.urls import re_path

from .views import (
    AboutView,
    CaffeineActivationView,
    CaffeineRegistrationView,
    ConfirmActionView,
    DeleteAccountView,
    DeleteCaffeineView,
    ExploreView,
    ExportActivityView,
    ImprintView,
    IndexView,
    OnTheRunOldView,
    OnTheRunView,
    OverallView,
    ProfileView,
    PublicProfileView,
    RegistrationClosedView,
    SelectTimeZoneView,
    SettingsView,
    SubmitCaffeineOnTheRunView,
    SubmitCaffeineView,
    random_users,
)

urlpatterns = [
    re_path(r"^$", IndexView.as_view(), name="home"),
    # django_registration
    re_path(
        r"^auth/activate/(?P<activation_key>[-:\w]+)/$",
        CaffeineActivationView.as_view(),
        name="django_registration_activate",
    ),
    re_path(
        r"^auth/register/$",
        CaffeineRegistrationView.as_view(),
        name="django_registration_register",
    ),
    re_path(
        r"^auth/register/closed$",
        RegistrationClosedView.as_view(),
        name="django_registration_disallowed",
    ),
    re_path(r"^about/$", AboutView.as_view(), name="about"),
    re_path(r"^explore/$", ExploreView.as_view(), name="explore"),
    re_path(r"^imprint/$", ImprintView.as_view(), name="imprint"),
    re_path(r"^overall/$", OverallView.as_view(), name="overall"),
    re_path(r"^settings/$", SettingsView.as_view(), name="settings"),
    re_path(r"^selecttimezone/$", SelectTimeZoneView.as_view(), name="select_timezone"),
    re_path(r"^ontherun/$", OnTheRunOldView.as_view(), name="ontherunold"),
    re_path(
        r"^ontherun/(?P<username>[\w0-9@.+-_]+)/(?P<token>\w+)/$",
        OnTheRunView.as_view(),
        name="ontherun",
    ),
    re_path(
        r"^activity/export/$", ExportActivityView.as_view(), name="export_activity"
    ),
    re_path(r"^deletemyaccount/$", DeleteAccountView.as_view(), name="delete_account"),
    re_path(
        r"^(?P<drink>(coffee|mate))/submit/$",
        SubmitCaffeineView.as_view(),
        name="submit_caffeine",
    ),
    re_path(
        r"^(?P<drink>(coffee|mate))/submit/(?P<username>[\w0-9@.+-_]+)"
        r"/(?P<token>\w+)/$",
        SubmitCaffeineOnTheRunView.as_view(),
        name="submit_caffeine_otr",
    ),
    re_path(
        r"^action/confirm/(?P<code>\w+)/$",
        ConfirmActionView.as_view(),
        name="confirm_action",
    ),
    re_path(
        r"^delete/(?P<pk>\d+)/$", DeleteCaffeineView.as_view(), name="delete_caffeine"
    ),
    re_path(r"^profile/$", ProfileView.as_view(), name="profile"),
    re_path(
        r"^profile/(?P<username>[\w0-9@.+-_]+)/$",
        PublicProfileView.as_view(),
        name="public",
    ),
    re_path(r"^random-users$", random_users, name="random_users"),
]
