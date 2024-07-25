from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import validate_email

from .constans import CHAR_MAX_LENGTH, EMAIL_MAX_LENGTH


class User(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        'Адрес электронной почты',
        validators=[validate_email],
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
    )
    username = models.CharField(
        'Уникальный юзернейм',
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Формат данных не соответствует допустимым символам.'),
        ],
        max_length=CHAR_MAX_LENGTH,
        unique=True,
        help_text='Не более 150 символов. Только буквы, цифры и @/./+/-/_.',
    )
    avatar = models.ImageField(
        blank=True,
        upload_to='users/images/',
        null=True,
        default=None,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class ListSubscriptions(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    subscription_on = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='На кого подписан',
        related_name='subscription_on',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Список подписок'
