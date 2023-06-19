from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model() 

class Tag(models.Model):
    name = models.CharField(
        verbose_name='тег',
        max_length=20,
        unique=True
    )
    color = models.CharField(
        'цвет',
        max_length=7,
        unique=True)
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='ссылка'
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'tags'
        ordering = ('-id',)

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(
        verbose_name = 'ингридиент',
        max_length = 100,
        unique = True
    )
    unit_of_measurement = models.CharField(
        verbose_name = 'Единица измерения ингредиента',
        max_length=30
    )
    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ingredients'

    def __str__(self):
        return f'{self.name} - {self.unit_of_measurement}.'

class Recipe(models.Model):
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
        upload_to='images',
    )
    text = models.TextField(
        verbose_name='описание приготовления блюда',
        max_length=1024,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='ингредиенты блюда',
        related_name='ingredients',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='тег',
        related_name='tags',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления',
        default=0,
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
