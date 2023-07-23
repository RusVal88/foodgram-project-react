from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from api.validators import validate_username, validate_name
from foodgram_backend.settings import (EMAIL_MAX_LENGTH,
                                       FIRST_LAST_NAME_AND_USERNAME_MAX_LENGTH)


class User(AbstractUser):
    """Создание таблицы пользователя."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        help_text='Укажите адрес электронной почты!',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Логин пользователя',
        help_text='Укажите логин!',
        max_length=FIRST_LAST_NAME_AND_USERNAME_MAX_LENGTH,
        unique=True,
        validators=[validate_username, UnicodeUsernameValidator()],
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        help_text='Укажите имя!',
        max_length=FIRST_LAST_NAME_AND_USERNAME_MAX_LENGTH,
        validators=[validate_name],
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        help_text='Укажите фамилию!',
        max_length=FIRST_LAST_NAME_AND_USERNAME_MAX_LENGTH,
        validators=[validate_name],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_user',),
        ]
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    """Создание таблицы подписок пользователей."""
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='subscriber',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецептов',
        on_delete=models.CASCADE,
        related_name='author',
    )

    class Meta:
        constraints = [
            (models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscriber')),
            (models.CheckConstraint(
                name='restriction_of_author_your_self', check=~models.Q(
                    user=models.F('author')))),
        ]
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
