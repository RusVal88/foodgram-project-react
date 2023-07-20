from colorfield.fields import ColorField
from django.db import models

from api.validators import (validate_slug,
                            validate_cooking_time,
                            validate_amount,)
from users.models import User


class Ingredient(models.Model):
    """Создание таблицы ингредиентов."""
    name = models.CharField(
        verbose_name='Название ингредиента',
        help_text='Укажите название ингредиента!',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения ингредиента',
        help_text='Укажите единицу измерения ингредиента!',
        max_length=200,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_measurement_unit_for_ingredient'),
        ]
        ordering = ('id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}.'


class Tag(models.Model):
    """Создание таблицы тегов."""
    name = models.CharField(
        verbose_name='Название тега',
        help_text='Укажите название тега!',
        max_length=200,
        unique=True,
    )
    color = ColorField(
        verbose_name='Цвет тега в HEX',
        help_text='Укажите цвет тега!',
        format='hex',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='slug тега',
        help_text='Укажите slug тега!',
        max_length=200,
        unique=True,
        validators=[validate_slug,],
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Создание таблицы рецептов."""
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        help_text='Укажите автора рецепта!',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        help_text='Укажите название рецепта!',
        max_length=200,
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        help_text='Добавьте изображение рецепта!',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Добавьте описание рецепта!',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты для рецепта',
        help_text='Добавьте ингредиенты для рецепта!',
        related_name='recipes',
        through='IngredientQuantity',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег рецепта',
        help_text='Добавьте тег рецепта!',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления по рецепту',
        help_text='Укажите время приготовления!',
        validators=[validate_cooking_time],
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe_for_author'),
        ]

    def __str__(self):
        return f'Рецепт: {self.name}. Автор: {self.author.username}.'


class IngredientQuantity(models.Model):
    """ Создание таблицы количества ингредиентов."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='recipe',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        help_text='Укажите количество ингредиента!',
        validators=[validate_amount,],
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'),
        ]

    def __str__(self):
        return (
            f'{self.recipe.name}: '
            f'{self.ingredient.name} - '
            f'{self.amount}'
            f'{self.ingredient.measurement_unit}'
        )


class Favorite(models.Model):
    """Создание таблицы избранных рецептов."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_favorites'),
        ]

    def __str__(self):
        return f'{self.recipe} в списке избранных у {self.user}'


class ShoppingCart(models.Model):
    """Создание таблицы списка покупок."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_chart_for_user'),
        ]

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
