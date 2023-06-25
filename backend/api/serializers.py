import base64

from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import exceptions, serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueValidator

from recipes.models import Ingredient, IngredientToRecipe, Recipe, Tag
from users.models import Subscribe, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class SubcribesRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    id = serializers.ReadOnlyField(source='ingredient.pk')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientToRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientsToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1,
                message='не может быть менее одного ингридиента!'
            ),
        )
    )

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'amount'
        )


class UserListSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    def get_is_subscribed(self, following):
        """ Проверка подписки."""

        data = self.context.get('request')
        return (
            not (data is None or data.user.is_anonymous)
            and Subscribe.objects.filter(
                user=data.user,
                author=following
            ).exists()
        )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class RecipesListSerializer(serializers.ModelSerializer):
    author = UserListSerializer()
    ingredients = IngredientToRecipeSerializer(
        source='recipe',
        many=True
    )
    tags = TagsSerializer(many=True)
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    def get_is_favorited(self, select):
        """ Проверка рецепта в избранном."""

        user = self.context.get('request').user
        return (
            not user.is_anonymous
            and user.select.filter(recipe=select).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        """ Проверка рецепта в корзине."""

        user = self.context.get('request').user
        return (
            not user.is_anonymous
            and user.listingredientuser.filter(
                recipe=recipe
            ).exists()
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
            'cooking_time'
        )


class RecipeSendSerializer(serializers.ModelSerializer):
    author = UserListSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientsToRecipeSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1,
                message='время не может быть меньше 1.'
            ),
        )
    )

    def validate_tags(self, value):
        """ Валидатор тегов."""

        if not value:
            raise exceptions.ValidationError(
                'не может быть меньше одного тега.'
            )

        tags = set()
        for item in value:
            if item in tags:
                raise exceptions.ValidationError(
                    'не может быть одинаковых тегов.'
                )
            tags.add(item)

        return value

    def validate_ingredients(self, value):
        """ Валидатор ингридиентов."""

        if not value:
            raise exceptions.ValidationError(
                'не может быть менее одного ингридиента.'
            )

        ingredients = set()
        for item in value:
            if item['id'] in ingredients:
                raise exceptions.ValidationError(
                    'не может быть одинаковых ингридиентов.'
                )
            ingredients.add(item['id'])
        return value

    def create(self, validated_data):
        """ Запись рецепта."""

        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient = get_object_or_404(Ingredient, pk=ingredient['id'])
            IngredientToRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        """ Обновление рецепта."""

        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()
            for ingredient in ingredients:
                amount = ingredient['amount']
                ingredient = get_object_or_404(Ingredient, pk=ingredient['id'])
                IngredientToRecipe.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient,
                    defaults={'amount': amount}
                )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """ Возврат результата."""

        r_serializer = RecipesListSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return r_serializer.data

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class UserSendSerializer(UserCreateSerializer):
    username = serializers.RegexField(
        regex=r"^[\w.@+-]+\Z", max_length=150,
        validators=[
            UniqueValidator(
                queryset=User.objects.all()
            )
        ]
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class PasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, obj):
        """ Валидатор пароля."""

        try:
            validate_password(obj['new_password'])
        except django_exceptions.ValidationError as error:
            raise serializers.ValidationError(
                {'new_password': list(error.messages)}
            )
        return super().validate(obj)

    def update(self, instance, validated_data):
        """ Обновление пароля."""

        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'пароль введен неверно!'}
            )
        if (
            validated_data['current_password']
            == validated_data['new_password']
        ):
            raise serializers.ValidationError(
                {'new_password': 'введенный пароль совпадает с текущим!'}
            )

        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class SubscribeSerializer(UserListSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('email', 'username')

    def get_recipes_count(self, recipes):
        """ Количество рецептов юзера."""

        return recipes.recipes.count()

    def get_recipes(self, recipes):
        """ Рецепты подписки."""

        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = recipes.recipes.all()

        if limit:
            recipes = recipes[:int(limit)]

        serializer = SubcribesRecipesSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data
