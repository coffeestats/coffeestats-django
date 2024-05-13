from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from rest_framework import permissions, viewsets

from caffeine.models import Caffeine, User
from .serializers import (
    CaffeineSerializer,
    UserCaffeineSerializer,
    UserSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsOwnCaffeineOrReadOnly


class CaffeineViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows caffeine entries to be viewed.
    """

    queryset = Caffeine.objects.all().order_by("-date")
    serializer_class = CaffeineSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """

    queryset = User.objects.all().order_by("username")
    serializer_class = UserSerializer
    lookup_field = "username"
    lookup_value_regex = r"[\w0-9@.+-_]+"


class UserCaffeineViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows working with a users caffeine entries.
    """

    serializer_class = UserCaffeineSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnCaffeineOrReadOnly,
        IsOwnerOrReadOnly,
    )
    _view_owner = None

    def _get_view_owner(self):
        if self._view_owner is None:
            self._view_owner = User.objects.get(
                username=self.kwargs["caffeine_username"]
            )
        return self._view_owner

    view_owner = property(_get_view_owner)

    def get_queryset(self):
        return self.view_owner.caffeines.all().order_by("-date")


class UsageAgreement(LoginRequiredMixin, TemplateView):
    template_name = "caffeine_api_v2/api_usage_agreement.html"
