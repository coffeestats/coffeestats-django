from rest_framework import permissions, viewsets
from rest_framework.reverse import reverse

from caffeine.models import Caffeine, User, DRINK_TYPES
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

    def create(self, request, *args, **kwargs):
        request.data['user'] = reverse(
            'user-detail', kwargs={'username': request.user.username},
            request=request)
        request.data['ctype'] = getattr(DRINK_TYPES, request.data['ctype'])
        return super(CaffeineViewSet, self).create(request, *args, **kwargs)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows caffeine entries to be viewed.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
