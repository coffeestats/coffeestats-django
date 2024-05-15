from django.urls import include, re_path
from rest_framework_nested import routers

from . import views

# Routers for determining the URL conf
router = routers.SimpleRouter()
router.register(r"users", views.UserViewSet)
router.register(r"caffeine", views.CaffeineViewSet)

users_router = routers.NestedSimpleRouter(router, r"users", lookup="caffeine")
users_router.register(r"caffeine", views.UserCaffeineViewSet, basename="user-caffeine")

urlpatterns = [
    re_path(r"", include(router.urls)),
    re_path(r"", include(users_router.urls)),
    re_path(r"agreement/$", views.UsageAgreement.as_view(), name="api_usage_agreement"),
]
