from caffeine.models import User, Caffeine, DRINK_TYPES
from rest_framework import serializers


READABLE_DRINK_TYPES = [
    (triple[1], triple[2]) for triple in DRINK_TYPES._triples]


class CaffeineField(serializers.Field):
    """
    This class provides a serializer field to map from labels in DRINK_TYPES
    to numeric values as used in the Caffeine model's ctype field.

    """

    def to_representation(self, obj):
        for key, attr, _ in DRINK_TYPES._triples:
            if key == obj:
                return attr
        # this should not happen
        raise RuntimeError(
            "Could not map database internal id {0} to value".format(obj))

    def to_internal_value(self, data):
        return getattr(DRINK_TYPES, data)


class CaffeineSerializer(serializers.HyperlinkedModelSerializer):
    ctype = CaffeineField()

    class Meta:
        model = Caffeine
        fields = (
            'url', 'user', 'date', 'timezone', 'ctype'
        )
        extra_kwargs = {
            'user': {'lookup_field': 'username'},
        }


class UserCaffeineSerializer(serializers.HyperlinkedModelSerializer):
    ctype = CaffeineField()
    user = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='user-detail', lookup_field='username')

    class Meta:
        model = Caffeine
        fields = (
            'url', 'date', 'entrytime', 'timezone', 'ctype', 'user'
        )

    def save(self):
        user = self.context['view'].view_owner
        self.validated_data['user'] = user
        if (
            'timezone' not in self.validated_data or
            not self.validated_data['timezone']
        ):
            self.validated_data['timezone'] = user.timezone
        return super(UserCaffeineSerializer, self).save()


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
