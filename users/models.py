from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class AlfredUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email).lower()
        user = self.model(
            email=email,
            **kwargs,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(
            email,
            password=password,
            **kwargs,
        )
        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)
        return user


class AlfredUser(AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        VOLUNTEER = "volunteer", "Volunteer"
        RAC = "rac", "RAC"
        NGO = "ngo", "NGO"
        UNDEFINED = "undefined", "Undefined"

    email = models.EmailField(unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    user_type = models.CharField(
        max_length=30, choices=UserType.choices, default=UserType.UNDEFINED
    )

    objects = AlfredUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "user_type"]

    def __str__(self):
        return str(self.email)
