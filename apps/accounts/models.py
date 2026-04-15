from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        WAITER = "WAITER", "Garson"
        CUSTOMER = "CUSTOMER", "Müşteri"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)

    def save(self, *args, **kwargs):
        # Django admin/staff compatibility:
        # - ADMIN users are staff+superuser by default
        # - WAITER users are staff by default
        if self.role == self.Role.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif self.role == self.Role.WAITER:
            self.is_staff = True
            self.is_superuser = False
        super().save(*args, **kwargs)

