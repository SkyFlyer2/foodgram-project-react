from django.contrib import admin

from .models import (Favorites, Ingredient, Ingredients_quantity, Recipe,
                     Order_cart, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'quantity_in_favorites')
    readonly_fields = ('quantity_in_favorites',)
    list_filter = ('author', 'name', 'tags',)

    #@display(description='Добавлено в избранное')
    def quantity_in_favorites(self, obj):
        return obj.favorites.count()
#    quantity_in_favorites.description='Добавлено в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(Order_cart)
class OrderCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(Favorites)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(Ingredients_quantity)
class IngredientInRecipe(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'quantity',)
