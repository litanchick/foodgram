from django.contrib import admin

from .models import (Ingredients, ListFavorite, ListIngredients, Recipes,
                     ShoppingCartIngredients, Tags, Units, User)


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Units)
class UnitsAdmin(admin.ModelAdmin):
    list_display = ('name',)


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
        'display_recipe_favorite',
    )
    search_fields = ('name', 'author__email')
    list_filter = ('tags',)
    inlines = [
        ListIngredientsInLine,
    ]

    def display_recipe_favorite(self, obj):
        count = ListFavorite.objects.filter(recipe=obj).count()
        return count

    def display_tags(self, obj):
        return ', '.join([str(item) for item in obj.tags.all()])

    def display_ingredients(self, obj):
        return ', '.join([str(item) for item in obj.ingredients.all()])

    display_tags.short_description = 'Теги'
    display_ingredients.short_description = 'Ингредиенты'
    display_recipe_favorite.short_description = (
        'Количесво добавлений в избранное'
    )


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


@admin.register(ShoppingCartIngredients)
class ShoppingCartIngredientsAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name')
    search_fields = ('email', 'username')
