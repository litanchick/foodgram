from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import ListSubscriptions, User

from .models import (Ingredients, ListFavorite, ListIngredients, Recipes,
                     ShoppingCartIngredients, Tags)


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
        user = self.context.get('request')
        if not user or user.user.is_anonymous:
            return False
        return ListSubscriptions.objects.filter(
            author=user.user, subscription_on=obj
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
    """Класс сериалайзер, который принимает информации по рецептам."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit.name'
    )
    amount = serializers.PrimaryKeyRelatedField(
        queryset=ListIngredients.objects.all()
    )

    class Meta:
        model = ListIngredients
        fields = ('id', 'measurement_unit', 'amount', 'name')


class RecipesSerializerGet(serializers.ModelSerializer):
    """Класс сериализаторов рецептов для метода GET."""

    tags = TagsSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = ListIngredientsSerializer(
        many=True, source='recipeingredient'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.CharField()

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
        return ListFavorite.objects.filter(
            user=request.user,
            recipe_id=data.id
        ).exists()

    def get_is_in_shopping_cart(self, data):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCartIngredients.objects.filter(
            user=request.user,
            recipe_id=data.id
        ).exists()


class RecipesSerializer(serializers.ModelSerializer):
    """Класс сериализаторов рецептов."""

    image = Base64ImageField()
    ingredients = serializers.ListField(
        child=serializers.DictField(), allow_empty=False, write_only=True
    )
    tags = serializers.SlugRelatedField(
        slug_field='id', queryset=Tags.objects.all(), many=True, required=True
    )

    class Meta:
        model = Recipes
        fields = (
            'id', 'image', 'name', 'text', 'cooking_time',
            'ingredients', 'tags',
        )
        extra_kwargs = {'image': {'required': True}}

    def to_representation(self, instance):
        return RecipesSerializerGet(instance, context=self.context).data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(
            author=self.context['request'].user, **validated_data
        )
        for ingredient in ingredients:
            ListIngredients.objects.get_or_create(
                ingredient_id=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().update(instance, validated_data)
        if ingredients:
            recipe.ingredients.clear()
            for ingredient in ingredients:
                ListIngredients.objects.create(
                    ingredient_id=ingredient['id'],
                    recipe=recipe,
                    amount=ingredient['amount']
                )
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        return recipe

    def validate(self, value):
        if not value.get('image'):
            raise serializers.ValidationError(
                'Не забудьте прикрепить фотографию.'
            )
        tags = value.get('tags')
        ingredients = value.get('ingredients')
        if not tags:
            raise serializers.ValidationError(
                'Вы не указали теги в рецепте.'
            )
        if not ingredients:
            raise serializers.ValidationError(
                'Пустой список ингредиентов.'
            )
        if int(ingredients[0]['amount']) < 1:
            raise serializers.ValidationError(
                'Количество не может быть меньше 1-го.'
            )
        if not Ingredients.objects.filter(
            id=ingredients[0]['id']
        ).exists():
            raise serializers.ValidationError(
                'Такого ингредиента нет в базе.'
            )
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                'Нельзя добавлять одинаковые теги в рецепт.'
            )
        list_id_ingredients = [ingredient['id'] for ingredient in ingredients]
        if len(list_id_ingredients) != len(set(list_id_ingredients)):
            raise serializers.ValidationError(
                'Нельзя добавлять одинаковые ингредиенты в рецепт.'
            )
        return value


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Класс сериалайзер для вывода сокращенной информации по рецептам."""

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для сохранения рецепта в список покупок."""

    class Meta:
        fields = ('user', 'recipe')
        model = ShoppingCartIngredients
        validators = (
            UniqueTogetherValidator(
                queryset=ShoppingCartIngredients.objects.all(),
                fields=('user', 'recipe')
            ),
        )

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для списка Избранного."""

    class Meta:
        fields = ('user', 'recipe')
        model = ListFavorite
        validators = (
            UniqueTogetherValidator(
                queryset=ListFavorite.objects.all(),
                fields=('user', 'recipe')
            ),
        )

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context={'request': self.context.get('request')}
        ).data


class ListSubscriptionsSerialaizerGet(UserSerializer):
    """Сериализатор получения подписок."""

    recipes = serializers.SerializerMethodField(
        'get_recipes', read_only=True
    )
    recipes_count = serializers.SerializerMethodField(
        'get_recipes_count', read_only=True
    )

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email', 'username', 'first_name',
            'last_name', 'avatar'
        )

    def get_recipes_count(self, data):
        return data.user.count()

    def get_recipes(self, data):
        request = self.context.get('request')
        recipes = data.user.all()
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data


class ListSubscriptionsSerialaizer(serializers.ModelSerializer):
    """Сериализатор создания подписок."""

    class Meta:
        fields = ('author', 'subscription_on')
        model = ListSubscriptions
        validators = (
            UniqueTogetherValidator(
                queryset=ListSubscriptions.objects.all(),
                fields=('author', 'subscription_on')
            ),
        )

    def validate(self, validated_data):
        if validated_data['author'] == validated_data['subscription_on']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        return validated_data

    def to_representation(self, instance):
        return ListSubscriptionsSerialaizerGet(
            instance.subscription_on,
            context={'request': self.context.get('request')}
        ).data


class DownloadShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для возможности скачивания списка покупок."""

    shopping_cart = serializers.FileField()

    class Meta:
        fields = ('user', 'recipe', 'shopping_cart')
        model = ShoppingCartIngredients
