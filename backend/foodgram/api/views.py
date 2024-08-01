from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from django.shortcuts import get_list_or_404
import pandas as pd
from .filtres import NameFilter, RecipeFilter
from foodgram.settings import ALLOWED_HOSTS
from .permissions import RecipePermissions


from .serializers import (
    TagsSerializer,
    IngredientsSerializer,
    FavoriteSerializer,
    RecipesSerializer,
    ListSubscriptionsSerialaizer,
    UserAvatarSerializer,
    UserSerializer,
    RecipesSerializerGet,
    ShoppingCartIngredientsSerializer,
    DownloadShoppingCartSerializer,
)
from .models import (
    User, Tags, Ingredients, ListFavorite, Recipes, Units,
    ListIngredients, ShoppingCartIngredients
)
from users.models import ListSubscriptions
from .pagination import PaginationNumber


class CustomUsersViewSet(viewsets.GenericViewSet):
    """Управление пользователями."""

    # permission_classes = [AllowAny,]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # lookup_field = 'author'
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
        serializer_class=ListSubscriptionsSerialaizer,
        pagination_class=PaginationNumber
    )
    def subscribe(self, request, pk=None):
        user = get_object_or_404(User, id=request.user.id)
        subscription_on = get_object_or_404(User, id=pk)
        sibscribe = ListSubscriptions.objects.filter(
            author=user.id,
            subscription_on=subscription_on.id
        )
        if request.method == 'POST':
            serializer = ListSubscriptionsSerialaizer(
                data={
                    'author': user.id,
                    'subscription_on': subscription_on.id
                }
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
        serializer_class=ListSubscriptionsSerialaizer,
        pagination_class=PaginationNumber,
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
    pagination_class = PaginationNumber
    filterset_class = RecipeFilter
    permission_classes = [RecipePermissions]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipesSerializerGet
        return RecipesSerializer

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated,],
        serializer_class=DownloadShoppingCartSerializer,
        pagination_class=None,
    )
    def download_shopping_cart(self, request):
        username = User.objects.get(user=self.kwargs.get('username'))
        list_recipes = get_list_or_404(ShoppingCartIngredients, user=username)
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
        return Response(
            data_frame.to_csv(download_file), status=status.HTTP_200_OK
        )

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
