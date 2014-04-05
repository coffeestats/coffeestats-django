from django.conf.urls import patterns, url

from .views import (
    random_users,
)

urlpatterns = patterns(
    '',
    url(r'random-users$', random_users, name='random_users'),
)
