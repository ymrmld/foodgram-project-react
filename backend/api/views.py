from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Ingredient, IngredientToRecipe, Recipe,
                            RecipesCart, SelectedRecipe, Tag)
from users.models import Subscribe, User

from .filtres import IngredientsFilter, RecipesFilter
from .paginations import LimitPagination
from .permissions import OwnerOrReadOnly
from .serializers import (IngredientsSerializer, PasswordSerializer,
                          RecipeSendSerializer, RecipesListSerializer,
                          SubcribesRecipesSerializer, SubscribeSerializer,
                          TagsSerializer, UserListSerializer,
                          UserSendSerializer)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitPagination
    permission_classes = (OwnerOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    serializer_class = RecipesListSerializer

    def get_serializer_class(self):
        """ Вывод списка рецептов."""

        if self.request.method in SAFE_METHODS:
            return RecipesListSerializer
        return RecipeSendSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """ Избранные рецепты."""

        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if self.request.method == 'POST':
            if SelectedRecipe.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    {'errors': 'рецепт уже в избранном'}
                )
            SelectedRecipe.objects.create(user=user, recipe=recipe)
            serializer = SubcribesRecipesSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not SelectedRecipe.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    {'errors': 'рецепта нет в избранном'}
                )
            selected = get_object_or_404(
                SelectedRecipe,
                user=user,
                recipe=recipe
            )
            selected.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        """ Добавление/удаление покупок."""

        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if self.request.method == 'POST':
            if RecipesCart.objects.filter(user=user, recipe=recipe).exists():
                raise exceptions.ValidationError(
                    {'errors': 'уже добавлено в список покупок.'}
                )
            RecipesCart.objects.create(user=user, recipe=recipe)
            serializer = SubcribesRecipesSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not RecipesCart.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise exceptions.ValidationError(
                    {'errors': 'не найдено в списке покупок'}
                )
            cartlist = get_object_or_404(RecipesCart, user=user, recipe=recipe)
            cartlist.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """ Загрузка списка покупок."""

        user = request.user
        if not user.listingredientuser.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientToRecipe.objects.filter(
            recipe__listrecipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        header = 'Что нужно купить:\n\n'
        purchases = f'{header}'
        purchases += '\n'.join([
            f'{ingredient["ingredient__name"]}'
            f' - {ingredient["amount"]}'
            f' {ingredient["ingredient__measurement_unit"]}.'
            for ingredient in ingredients
        ])
        file = 'purchases.txt'
        response = HttpResponse(purchases, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file}'
        return response


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """ Работа с ингридиентами."""

    queryset = Ingredient.objects.all()
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter
    serializer_class = IngredientsSerializer


class UsersViewSet(viewsets.ModelViewSet):
    """ Для работы с юзерами."""

    queryset = User.objects.all()
    pagination_class = LimitPagination
    permission_classes = (AllowAny,)
    serializer_class = UserListSerializer

    def get_serializer_class(self):
        """ Вывод списка юзеров."""

        if self.action in ('list', 'retrieve'):
            return UserListSerializer
        return UserSendSerializer

    @action(
        detail=False,
        methods=['get'],
        pagination_class=None,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        """ Инфо о текущем юзере."""

        serializer = UserListSerializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False, methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        """ Смена пароля."""

        serializer = PasswordSerializer(
            request.user,
            data=request.data
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            {'detail': 'пароль изменен!'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """ Работа с подписками."""

        user = self.request.user
        author = get_object_or_404(User, pk=pk)
        if self.request.method == 'POST':
            if user == author:
                raise exceptions.ValidationError(
                    {'errors': 'нельзя подписаться на себя!'}
                )

            if Subscribe.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError(
                    {'errors': 'вы уже подписаны на этого пользователя!'}
                )
            Subscribe.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not Subscribe.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError(
                    {'errors': 'такой подписки нет!'}
                )

            subscription = get_object_or_404(
                Subscribe,
                user=user,
                author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """ Список подписок пользователя."""

        user = self.request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """ Для работы с тегами."""

    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = TagsSerializer
