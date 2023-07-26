from rest_framework import status
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
from users.models import User
from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            IngredientQuantity,
                            ShoppingCart,
                            Favorite)
from api.filters import (IngredientsFilter,
                         RecipesFilter)
from api.permissions import IsAuthorOrReadOnly
from api.paginations import LimitPaginator


class UserViewSet(GenericViewSet):
    """
    Вьюсет для создание и получение списков пользователей,
    а также на создание, удаление и получения списка подписок.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    search_fields = ('username', 'email')
    permission_classes = (AllowAny,)
    pagination_class = LimitPaginator

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk):
        """Подписка на и отписка от пользователя."""
        author = get_object_or_404(User, pk=pk)
        user = request.user
        subscriptions = request.user.subscriber.filter(
            user=user,
            author=author
        )
        if request.method == 'POST':
            if subscriptions.exists():
                message = 'Данная подписка уже существует!'
                return Response(
                    {'detail': message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if user == author:
                message = 'Нельзя подписаться на самого себя!'
                return Response(
                    {'detail': message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = SubscriptionsSerializer(
                author,
                context={'request': request}
            )
            request.user.subscriber.create(
                user=request.user,
                author=author
            )
            message = 'Вы успешно подписались на пользователя!'
            return Response(
                {'detail': message, 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if subscriptions.exists():
                subscriptions.delete()
                message = 'Пользователь удалён из подписок!'
                return Response(
                    {'detail': message},
                    status=status.HTTP_204_NO_CONTENT
                )
            message = 'Вы не подписаны на данного пользователя!'
            return Response(
                {'detail': message},
                status=status.HTTP_400_BAD_REQUEST
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
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для получения ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientsFilter,)
    search_fields = ('^name',)
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
    pagination_class = LimitPaginator

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateUpdateSerializer

    def create_or_delete_item(
            self,
            request,
            pk,
            model_class,
            serializer_class,
            message_exists,
            message_post,
            message_http404,
            message_delete
    ):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if model_class.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                return Response(
                    {'detail': message_exists},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data = {
                'user': user.id,
                'recipe': recipe.id
            }
            serializer = serializer_class(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'detail': message_post, 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        try:
            item = get_object_or_404(
                model_class,
                user=user,
                recipe=recipe
            )
        except Http404:
            return Response(
                {'detail': message_http404},
                status=status.HTTP_400_BAD_REQUEST
            )
        item.delete()
        return Response(
            {'detail': message_delete},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True
    )
    def favorite(self, request, pk=None):
        return self.create_or_delete_item(
            request,
            pk,
            model_class=Favorite,
            serializer_class=FavoriteSerializer,
            message_exists='Рецепт уже присутствует в избранном!',
            message_post='Рецепт добавлен в избранное!',
            message_http404='Рецепт не найден в избранном!',
            message_delete='Рецепт удалён из избранного!'
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True
    )
    def shopping_cart(self, request, pk=None):
        return self.create_or_delete_item(
            request,
            pk,
            model_class=ShoppingCart,
            serializer_class=ShoppingCartSerializer,
            message_exists='Рецепт уже присутствует в списке покупок!',
            message_post='Рецепт добавлен в список покупок!',
            message_http404='Рецепт не найден в списке покупок!',
            message_delete='Рецепт удалён из списка покупок!'
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_cart_items = request.user.shopping_cart.all().values(
            'recipe_id'
        )
        ingredients = IngredientQuantity.objects.filter(
            recipe__in=shopping_cart_items
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
