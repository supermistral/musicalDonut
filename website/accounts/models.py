from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError(_("Email is required"))

        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError(_('Error due to is_staff'))
        if kwargs.get('is_superuser') is not True:
            raise ValueError(_('Error due to is_superuser'))
        
        return self.create_user(email, password, **kwargs)


class User(AbstractUser):
    email = models.EmailField(_('Email address'), unique=True)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email