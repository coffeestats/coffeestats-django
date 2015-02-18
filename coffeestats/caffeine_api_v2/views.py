from rest_framework import permissions, viewsets

from caffeine.models import Caffeine, User
from .serializers import CaffeineSerializer, UserSerializer
from .permissions import IsOwnerOrReadOnly


class CaffeineViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """
    queryset = Caffeine.objects.all()
    serializer_class = CaffeineSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows caffeine entries to be viewed.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
