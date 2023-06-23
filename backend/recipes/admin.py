from django.contrib import admin
from django.contrib.admin import TabularInline, display

from .models import (Ingredient, IngredientToRecipe, Recipe, RecipesCart,
                     RecipeToTag, SelectedRecipe, Tag)

admin.site.site_header = 'foodgram'


class IngredientToRecipeInline(TabularInline):
    model = IngredientToRecipe
    extra = 1


class TagToRecipeInline(admin.StackedInline):
    model = RecipeToTag
    extra = 1


class SelectedAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    empty_value_display = '-пусто-'


class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name', )
    empty_value_display = '-пусто-'


class RecipesAdmin(admin.ModelAdmin):
    inlines = [IngredientToRecipeInline, TagToRecipeInline]
    list_display = (
        'name',
        'author',
        'selected_amount'
    )
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'

    @display(description='в избранном!')
    def selected_amount(self, obj):
        return obj.recipe.count()


class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    empty_value_display = '-пусто-'


class IngredientToRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    empty_value_display = '-пусто-'


class TagToRecipesAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'tag',
    )
    empty_value_display = '-пусто-'


class RecipesCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagsAdmin)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(Recipe, RecipesAdmin)
admin.site.register(IngredientToRecipe, IngredientToRecipeAdmin)
admin.site.register(RecipeToTag, TagToRecipesAdmin)
admin.site.register(SelectedRecipe, SelectedAdmin)
admin.site.register(RecipesCart, RecipesCartAdmin)
