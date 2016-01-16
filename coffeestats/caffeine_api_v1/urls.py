from django.conf.urls import url

from .views import (
    add_drink,
    random_users,
)

urlpatterns = [
    url(r'random-users$', random_users, name='random_users'),
    url(r'add-drink$', add_drink, name='add_drink'),
]
