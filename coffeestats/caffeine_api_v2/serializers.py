from caffeine.models import User, Caffeine
from rest_framework import serializers


# add_drink
class CaffeineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Caffeine
        fields = (
            'url', 'user', 'date', 'entrytime', 'timezone',
            'ctype'
        )


# random_users
class UserSerializer(serializers.HyperlinkedModelSerializer):
    caffeines = serializers.HyperlinkedRelatedField(
        many=True, view_name='caffeine-detail', read_only=True)

    class Meta:
        model = User
        fields = (
            'url', 'username', 'location', 'first_name', 'last_name',
            'caffeines',
        )
# 'name': user.get_full_name(),
# 'profile': request.build_absolute_uri(
#   reverse('public', kwargs={'username': user.username})),
# coffees, mate
