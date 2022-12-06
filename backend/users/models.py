from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    user = 'user'
    moderator = 'moderator'
    admin = 'admin'

    ROLES = (
        (user, user),
        (moderator, moderator),
        (admin, admin),
    )

    username = models.CharField(
        max_length=25,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        max_length=50,
        unique=True,
        verbose_name='Почта'
    )
    role = models.CharField(
        max_length=30,
        blank=True,
        choices=ROLES,
        default='user',
        verbose_name='Роль пользователя'
    )

    first_name = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Имя'
    )

    last_name = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Фамилия'
    )

    @property
    def is_user(self):
        return self.role == self.user

    @property
    def is_moderator(self):
        return self.role == self.moderator

    @property
    def is_admin(self):
        return self.role == self.admin or self.is_superuser

    class Meta:
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        db_index=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        db_index=False
    )

    class Meta:
        ordering = ['-id']
        models.UniqueConstraint(
            fields=['user', 'author', ],
            name='user_and_author_uniq'
        )
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
