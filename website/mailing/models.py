from django.db import models
from django.utils import timezone


class Subscribe(models.Model):
    email = models.EmailField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email