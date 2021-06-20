from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Singer)
class SingerAdmin(admin.ModelAdmin):
    pass


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    pass


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    pass


@admin.register(TextBlockClass)
class TextBlockClassAdmin(admin.ModelAdmin):
    pass


@admin.register(TextBlock)
class TextBlockAdmin(admin.ModelAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass