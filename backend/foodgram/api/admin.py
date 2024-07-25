from django.contrib import admin

from .models import (
    Ingredients, Recipes, Tags, Units, User,
    DownloadListIngredients, ListFavorite, ListIngredients,
)


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Units)
class UnitsAdmin(admin.ModelAdmin):
    pass


@admin.register(ListFavorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')


class ListIngredientsInLine(admin.TabularInline):
    model = ListIngredients
    extra = 1


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'text',
        'author', 'cooking_time', 'image',
        'display_tags', 'display_ingredients',
    )
    search_fields = ('name', 'tags', 'author', 'cooking_time')
    list_filter = ('name', 'tags', 'author', 'cooking_time')
    inlines = [
        ListIngredientsInLine,
    ]

    def display_tags(self, obj):
        return ', '.join([str(item) for item in obj.tags.all()])

    def display_ingredients(self, obj):
        return ', '.join([str(item) for item in obj.ingredients.all()])

    display_tags.short_description = 'Теги'
    display_ingredients.short_description = 'Ингредиенты'


@admin.register(ListIngredients)
class ListIngredientsAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient')
    list_filter = ('recipe', 'ingredient')


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(DownloadListIngredients)
class DownloadIngredientsAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name')
    search_fields = ('email', 'username')
