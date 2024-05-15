from django.urls import re_path

from .views import add_drink, random_users

urlpatterns = [
    re_path(r"random-users$", random_users, name="random_users"),
    re_path(r"add-drink$", add_drink, name="add_drink"),
]
