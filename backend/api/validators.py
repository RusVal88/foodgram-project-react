import re

from rest_framework import validators, serializers


def validate_username(value):
    """Валидация username на коректность."""
    if value.lower() == 'me':
        raise validators.ValidationError(
            '"me" в качестве логина использовать нельзя!'
        )
    return value


def validate_name(value):
    """Валидация name на корректность."""
    if not re.match(r'^[а-яА-ЯёЁa-zA-Z\s]+$', value):
        raise validators.ValidationError(
            'Введены некорректные символы!'
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
