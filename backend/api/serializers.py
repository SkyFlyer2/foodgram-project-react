from django.db import transaction
from django.db.models import F
from django.db import models
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorites, Ingredient, IngredientsForRecipes,
                            Recipe, ShoppingCart, Tag)
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (IntegerField, PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        )
from users.models import Follow, User


class UserRegistrationSerializer(UserCreateSerializer):
    """Регистрация нового пользователя"""

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UsersSerializer(UserSerializer):
    """Информация о пользователе"""

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Follow.objects.filter(user=user, author=obj).exists()
            )


class RecipeInfoSerializer(serializers.ModelSerializer):
    """Краткая информация о рецепте """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UsersSerializer):
    """Управление подписками"""

#    recipes_count = SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count',
                                             read_only=True)
    recipes = SerializerMethodField()

    class Meta(UsersSerializer.Meta):
        fields = UsersSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Разрешена только однократная подписка на автора!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

#    def get_recipes_count(self, obj):
#        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeInfoSerializer(recipes, many=True, read_only=True)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    """Теги"""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Ингредиенты"""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Управление выводом рецептов"""

    tags = TagSerializer(many=True, read_only=True)

    ingredients = SerializerMethodField()
    author = UsersSerializer(read_only=True)
    image = Base64ImageField()
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    is_favorited = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        )

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientsforrecipes__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Favorites.objects.filter(recipe=obj, user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(recipe=obj, user=user).exists()
        )


class IngredientsForRecipesNewSerializer(serializers.ModelSerializer):
    """Список ингредиентов для рецепта"""

    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientsForRecipes
        fields = ('id', 'amount',)


class NewRecipeSerializer(serializers.ModelSerializer):
    """Создание нового рецепта"""

    image = Base64ImageField(use_url=True)
    author = UsersSerializer(read_only=True)
    ingredients = IngredientsForRecipesNewSerializer(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    cooking_time = models.PositiveSmallIntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'image', 'tags', 'author', 'ingredients',
            'name', 'text', 'cooking_time',
        )

    def validate_ingredients(self, value):
        """Валидатор ингредиентов в рецепте."""

        ingredients = value
        if not ingredients:
            raise ValidationError({'Добавьте ингридиенты!'})
        for item in ingredients:
            if int(item['amount']) <= 0:
                raise ValidationError({
                    'Количество ингредиентов должно быть больше 0!'
                })
        items = [item["id"] for item in ingredients]
        if len(items) != len(set(items)):
            raise ValidationError({'Ингредиенты должны быть уникальными!'})
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError({'Выберите теги!'})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({'Теги не должны повторяться!'})
            tags_list.append(tag)
        return value

    @transaction.atomic
    def create_ingredients(self, recipe, ingredients):

        IngredientsForRecipes.objects.bulk_create(
            [IngredientsForRecipes(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            ) for ingredient in ingredients]
        )


    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context.get('request').user
        recipe = super().create(validated_data)
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        IngredientsForRecipes.objects.filter(recipe=instance).delete()
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request'),
            }
        ).data
