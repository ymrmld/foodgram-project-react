from django.shortcuts import render
from rest_framework import status, viewsets
from .serializers import TagsSerializer, IngredientsSerializer
from recipes.models import Ingredient, Tag, Recipe
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from .filtres import IngredientsFilter
from django_filters.rest_framework import DjangoFilterBackend


class RecipeViewSet(viewsets.ModelViewSet):
    pass

class UserViewSet(viewsets.ModelViewSet):
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