from django.contrib import admin
from .models import *
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db import models
from django.forms import Textarea


@admin.register(Singer)
class SingerAdmin(admin.ModelAdmin):
    pass


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    ordering = ['name']


@admin.register(SongSingerRelation)
class SongSingerRelationAdmin(admin.ModelAdmin):
    ordering = ['singer__name', 'song__name']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    pass


@admin.register(TextBlock)
class TextBlockAdmin(admin.ModelAdmin):
    readonly_fields = ["slider_preview"]
    list_display = ['subdivision', 'format_text']

    def slider_preview(self, obj):
        # images = obj.slider.images.all() if obj.slider else None
        # if images is None or not images.exists():
        #     return None
        # images_html = "".join([f"<img src='{item.image.url}' style='max-height: 400px;display: block;'>" for item in images])
        # return mark_safe(f"<div>{images_html}</div>")
        slider = obj.slider
        url = reverse(f'admin:{slider._meta.app_label}_{slider._meta.model_name}_change', args=[slider.pk])
        if slider.pk:
            return mark_safe(f"<a href='{url}'>изменить слайдер</a>")
        else:
            return ""

    def format_text(self, obj):
        if obj.text and len(obj.text) > 30:
            return obj.text[:30] + ".."
        return obj.text or " - "


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
    list_display = ['article', 'name', 'song']


class ImageUnitInline(admin.TabularInline):
    model = ImageUnit
    extra = 1
    readonly_fields = ["image_preview"]
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={'rows': 10, 'cols': 30}),
        }
    }
    
    def image_preview(self, obj):
        return mark_safe(f"<img src='{obj.image.url}' style='max-height: 200px;'>")


@admin.register(ImageSlider)
class ImageSliderAdmin(admin.ModelAdmin):
    inlines = [ImageUnitInline]
    list_display = ['name', 'bindings']


@admin.register(ImageUnit)
class ImageUnitAdmin(admin.ModelAdmin):
    readonly_fields = ["image_preview"]
    
    def image_preview(self, obj):
        return mark_safe(f"<img src='{obj.image.url}' style='max-height: 400px;'>")