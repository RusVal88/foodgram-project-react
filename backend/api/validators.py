import re

from rest_framework import validators
from rest_framework import serializers
from rest_framework import status


def validate_username(value):
    """Валидация username на коректность."""
    if value.lower() == 'me':
        raise validators.ValidationError(
            '"me" в качестве логина использовать нельзя!'
        )
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise validators.ValidationError(
            'Введены некоректные символы!'
        )
    return value


def validate_first_last_name(value):
    """Валидация first_name и last_name на коректность."""
    if not re.match(r'^[\w.@+-]+\Z', value):
        raise validators.ValidationError(
            'Введены некоректные символы!'
        )
    return value


def validate_subscription(data, user, author):
    """Валидация подписки на автора и на себя."""
    if user == author:
        raise serializers.ValidationError(
            detail='Нельзя подписаться на самого себя!',
            code=status.HTTP_400_BAD_REQUEST,
        )
    if user.subscriber.filter(author=author).exists():
        raise serializers.ValidationError(
            detail='Данная подписка уже существует!',
            code=status.HTTP_400_BAD_REQUEST,
        )
    return data


def validate_slug(value):
    """Валидация slug на коректность."""
    if not re.match(r'^[-a-zA-Z0-9_]+$', value):
        raise validators.ValidationError(
            'Введены некоректные символы!'
        )
    return value


def validate_cooking_time(value):
    """Валидация cooking_time на ограничение по времени."""
    if value < 1:
        raise validators.ValidationError(
            'Время приготовления должно быть не менее 1 минуты!'
        )
    return value


def validate_amount(value):
    """
    Валидация amount на ограничение по
    количеству единицы измерения ингредиента.
    """
    if value < 1:
        raise validators.ValidationError(
            'Количество единицы измерения ингредиента,'
            ' должно быть не менее 1гр!'
        )
    return value


def validate_recipe(data):
    """
    Валидация создания рецепта, на отсутствие обязательных полей,
    ограгичение количества ингредиентов и тегов в рецепте,
    а также уникальность ингредиеннта.
    """
    fields = ['name', 'text', 'cooking_time']
    missing_fields = [
        field for field in fields if not data.get(field)
    ]
    if missing_fields:
        raise serializers.ValidationError(
            ', '.join(
                f'{field} - Обязательное поле для заполнения!'
                for field in missing_fields
            )
        )

    if not data.get('ingredients'):
        raise serializers.ValidationError(
            'Количество ингредиентов в рецепте,'
            ' должно быть не менее 1 ингредиента!'
        )

    if not data.get('tags'):
        raise serializers.ValidationError(
            'Нужно добавить не менее 1 тега!'
        )

    ingredients = [
        ingredient['id'] for ingredient in data.get('ingredients')
    ]
    duplicates = []
    for ingredient in ingredients:
        if ingredient in duplicates:
            raise serializers.ValidationError(
                'Ингредиенты в рецепте должны быть уникальны!'
            )
        duplicates.append(ingredient)


def validate_favorite_recipe(request, recipe, Favorite):
    """Валидация избранных рецептов."""
    if not request or not request.user.is_authenticated:
        raise serializers.ValidationError(
            'Пользователь не аутентифицирован!')

    if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
        raise serializers.ValidationError({
            'error': 'Данный рецепт уже имеется!'
        })
