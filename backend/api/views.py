from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import Ingredient, Tag
from users.models import Subscribe, User

from .filtres import IngredientsFilter
from .paginations import LimitPagination
from .serializers import (IngredientsSerializer, PasswordSerializer,
                          SubscribeSerializer, TagsSerializer,
                          UserListSerializer, UserSendSerializer)


class RecipesViewSet(viewsets.ModelViewSet):
    pass


class UsersViewSet(viewsets.ModelViewSet):
    pass


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """ Для работы с ингридиентами."""

    queryset = Ingredient.objects.all()
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = IngredientsSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsFilter


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """ Для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)


class UsersViewSet(viewsets.ModelViewSet):
    """ Для работы с юзерами."""

    queryset = User.objects.all()
    serializer_class = UserListSerializer
    pagination_class = LimitPagination
    permission_classes = (AllowAny,)

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
        """ Информация о текущем юзере."""

        serializer = UserListSerializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False, methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        """ Метод смены пароля."""

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
        """ Метод работы с подписками."""

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
                    {'errors': 'такой подписки нет'}
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
        """ Метод вывода списка подписок пользователя."""

        user = self.request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
