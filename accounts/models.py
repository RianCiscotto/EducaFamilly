from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    USER_TYPES = (
        ('teacher', 'Professor'),
        ('parent', 'Responsável'),
    )

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPES
    )

    last_seen = models.DateTimeField(
        null=True,
        blank=True
    )