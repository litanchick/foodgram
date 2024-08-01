from django_filters.rest_framework import FilterSet, filters
from .models import Ingredients, Recipes, Tags


class NameFilter(FilterSet):
    filter = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredients
        fields = ['name',]


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug', to_field_name='slug',
        lookup_expr='istartswith',
        queryset=Tags.objects.all()
    )

    class Meta:
        model = Recipes
        fields = ['tags', 'author']
