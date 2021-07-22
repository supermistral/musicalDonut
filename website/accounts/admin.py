from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ordering = ['email']

    fieldsets = (
        (None, {
            "fields": (
                'email', 'first_name', 'last_name', 'date_joined', 'is_staff'
            ),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'fields': (
                'email', 'first_name', 'last_name'
            ),
        }),
    )