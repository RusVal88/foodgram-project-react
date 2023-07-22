from django.contrib import admin

from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            Favorite,
                            ShoppingCart,
                            IngredientQuantity)


class TagAdmin(admin.ModelAdmin):
    """Админ зона(теги)."""
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name', 'slug')
    list_editable = ('slug',)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    """Админ зона(ингредиенты)."""
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name', 'measurement_unit')
    list_editable = ('name',)
    empty_value_display = '-пусто-'


class IngredientQuantityInline(admin.TabularInline):
    """Админ зона(класс редактирования связанных объектов)."""
    model = IngredientQuantity
    min_num = 1
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    """Админ зона(рецепты)."""
    list_display = (
        'id',
        'name',
        'cooking_time',
        'image',
        'author',
        'text',
    )
    search_fields = ('name',)
    list_filter = (
        'author',
        'name',
        'cooking_time',
    )
    list_editable = ('name',)
    inlines = (IngredientQuantityInline,)
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    """Админ зона(избранные)."""
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user',)
    list_filter = ('user', 'recipe')
    list_editable = ('user',)
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ зона(списки покупок)."""
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    list_editable = ('user', 'recipe')
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
