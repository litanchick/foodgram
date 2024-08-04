import pandas as pd
from django.http import HttpResponse
from django.shortcuts import get_list_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import ListSubscriptions

from foodgram.settings import ALLOWED_HOSTS

from .filtres import NameFilter, RecipeFilter
from .models import (Ingredients, ListFavorite, ListIngredients, Recipes,
                     ShoppingCartIngredients, Tags, User)
from .pagination import LimitNumber, PaginationNumber
from .permissions import RecipePermissions
from .serializers import (FavoriteSerializer, IngredientsSerializer,
                          ListSubscriptionsSerialaizer,
                          ListSubscriptionsSerialaizerGet, RecipesSerializer,
                          RecipesSerializerGet,
                          ShoppingCartIngredientsSerializer, TagsSerializer,
                          UserAvatarSerializer, UserSerializer)


class CustomUsersViewSet(viewsets.GenericViewSet):
    """Управление пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

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
        serializer_class=ListSubscriptionsSerialaizer,
        pagination_class=PaginationNumber
    )
    def subscribe(self, request, pk=None):
        author = request.user
        subscription_on = get_object_or_404(User, id=pk)
        sibscribe = ListSubscriptions.objects.filter(
            author=author.id,
            subscription_on=subscription_on.id
        )
        if request.method == 'POST':
            serializer = ListSubscriptionsSerialaizer(
                data={
                    'author': author.id,
                    'subscription_on': subscription_on.id
                }, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if sibscribe.exists():
            sibscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
        pagination_class=PaginationNumber,
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscription_on__author=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = ListSubscriptionsSerialaizerGet(
            pages, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс получения тегов."""

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс получения списка и отдельного ингредиента."""

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filterset_class = NameFilter
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Управление рецептами."""

    queryset = Recipes.objects.all()
    pagination_class = [PaginationNumber, LimitNumber]
    filterset_class = RecipeFilter
    permission_classes = [RecipePermissions]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipesSerializerGet
        return RecipesSerializer

    @action(
        detail=False,
        methods=['GET'],
        pagination_class=None,
    )
    def download_shopping_cart(self, request):
        list_recipes = get_list_or_404(
            ShoppingCartIngredients, user=request.user.id
        )
        col = ['Ингредиенты', 'Единица измерения', 'Количество']
        table_ingredients = pd.DataFrame(columns=col)

        for shopping_cart in list_recipes:
            ingredients_recipe = list(
                ListIngredients.objects.filter(
                    recipe_id=shopping_cart.recipe.id
                ).values()
            )
            temp_pd = pd.DataFrame(columns=col)

            for ingredients in ingredients_recipe:
                ingredient_id = ingredients['ingredient_id']
                ingredient = Ingredients.objects.get(id=ingredient_id)
                new_row = {
                    'Ингредиенты': ingredient.name,
                    'Единица измерения': ingredient.measurement_unit,
                    'Количество': ingredients['amount']
                }
                temp_pd = pd.concat(
                    [temp_pd, pd.DataFrame([new_row])], ignore_index=True
                )
            table_ingredients = pd.concat(
                [table_ingredients, temp_pd], ignore_index=True
            )
        data_frame = table_ingredients.groupby(
            ['Ингредиенты', 'Единица измерения'], as_index=False
        ).sum()
        content = "Ингредиенты\tЕдиница измерения\tКоличество\n"
        for index, row in data_frame.iterrows():
            content += (
                f"{row['Ингредиенты']}\t "
                f"{row['Единица измерения']}\t{row['Количество']}\n"
            )
        return HttpResponse(content, content_type='text/plain')

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated,],
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipes, id=pk)
        user = get_object_or_404(User, id=request.user.id)
        shopping_cart = ShoppingCartIngredients.objects.filter(
            user=user.id,
            recipe=recipe
        )
        if request.method == 'POST':
            serializer = ShoppingCartIngredientsSerializer(
                data={'user': user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if shopping_cart.exists():
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated,],
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipes, id=pk)
        user = get_object_or_404(User, id=request.user.id)
        shopping_cart = ListFavorite.objects.filter(
            user=user.id,
            recipe=recipe
        )
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if shopping_cart.exists():
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['GET'],
        url_name='get_link',
        url_path='get-link',
    )
    def get_link(self, request, pk):
        get_object_or_404(Recipes, id=pk)
        return Response(
            {'short-link': f'https://{ALLOWED_HOSTS[0]}/api/recipes/{pk}/'},
            status=status.HTTP_200_OK
        )
