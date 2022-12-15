from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from django.shortcuts import get_object_or_404
from django.db.models import F
from users.models import User, Follow
from recipes.models import Tag, Ingredient, Recipe, Favorites, ShoppingCart, IngredientsForRecipes
from djoser.serializers import UserSerializer
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        SlugRelatedField, ValidationError)
from drf_extra_fields.fields import Base64ImageField


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


class RecipeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UsersSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UsersSerializer.Meta):
        fields = UsersSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )
        read_only_fields = ('email', 'username')
    
    # исправить, как в yatube_api!

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

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeInfoSerializer(recipes, many=True, read_only=True)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

class IngredientsForRecipes(serializers.ModelSerializer):
    id = PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientsForRecipes
        fields = ('id', 'amount',)
#    measurement_unit = SlugRelatedField(
#        source='ingredient',
#        slug_field='measurement_unit',
#        read_only=True,
#    )
#    name = SlugRelatedField(
#        source='ingredient',
#        slug_field='name',
#        read_only=True,
#    )

#    class Meta:
#        model = IngredientsForRecipes
#        fields = (
#            'id',
#            'name',
#            'measurement_unit',
#            'amount',
#        )



class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
#    ingredients = IngredientsForRecipes(
#        many=True,
#        read_only=True,
#    )
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
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorites.objects.filter(
            user=request.user, recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe__id=obj.id).exists()


class NewRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True, max_length=None)
    author = UsersSerializer(read_only=True)
    ingredients = IngredientsForRecipes(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'image', 'tags', 'author', 'ingredients',
            'name', 'text', 'cooking_time',
        )

    def validate_ingredients(self, value):
        ingredients = value
        print(ingredients)
        if not ingredients:
            raise ValidationError({'Необходимо добавить ингридиенты!'})
        ingredients_list = []
        for item in ingredients:
            print(item)
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError({'Ингридиенты должны быть уникальными!'})
#            if int(item['amount']) <= 0:
#                raise ValidationError({
#                    'amount': 'Количество ингредиента должно быть больше 0!'
#                })
            ingredients_list.append(ingredient)
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

#    @atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=request.user,
            **validated_data
        )
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

#    @atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = instance
        IngredientsForRecipes.objects.filter(recipe=recipe).delete()
        self.create_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)
