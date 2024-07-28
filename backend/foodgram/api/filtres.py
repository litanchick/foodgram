from django_filters.rest_framework import FilterSet, filters
from .models import Ingredients


class NameFilter(FilterSet):
    filter = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredients
        fields = ['name',]
