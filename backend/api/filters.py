from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class IngredientsFilter(SearchFilter):
    """Фильтр ингредиентов."""
    search_param = 'name'


class RecipesFilter(filters.FilterSet):
    """Фильтр рецептов."""
    tags = filters.filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def filter_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return Recipe.objects.filter(
                id__in=self.request.user.favorites.all().values_list(
                    'recipe_id'
                )
            )
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return Recipe.objects.filter(
                id__in=self.request.user.shopping_cart.all().values_list(
                    'recipe_id'
                )
            )
        return queryset
