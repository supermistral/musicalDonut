from django.db import models
from django.utils import timezone


class ArticleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(date_release__lte=timezone.now(), is_active=True)


class Singer(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Genre(models.Model):
    name = models.CharField(max_length=20, unique=True)


class Song(models.Model):
    singer = models.ForeignKey(Singer, on_delete=models.CASCADE, related_name='songs')
    name = models.CharField(max_length=100)
    date_release = models.DateField()
    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL, null=True, related_name='songs'
    )


class Section(models.Model):
    name = models.CharField(max_length=20, unique=True)
    name_for_url = models.CharField(max_length=20, unique=True)


# Классы блоков для css: center, left, right
class TextBlockClass(models.Model):
    name = models.CharField(max_length=20)


class TextBlock(models.Model):
    text = models.TextField()
    image = models.ImageField(upload_to='text_blocks/', blank=True, null=True)
    text_class = models.ForeignKey(
        TextBlockClass, on_delete=models.SET_DEFAULT, 
        default="center", related_name='textblocks'
    )


class Article(models.Model):
    name = models.CharField(max_length=100)
    songs = models.ManyToManyField(Song, related_name='articles')
    section = models.ForeignKey(
        Section, on_delete=models.SET_NULL, null=True, related_name='articles'
    )
    image = models.ImageField(upload_to='articles/', blank=True, null=True)    # Добавить дефолтную картинку
    text_blocks = models.ManyToManyField(TextBlock, related_name='articles')
    date_release = models.DateTimeField()
    date_change = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    ready_objects = ArticleManager()