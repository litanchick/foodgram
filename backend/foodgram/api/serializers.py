import base64

from django.core.files.base import ContentFile
from rest_framework.generics import get_object_or_404
from rest_framework import serializers
from django.utils.text import slugify

from .models import Ingredients, ListFavorite, ListIngredients, Recipes, Tags
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

    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class TagsSerializer(serializers.Serializer):
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


class RecipesSerializer(serializers.ModelSerializer):
    """Класс сериализаторов рецептов."""

    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.ModelField('get_is_favorited')
    is_in_shopping_cart = serializers.ModelField('get_is_in_shopping_cart')
    ingredients = IngredientsSerializer()
    author = UserSerializer()
    tags = TagsSerializer()
    slug = serializers.ModelField('get_slug')

    class Meta:
        model = Recipes
        fields = (
            'id', 'image', 'name', 'user', 'text', 'cooking_time',
            'is_in_shopping_cart', 'is_favorited',
            'ingredients', 'author', 'tags',
        )

    def get_is_favorited(self, data):
        username = data.get('username')
        recipe_id = data.get('recipe_id')
        if ListFavorite.objects.filter(
            user=username,
            recipe_id=recipe_id
        ).exists():
            return False
        return True

    def get_is_in_shopping_cart(self, data):
        username = data.get('username')
        recipe_id = data.get('recipe_id')
        if ListIngredients.objects.filter(
            user=username,
            recipe_id=recipe_id
        ).exists():
            return False
        return True

    def get_slug(self, data):
        name_recipe = data.get('name')
        slug_recipe = slugify(name_recipe)
        return slug_recipe


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


class ListIngredientsSerializer(serializers.ModelSerializer):
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
        fields = ('id', 'name', 'image', 'cooking_time')
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
