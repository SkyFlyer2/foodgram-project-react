import django_filters
from recipes.models import Recipe, Ingredient


class IngredientsSearchFilter(django_filters.FilterSet):
#    search_param = '^name^',
#    lookup_expr="istartswith",
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="istartswith",
    )

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeAndTagsFilter(django_filters.FilterSet):
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    is_favorited = django_filters.BooleanFilter(method='filter_is_favorited')
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        print('value=',value)
        if self.request.user.is_authenticated and value:
            #return queryset.filter(in_favorite__user=self.request.user)
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(cart__user=self.request.user)
        return queryset
