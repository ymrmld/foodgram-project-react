from django.contrib.auth.models import AbstractUser

from django.db import models

LIMIT_SYMBOL_NAME = 15


class User(AbstractUser):
    """ Модель для юзера."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    username = models.CharField(
        max_length=150,
        unique=True
    )
    first_name = models.CharField(
        max_length=150
    )
    last_name = models.CharField(
        max_length=150
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'юзер'
        verbose_name_plural = 'юзеры'

    def __str__(self):
        return self.username[:LIMIT_SYMBOL_NAME]


class Subscribe(models.Model):
    """ Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='подписка'
    )

    class Meta:
        models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_follow'
        )
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return f'{self.user} - {self.author}.'
