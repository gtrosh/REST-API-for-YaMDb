from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        USER = "user", "user"
        MODER = "moderator", "moderator"
        ADMIN = "admin", "admin"

    email = models.EmailField(_("email address"), unique=True)

    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.USER,
    )

    bio = models.TextField(
        verbose_name="О себе",
        help_text="пара слов о себе, чтобы другим было понятно",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_username(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.Role.MODER

    class Meta:
        ordering = ["-date_joined"]
