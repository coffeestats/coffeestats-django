from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.validators import BaseUniqueForValidator

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


class NoRecentCaffeineValidator(BaseUniqueForValidator):
    message = None

    def __init__(self, user_field, ctype_field, date_field, message=None):
        self.queryset = None
        self.date_field = date_field
        self.field = ctype_field
        self.user_field = user_field
        self.message = message or self.message

    def set_context(self, serializer):
        """
        This hook is called by the serializer instance, prior to the validation
        call being made.
        """
        self.field_date = serializer.fields[self.date_field].source_attrs[-1]
        self.field_ctype = serializer.fields[self.field].source_attrs[-1]
        self.user = serializer.context['view'].view_owner
        self.instance = getattr(serializer, 'instance', None)

    def filter_queryset(self, attrs, queryset):
        user = self.user
        date = attrs[self.field_date]
        ctype = attrs[self.field_ctype]
        self.message = (
            'Your last %(drink)s was less than %(minutes)d minutes ago.'
        ) % dict(
            drink=READABLE_DRINK_TYPES[ctype][0],
            minutes=settings.MINIMUM_DRINK_DISTANCE)
        return Caffeine.objects.recent_caffeine_queryset(user, date, ctype)


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

    validators = [
        NoRecentCaffeineValidator('user', 'ctype', 'date')
    ]


class UserCaffeineSerializer(serializers.HyperlinkedModelSerializer):
    ctype = CaffeineField()
    user = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='user-detail', lookup_field='username')

    class Meta:
        model = Caffeine
        fields = (
            'url', 'date', 'entrytime', 'timezone', 'ctype', 'user'
        )
        validators = [
            NoRecentCaffeineValidator('user', 'ctype', 'date')
        ]

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
