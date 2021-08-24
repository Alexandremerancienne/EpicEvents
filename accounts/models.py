from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE = (
        ("management", "Management"),
        ("sales", "Sales"),
        ("support", "Support"),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE,
        blank=True,
        help_text="Role (Management, Sales, Support)",
    )
    is_staff = models.BooleanField(default=True)
