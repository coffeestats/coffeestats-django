from caffeine.models import User, Caffeine, DRINK_TYPES
from rest_framework import serializers


class CaffeineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Caffeine
        fields = (
            'url', 'user', 'date', 'entrytime', 'timezone',
            'ctype'
        )
        extra_kwargs = {
            'user': {'lookup_field': 'username'},
        }


class UserSerializer(serializers.HyperlinkedModelSerializer):
    caffeines = serializers.HyperlinkedRelatedField(
        many=True, view_name='caffeine-detail', read_only=True)
    name = serializers.SerializerMethodField()
    profile = serializers.HyperlinkedIdentityField(
        view_name='public', lookup_field='username')
    coffees = serializers.SerializerMethodField()
    mate = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'url', 'username', 'location', 'first_name', 'last_name',
            'caffeines', 'name', 'profile', 'coffees', 'mate',
        )
        extra_kwargs = {
            'url': {'lookup_field': 'username'},
        }

    def get_name(self, obj):
        return obj.get_full_name()

    def get_coffees(self, obj):
        return Caffeine.objects.total_caffeine_for_user(obj)[
            DRINK_TYPES.coffee]

    def get_mate(self, obj):
        return Caffeine.objects.total_caffeine_for_user(obj)[
            DRINK_TYPES.mate]
