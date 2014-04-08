from django.conf.urls import patterns, url

from .views import (
    add_drink,
    random_users,
)

urlpatterns = patterns(
    '',
    url(r'random-users$', random_users, name='random_users'),
    url(r'add-drink$', add_drink, name='add_drink'),
)
