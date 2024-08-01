from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from users.models import User

from .constants import (INGREDIENTS_LIMIT_LENGHT, MEASUREMENT_UNIT_LENGHT,
                        SMALL_LIMIT_LENGHT, TEXT_LIMIT_LENGHT)


class Tags(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=SMALL_LIMIT_LENGHT,
    )
    slug = models.CharField(
        'Уникальный идентификатор тега',
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Формат данных не соответствует допустимым символам.')
        ],
        max_length=SMALL_LIMIT_LENGHT,
        unique=True,
    )

    class Meta():
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Units(models.Model):
    name = models.CharField(
        'Название еденицы измерения',
        max_length=SMALL_LIMIT_LENGHT,
    )

    class Meta():
        verbose_name = 'Еденица измерения'
        verbose_name_plural = 'Еденицы измерения'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=INGREDIENTS_LIMIT_LENGHT,
        unique=True
    )
    measurement_unit = models.ForeignKey(
        Units,
        verbose_name='Еденица измерения',
        on_delete=models.CASCADE,
        max_length=MEASUREMENT_UNIT_LENGHT,
        related_name='unitingredient'
    )

    class Meta():
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipes(models.Model):
    ingredients = models.ManyToManyField(
        Ingredients,
        through='ListIngredients',
        verbose_name='Список ингредиентов',
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Список тегов',
        related_name='tagspecipes'
    )
    image = models.ImageField(
        'Фото рецепта',
        upload_to='recipes/images/',
        null=True,
        default=None,
    )
    name = models.CharField(
        'Название рецепта',
        max_length=TEXT_LIMIT_LENGHT,
    )
    text = models.TextField(
        'Описание рецепта',
    )
    cooking_time = models.IntegerField(
        'Время приготоваления (мин)',
        validators=[MinValueValidator(
            1,
            message='Время приготовления не может быть меньше 1 минуты.'
        )]
    )
    author = models.ForeignKey(
        User,
        related_name='user',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta():
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('pub_date',)

    def __str__(self):
        return self.name


class ListFavorite(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в избранном',
        related_name='recipe_favorite',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )

    class Meta():
        verbose_name = 'Избранное'
        verbose_name_plural = 'Список избранного'


class ListIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipeingredient'
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipeingredient',
    )
    amount = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(
            1,
            message='Количество не может быть меньше 1-го.'
        )]
    )

    class Meta():
        verbose_name = 'Список ингредиентов'
        verbose_name_plural = 'Списки ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_recipe',
            )
        ]


class ShoppingCartIngredients(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_download',
    )

    class Meta():
        verbose_name = 'Добавлен в список покупок'
        verbose_name_plural = 'Добавленые в списки покупок'
