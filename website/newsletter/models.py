from django.db import models


class NewsletterSubscribedUsers(models.Model):
    email = models.CharField(unique=True, max_length=50)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_created = models.DateField(null=False, blank=True, auto_now_add=True)

    def __str__(self):
        return self.email