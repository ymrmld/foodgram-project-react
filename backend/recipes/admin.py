from django.contrib import admin
from django.contrib.admin import TabularInline
from .models import Recipe, IngredientToRecipe, Ingredient, Tag

admin.site.site_header = 'foodgram'

class IngredientInline(TabularInline):
    model = IngredientToRecipe
    autocomplete_fields = ('ingredient',)
    extra = 2

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'cooking_time',)
    search_fields = ('name', 'author', 'tags',)
    list_filter = ('author', 'name', 'tags',)
    empty_value_display = '-пусто-'
    inlines = (IngredientInline,)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    list_display_links = ('name',)
    search_fields = ('name', 'color',)
    empty_value_display = '-пусто-'
