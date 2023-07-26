from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.validators import MinValueValidator
from drf_base64.fields import Base64ImageField

from users.models import User
from api.validators import (validate_recipe,
                            validate_favorite_recipe)
from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            IngredientQuantity,
                            Favorite,
                            ShoppingCart)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """
        Метод проверяет подписан ли текущий пользователь на этого.
        """
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.subscriber.filter(author=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        read_only_fields = '__all__',


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор списка ингридиентов."""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientQuantitySerializer(serializers.ModelSerializer):
    """Сериализатор количества ингредиента."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.ReadOnlyField()

    class Meta:
        model = IngredientQuantity
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов в рецепт."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        validators=[MinValueValidator(1)])

    class Meta:
        model = IngredientQuantity
        fields = (
            'id',
            'amount'
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор создания и обновления рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = UserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(1)])

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        validate_recipe(data)
        return data

    def create_ingredients(self, ingredients, recipe):
        ingredients_list = [
            IngredientQuantity(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients
        ]
        IngredientQuantity.objects.bulk_create(ingredients_list)

    def add_tags(self, tags, recipe):
        recipe.tags.set(tags)

    def create(self, validated_data):
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context['request'].user
        recipe = Recipe.objects.create(
            author=author,
            image=image,
            **validated_data
        )
        self.add_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(
            instance, context=context).data

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientQuantity.objects.filter(recipe=instance).delete()
        self.add_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор списка рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientQuantitySerializer(
        many=True,
        read_only=True,
        source='ingredient'
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        queryset = IngredientQuantity.objects.filter(recipe=obj)
        return IngredientQuantitySerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        favorites = request.user.favorites.filter(recipe=obj)
        return favorites.exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return False
        shopping_cart = request.user.shopping_cart.filter(recipe=obj)
        return shopping_cart.exists()


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Уменьшенный рецепт."""
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор добавления и удаления в избранное."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        recipe = data['recipe']
        validate_favorite_recipe(request, recipe, Favorite)
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeMinifiedSerializer(
            instance.recipe, context=context).data


class ShoppingCartSerializer(FavoriteSerializer):
    """
    Сериализатор добавления и удаления в список покупок.
    """
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор подписок."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )

    def get_recipes(self, author):
        request = self.context.get('request')
        if request is None:
            return False
        limit = request.query_params.get('recipes_limit')
        try:
            if limit:
                recipes = author.recipes.all()[:int(limit)]
            else:
                recipes = author.recipes.all()
        except ValueError:
            raise ValidationError(
                'Некорректное значение,'
                ' Ожидалось целое число.'
            )
        return RecipeMinifiedSerializer(
            recipes,
            read_only=True,
            many=True
        ).data

    def get_recipes_count(self, object):
        return object.recipes.count()
