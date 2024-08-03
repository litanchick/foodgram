from django_filters.rest_framework import FilterSet, filters

from .models import Ingredients, Recipes, Tags


class NameFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredients
        fields = ['name',]


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug', to_field_name='slug',
        lookup_expr='istartswith',
        queryset=Tags.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = ['tags', 'author']

    def filter_is_favorited(self, queryset, name, values):
        user = self.request.user
        if values and not user.is_anonymous:
            return queryset.filter(recipe_favorite__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, values):
        user = self.request.user
        if values and not user.is_anonymous:
            return queryset.filter(recipe_download__user_id=user.id)
        return queryset
