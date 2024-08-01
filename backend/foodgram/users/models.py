from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.validators import RegexValidator, validate_email
from django.db import models

from .constans import CHAR_MAX_LENGTH, EMAIL_MAX_LENGTH


class UserManager(BaseUserManager):
    """Кастомный менеджер создания пользователя."""

    use_in_migrations = True

    def _create_user(
            self, email, username,
            first_name, last_name,
            password
    ):
        """Переопределение создания пользователя."""
        if not email:
            raise ValueError('Почта - обязательное поле для регистрации.')
        if not username:
            raise ValueError('Username - обязательное поле для регистрации.')
        if not first_name:
            raise ValueError('Имя - обязательное поле для регистрации.')
        if not last_name:
            raise ValueError('Фамилия - обязательное поле для регистрации.')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(
            email=email, username=username, first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
            self, email, username,
            first_name, last_name,
            password=None
    ):
        return self._create_user(
            email, username, first_name, last_name, password
        )

    def create_superuser(
            self, email, username,
            first_name, last_name,
            password, **extra_fields
    ):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(
            email, username, first_name, last_name, password, **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        'Адрес электронной почты',
        validators=[validate_email],
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
    )
    first_name = models.CharField(
        max_length=CHAR_MAX_LENGTH,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=CHAR_MAX_LENGTH,
        verbose_name='Фамилия',
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
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


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
