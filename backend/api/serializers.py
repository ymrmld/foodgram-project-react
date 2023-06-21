from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueValidator

from recipes.models import Ingredient, Recipe, Tag
from users.models import Subscribe, User


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class UserListSerializer(UserSerializer):
    """ Сериализатор для получения юзеров."""

    is_subscribed = SerializerMethodField(read_only=True)

    def get_is_subscribed(self, following):
        """ Проверка подписки."""

        data = self.context.get('request')
        if data is None or data.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=data.user,
            author=following
        ).exists()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        model = User


class UserSendSerializer(UserCreateSerializer):
    """ Сериализатор создания юзера."""

    username = serializers.RegexField(
        regex=r"^[\w.@+-]+\Z", max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        model = User


class PasswordSerializer(serializers.Serializer):
    """ Сериализатор для смены пароля юзера."""

    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, obj):
        """ Валидатор пароля."""

        try:
            validate_password(obj['new_password'])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)}
            )
        return super().validate(obj)

    def update(self, instance, validated_data):
        """ Обновление пароля."""

        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'пароль введен неверно!'}
            )
        if (
          validated_data['current_password'] == validated_data['new_password']
        ):
            raise serializers.ValidationError(
                {'new_password': 'введенный пароль совпадает с текущим!'}
            )

        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class RecipesSubscribeSerializer(serializers.ModelSerializer):
    """ Сериализатор рецепта подписки."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(UserListSerializer):
    """ Сериализатор подписки."""

    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('email', 'username')

    def get_recipes_count(self, recipes):
        """ Вывод количества рецептов юзера."""

        return recipes.recipes.count()

    def get_recipes(self, recipes):
        """ Рецепты подписки."""

        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = recipes.recipes.all()

        if limit:
            recipes = recipes[:int(limit)]

        serializer = RecipesSubscribeSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data
