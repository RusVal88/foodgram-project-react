from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import (ModelViewSet,
                                     GenericViewSet,
                                     ReadOnlyModelViewSet)
from rest_framework.decorators import action
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated)
from rest_framework.response import Response

from api.serializers import (UserSerializer,
                             SubscriptionsSerializer,
                             TagSerializer,
                             IngredientSerializer,
                             RecipeCreateUpdateSerializer,
                             RecipeListSerializer,
                             ShoppingCartSerializer,
                             FavoriteSerializer)
from users.models import Subscriptions, User
from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            IngredientQuantity,
                            ShoppingCart,
                            Favorite)
from api.filters import (TagsFilter,
                         IngredientsFilter,
                         RecipesFilter)
from api.permissions import IsAuthorOrReadOnly


class UserViewSet(GenericViewSet):
    """
    Вьюсет для создание и получение списков пользователей,
    а также на создание, удаление и получения списка подписок.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    search_fields = ('username', 'email')
    permission_classes = (AllowAny,)
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk):
        """Подписка на и отписка от пользователя."""
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            serializer = SubscriptionsSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscriptions.objects.create(
                author=author,
                user=user
            )
            message = 'Вы успешно подписались на пользователя!'
            return Response(
                {'detail': message, 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        try:
            subscribe_item = get_object_or_404(
                Subscriptions,
                author=author,
                user=user
            )
        except Http404:
            message = 'Пользователь не найден в подписках!'
            return Response(
                {'detail': message},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscribe_item.delete()
        message = 'Пользователь удалён из подписок!'
        return Response(
            {'detail': message},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Подписки пользователя."""
        user = request.user
        page = self.paginate_queryset(
            User.objects.filter(author__user=user)
        )
        serializer = SubscriptionsSerializer(
            page, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для получения тегов."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TagsFilter
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для получения ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter
    search_fields = ("^name",)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """
    Вьюсет для создания, удаления рецептов,
    а также добавления,
    удаления рецептов в избраное и список покупок.
    """
    serializer_class = RecipeCreateUpdateSerializer
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateUpdateSerializer

    @action(
            methods=('POST', 'DELETE'),
            detail=True)
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                message = (
                    'Рецепт уже присутствует в избранном!'
                )
                return Response(
                    {'detail': message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data = {
                'user': user.id,
                'recipe': recipe.id
            }
            serializer = FavoriteSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            message = 'Рецепт добавлен в избранное!'
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        try:
            favorites_item = get_object_or_404(
                Favorite,
                user=user,
                recipe=recipe
            )
        except Http404:
            message = 'Рецепт не найден в избранном!'
            return Response(
                {'detail': message},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorites_item.delete()
        message = 'Рецепт удалён из избранного!'
        return Response(
            {'detail': message},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
            methods=['POST', 'DELETE'],
            detail=True
    )
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                message = (
                    'Рецепт уже присутствует в списке покупок!'
                )
                return Response(
                    {'detail': message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data = {
                'user': user.id,
                'recipe': recipe.id
            }
            serializer = ShoppingCartSerializer(
                data=data,
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            message = 'Рецепт добавлен в список покупок!'
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED)
        try:
            cart_item = get_object_or_404(
                ShoppingCart,
                user=user,
                recipe=recipe
            )
        except Http404:
            message = 'Рецепт не найден в списке покупок!'
            return Response(
                {'detail': message},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_item.delete()
        message = 'Рецепт удалён из списка покупок!'
        return Response(
            {'detail': message},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
            methods=['GET'],
            detail=False,
            permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shopping_cart_items = ShoppingCart.objects.filter(
            user=request.user
        )
        ingredients = IngredientQuantity.objects.filter(
            recipe__shopping_cart__in=shopping_cart_items
        ).order_by(
            'ingredient__name'
            ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
            ).annotate(
            amount=Sum('amount'))
        ingredients_text = ''
        for ingredient in ingredients:
            ingredients_text += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}"
            )
        response = HttpResponse(ingredients_text, content_type='text/plain')
        response[
            'Content-Disposition'
            ] = 'attachment; filename=shopping-cart.txt'
        return response
