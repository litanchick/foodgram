import base64

from django.core.files.base import ContentFile
from rest_framework.generics import get_object_or_404
from rest_framework import serializers

from .models import (
    Ingredients, Recipes, Tags, Units,
    ListFavorite, ListIngredients, DownloadListIngredients
)
from users.models import User, ListSubscriptions


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для юзера."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ListSubscriptions.objects.filter(
            author=user, subscription_on=obj
        ).exists()


class UserAvatarSerializer(UserSerializer):
    """Сериализатор для аватара юзера."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        fields = ('id', 'name', 'slug')
        model = Tags
        lookup_field = 'id'


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredients
        lookup_field = 'id'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['measurement_unit'] = f'{instance.measurement_unit.name}'
        return data


class ListIngredientsSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField(source='ingredient.id')
    # name = serializers.ReadOnlyField(
    #     source='ingredient.name'
    # )
    # measurement_unit = serializers.ReadOnlyField(
    #     source='ingredient.measurement_unit.name'
    # )
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit.name')
    amount = serializers.PrimaryKeyRelatedField(
        queryset=ListIngredients.objects.all()
    )

    class Meta:
        model = ListIngredients
        fields = ('id', 'measurement_unit', 'amount', 'name')

    # def get_measurement_unit(self, data):
    #     ingredient = Ingredients.objects.get(id=data.ingredient.id)

    #     return data


# class IngredientsForRecipesSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())

#     class Meta:
#         model = ListIngredients
#         fields = ('id', 'amount')


class RecipesSerializerGet(serializers.ModelSerializer):
    """Класс сериализаторов рецептов для метода GET."""
    tags = TagsSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = ListIngredientsSerializer(
        many=True, source='recipeingredient'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, data):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user_id = data.author
        recipe_id = data.id
        if ListFavorite.objects.filter(
            user=user_id,
            recipe_id=recipe_id
        ).exists():
            return False
        return True

    def get_is_in_shopping_cart(self, data):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user_id = data.author
        recipe_id = data.id
        if DownloadListIngredients.objects.filter(
            user=user_id,
            recipe_id=recipe_id
        ).exists():
            return False
        return True


class RecipesSerializer(serializers.ModelSerializer):
    """Класс сериализаторов рецептов."""

    image = Base64ImageField()
    ingredients = serializers.ListField(
        child=serializers.DictField(), allow_empty=False, write_only=True
    )
    tags = serializers.SlugRelatedField(
        slug_field='id', queryset=Tags.objects.all(), many=True
    )

    class Meta:
        model = Recipes
        fields = (
            'id', 'image', 'name', 'text', 'cooking_time',
            'ingredients', 'tags',
        )

    def to_representation(self, instance):
        return RecipesSerializerGet(instance, context=self.context).data

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['is_favorited'] = self.get_is_favorited(data)
    #     return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context['request'].user
        recipe = Recipes.objects.create(author=user, **validated_data)
        for ingredient in ingredients:
            ListIngredients.objects.get_or_create(
                ingredient_id=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            )
        recipe.tags.set(tags)
        return recipe


class DowmloadListIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для сохранения рецепта в список покупок."""

    name = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Recipes.objects.all(),
    )
    image = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Recipes.objects.all(),
    )
    cooking_time = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Recipes.objects.all(),
    )

    class Meta:
        fields = ('id', 'amount')
        model = ListIngredients

    def create(self, validated_data):
        if ListIngredients.objects.filter(
            user=self.context['request'].user,
            recipe=get_object_or_404(Recipes, pk=validated_data['recipe_id']),
        ).exists():
            raise serializers.ValidationError(
                'Вы уже добавили рецепт в список покупок.'
            )

        return ListIngredients.objects.create(**validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для списка Избранного."""

    def create(self, validated_data):
        if ListFavorite.objects.filter(
            user=self.context['request'].user,
            recipe=get_object_or_404(Recipes, pk=validated_data['recipe_id'])
        ).exists():
            raise serializers.ValidationError(
                'Вы уже добавили в избранное этот рецепт.'
            )

        return ListFavorite.objects.create(**validated_data)

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipes


class ListSubscriptionsSerialaizer(serializers.ModelSerializer):
    """Сериализатор произведений."""

    resipes = RecipesSerializer()
    recipes_count = serializers.ModelField('get_recipes_count', read_only=True)
    is_subscribed = serializers.ModelField('get_subscribed', read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'resipes',
            'recipes_count',
            'avatar',
        )

    def get_recipes_count(self, data):
        return Recipes.objects.filter(name=data.get('username')).count

    def get_subscribed(self, data, instance):
        username = data.get('username')
        subscribe = instance.user.username
        if ListSubscriptions.objects.filter(
            author=username,
            subscription_on=subscribe
        ).exists():
            return False
        return True
