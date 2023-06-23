from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
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
        unique=True
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='ссылка'
    )

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
        max_length=100,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения ингредиента',
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
        null=True,
    )
    name = models.CharField(
        verbose_name='название шедевра',
        max_length=100,
    )
    image = models.ImageField(
        verbose_name='как выглядит блюдо',
        upload_to='recipes/images/',
        blank=True,
        help_text='добавьте фото шедевра',
    )
    text = models.TextField(
        verbose_name='описание приготовления блюда',
        max_length=1024,
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
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                message='приготовление не может занимать менее 1 минуты'
            )
        ],
        default=0
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
        validators=(MinValueValidator(
            1, message='ингридиентов не может быть меньше 1'
        ),),
        verbose_name='количество ингридиентов'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'связь ингридиента с рецептом'
        verbose_name_plural = 'связи ингридиентов и рецептов'

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


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
        ordering = ['-id']
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
        verbose_name='рецепт')

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'корзины'
