from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientsFilter(FilterSet):
    """ Фильтр ингридиентов."""

    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipesFilter(FilterSet):
    """ Фильтр рецептов."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        method='selected_filter'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='cart_filter'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
        )

    def selected_filter(self, queryset, name, value):
        """ Фильтр избранного."""

        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(recipe__user=user)
        return queryset

    def cart_filter(self, queryset, name, value):
        """ Фильтр покупок."""

        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(recipelist__user=user)
        return queryset
