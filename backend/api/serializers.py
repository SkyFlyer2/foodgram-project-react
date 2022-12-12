from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from users.models import User, Follow
from djoser.serializers import UserSerializer


class UsersSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)
    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed',
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

