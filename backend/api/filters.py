from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class TagsFilter(filters.FilterSet):
    """Фильтр тегов."""
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='startswith'
    )

    class Meta:
        model = Tag
        fields = ('name',)


class IngredientsFilter(filters.FilterSet):
    """Фильтр ингредиентов."""
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='startswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


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
