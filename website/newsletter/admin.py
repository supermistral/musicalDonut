from django.contrib import admin
from .models import *


@admin.register(NewsletterSubscribedUsers)
class NewsletterSubscribedUsersAdmin(admin.ModelAdmin):
    pass