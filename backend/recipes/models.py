from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """ Модель тегов."""

    name = models.CharField(
        verbose_name='тег',
        max_length=20,
        unique=True
    )
    color = models.CharField(
        verbose_name='цвет',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='данное поле должно быть в формате HEX'
            )
        ]
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='ссылка'
    )

    def clean(self):
        self.name = self.name.lower()
        self.slug = self.slug.lower()
        self.color = self.color.lower()
        return super().clean()

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """ Модель ингридиентов."""

    name = models.CharField(
        verbose_name='ингридиент',
        max_length=100
    )
    measurement_unit = models.CharField(
        verbose_name='единица измерения ингредиента',
        max_length=30
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингридиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}.'


class Recipe(models.Model):
    """ Модель рецептов."""

    author = models.ForeignKey(
        User,
        verbose_name='автор шедевра',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='название шедевра',
        max_length=100,
    )
    image = models.ImageField(
        verbose_name='как выглядит блюдо',
        upload_to='recipes/images/',
        default=None,
        help_text='добавьте фото шедевра',
    )
    text = models.TextField(
        verbose_name='описание приготовления блюда',
        default='автор не добавил описание блюда',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='ингредиенты блюда',
        related_name='ingredients',
        through='IngredientToRecipe',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='тег',
        related_name='tags',
        through='RecipeToTag',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                message='приготовление не может занимать менее 1 минуты'
            ),
            MaxValueValidator(
                1440,
                message='приготовление не может занимать более одного дня'
            )
        ],
        default=1
    )
    pub_date = models.DateField(
        verbose_name='дата публикации рецепта',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.name}'


class IngredientToRecipe(models.Model):
    """ Модель ингридиентов в рецептах."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredienttorecipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(
                1,
                message='ингридиентов не может быть меньше 1'
            ),
            MaxValueValidator(
                30,
                message='ингридиентов не может быть больше 30'
            )
        ],
        verbose_name='количество ингридиентов'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'связь ингридиента с рецептом'
        verbose_name_plural = 'связи ингридиентов и рецептов'

    def __str__(self):
        return f'{self.recipe} - {self.ingredient} - {self.amount}'


class RecipeToTag(models.Model):
    """ Связь рецептов с тегами."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='тег'
    )

    class Meta:
        verbose_name = 'тег рецепта'
        verbose_name_plural = 'теги рецептов'

    def __str__(self):
        return f'{self.tag} - {self.recipe}'


class SelectedRecipe(models.Model):
    """ Избранный рецепт."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='select',
        verbose_name='авторы избранных',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeselect',
        verbose_name='избранные',
    )

    class Meta:
        verbose_name = 'избранный'
        verbose_name_plural = 'избранные'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_for_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name} - {self.user}'


class RecipesCart(models.Model):
    """ Список покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listingredientuser',
        verbose_name='юзер'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='listrecipe',
        verbose_name='рецепт'
    )

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'корзины'

    def __str__(self):
        return f'{self.recipe.name} - {self.user}'
