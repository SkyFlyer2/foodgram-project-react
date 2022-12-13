from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from users.models import User, Follow
from recipes.models import Tag, Ingredient
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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


