from django.contrib import admin
from .models import *
from django.utils.safestring import mark_safe
from django.urls import reverse


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


@admin.register(TextBlock)
class TextBlockAdmin(admin.ModelAdmin):
    readonly_fields = ["image_preview"]

    def image_preview(self, obj):
        return mark_safe(f"<img src='{obj.image.url}' style='max-height: 400px;'>")


class SubdivisionInline(admin.TabularInline):
    model = Subdivision
    extra = 1
    readonly_fields = ["edit_link"]

    def edit_link(self, obj):
        url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.pk])
        if obj.pk:
            return mark_safe(f"<a href='{url}'>изменить</a>")
        else:
            return ""


class TextBlockInline(admin.TabularInline):
    model = TextBlock
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [SubdivisionInline]


@admin.register(Subdivision)
class SubdivisionAdmin(admin.ModelAdmin):
    inlines = [TextBlockInline]


class ImageUnitInline(admin.TabularInline):
    model = ImageUnit
    extra = 1
    readonly_fields = ["image_preview"]
    
    def image_preview(self, obj):
        return mark_safe(f"<img src='{obj.image.url}' style='max-height: 200px;'>")


@admin.register(ImageSlider)
class ImageSliderAdmin(admin.ModelAdmin):
    inlines = [ImageUnitInline]


@admin.register(ImageUnit)
class ImageUnitAdmin(admin.ModelAdmin):
    readonly_fields = ["image_preview"]
    
    def image_preview(self, obj):
        return mark_safe(f"<img src='{obj.image.url}' style='max-height: 400px;'>")