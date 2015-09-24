from caffeine.models import User, Caffeine, DRINK_TYPES
from rest_framework import serializers


class CaffeineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Caffeine
        fields = (
            'url', 'user', 'date', 'timezone', 'ctype'
        )
        extra_kwargs = {
            'user': {'lookup_field': 'username'},
        }


class UserCaffeineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Caffeine
        fields = (
            'url', 'date', 'entrytime', 'timezone', 'ctype',
        )

    def save(self):
        self.validated_data['user'] = self.context['view'].view_owner
        super(UserCaffeineSerializer, self).save()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    caffeines = serializers.HyperlinkedIdentityField(
        view_name='user-caffeine-list', lookup_field='username',
        lookup_url_kwarg='caffeine_username')
    name = serializers.SerializerMethodField()
    profile = serializers.HyperlinkedIdentityField(
        view_name='public', lookup_field='username')
    counts = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'url', 'username', 'location', 'first_name', 'last_name',
            'name', 'profile', 'counts', 'caffeines',
        )
        extra_kwargs = {
            'url': {'lookup_field': 'username'},
        }

    def get_name(self, obj):
        return obj.get_full_name()

    def get_counts(self, obj):
        count_items = Caffeine.objects.total_caffeine_for_user(obj)
        return count_items
