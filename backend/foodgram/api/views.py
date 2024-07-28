from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from django.shortcuts import get_list_or_404
from django.http import HttpResponse
from rest_framework.viewsets import generics
import pandas as pd
from djoser.views import UserViewSet
from djoser.conf import settings
from rest_framework.pagination import LimitOffsetPagination
from .filtres import NameFilter
from django_filters import rest_framework


from .serializers import (
    TagsSerializer,
    IngredientsSerializer,
    FavoriteSerializer,
    RecipesSerializer,
    ListSubscriptionsSerialaizer,
    ListIngredientsSerializer,
    DowmloadListIngredientsSerializer,
    UserAvatarSerializer,
    UserSerializer,
    RecipesSerializerGet,
)
from .models import (
    User, Tags, Ingredients, ListFavorite, Recipes, Units,
    ListIngredients, DownloadListIngredients
)
from users.models import ListSubscriptions
from .pagination import PaginationNumber


class CustomUsersViewSet(viewsets.GenericViewSet):
    """Управление пользователями."""

    # permission_classes = [AllowAny,]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'user'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    # pagination_class = PaginationNumber

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_path='me'
    )
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user, context={"request": request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['PUT', 'DELETE'],
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar',
        serializer_class=UserAvatarSerializer,
    )
    def avatar(self, request):
        if request.method == 'PUT':
            if request.data:
                serializer = self.get_serializer(
                    request.user,
                    data=request.data,
                    partial=True,
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            self.request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
        serializer_class=[ListSubscriptionsSerialaizer,]
    )
    def subscribe(self, request):
        serializer = self.get_serializer(
            request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
        serializer_class=[ListSubscriptionsSerialaizer,],
        pagination_class=[PaginationNumber,]
    )
    def subscriptions(self):
        return ListSubscriptions.objects.filter(author=self.request.user)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс получения тегов."""

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс получения списка и отдельного ингредиента."""

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    # filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = NameFilter
    pagination_class = None

    # def create(self, request):
    #     measurement_unit = request.data['measurement_unit']
    #     unit = Units.objects.get(name=measurement_unit)
    #     Ingredients.objects.create(name=request, measurement_unit=unit)
    #     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RecipesViewSet(viewsets.ModelViewSet):
    """Управление рецептами."""

    queryset = Recipes.objects.all()
    # serializer_class = RecipesSerializer
    pagination_class = PaginationNumber
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ['tags', 'is_favorite', 'is_in_shopping_cart', 'author']

    # def get_queryset(self):
    #     review_queryset = get_object_or_404(
    #         Recipes, id=self.kwargs.get('recipe_id')
    #     )
    #     return review_queryset

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user.id)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipesSerializerGet
        return RecipesSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated,],
        serializer_class=[DowmloadListIngredientsSerializer,],
        pagination_class=None,
    )
    def download_shopping_cart(self):
        username = User.objects.get(user=self.kwargs.get('username'))
        list_recipes = get_list_or_404(DownloadListIngredients, user=username)
        download_file = 'listingredients.csv'
        col = ['Ингредиенты', 'Единица измерения', 'Количество']
        table_ingredients = pd.DataFrame(columns=col)
        for recipe_id in list_recipes:
            ingredients_recipe = list(
                ListIngredients.objects.filter(
                    recipe_id=recipe_id['recipe_id']
                ).values()
            )
            for ingredients, number_row in enumerate(ingredients_recipe):
                ingredient_id = ingredients['ingredient_id']
                ingredient = Ingredients.objects.get(id=ingredient_id)
                measurement_unit_name = Units.objects.get(
                    id=ingredient.measurement_unit
                )
                table_ingredients.at[
                    number_row, 'Ингредиенты'
                ] = ingredient.name
                table_ingredients.at[
                    number_row, 'Единица измерения'
                ] = measurement_unit_name
                table_ingredients.at[
                    number_row, 'Количество'
                ] = ingredients['amount']

        data_frame = pd.pivot_table(table_ingredients, index=['ingredient'])
        return data_frame.to_csv(download_file)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated,],
        serializer_class=[ListIngredientsSerializer,],
    )
    def shopping_cart(self, serializer):
        get_list_or_404(Recipes, id=self.kwargs.get('recipe_id'))
        list_ingredients = ListIngredients.objects.filter(
            recipe_id=self.kwargs.get('recipe_id')
        )
        for i in range(len(list_ingredients)):
            if self.http_method_names == 'post':
                serializer.save(
                    user=self.request.user,
                    recipe_id=self.kwargs.get('recipe_id'),
                )
            else:
                return ListIngredients.objects.get_queryset(
                    user=self.request.user.id,
                    recipe_id=self.kwargs.get('recipe_id')
                )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated,],
        serializer_class=[FavoriteSerializer,],
    )
    def favorite(self, serializer):
        get_object_or_404(User, id=self.kwargs.get('user_id'))
        if self.http_method_names == 'post':
            serializer.save(
                user=self.request.user.id,
                recipe_id=self.kwargs.get('recipe_id')
            )
        else:
            return ListFavorite.objects.get(
                user=self.request.user.id,
                recipe_id=self.kwargs.get('recipe_id')
            )

    @action(
        detail=True,
        methods=['get'],
        url_name='get-link',
        url_path='get_link',
    )
    def get_link(self):
        recipe = get_object_or_404(Recipes, id=self.kwargs.get('recipe_id'))
        localhost = '123'
        return f'https://{localhost}/{recipe.slug}/'
