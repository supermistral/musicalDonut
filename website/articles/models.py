from django.db import models
from django.utils import timezone


class ArticleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(date_release__lte=timezone.now(), is_active=True)\
            .order_by('-date_release')


class Singer(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Genre(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Song(models.Model):
    singer = models.ForeignKey(Singer, on_delete=models.CASCADE, related_name='songs')
    name = models.CharField(max_length=100)
    date_release = models.DateField()
    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL, null=True, related_name='songs'
    )

    def __str__(self):
        return f"{self.singer.name} -> {self.name}" 

    class Meta:
        ordering = ['singer__name']


class Section(models.Model):
    name = models.CharField(max_length=20, unique=True)
    name_for_url = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


# Классы блоков для css: center, left, right
class TextBlockClass(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class TextBlock(models.Model):
    subdivision = models.ForeignKey('Subdivision', on_delete=models.CASCADE, related_name="textblocks")
    text = models.TextField()
    image = models.ImageField(upload_to='text_blocks/', blank=True, null=True)
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='textblocks')
    text_class = models.ForeignKey(
        TextBlockClass, 
        on_delete=models.SET_DEFAULT, 
        default="center", 
        related_name='textblocks'
    )

    def __str__(self):
        temp_name = self.subdivision.name[:10] + ".." if len(self.subdivision.name) > 10 else self.subdivision.name
        return f"{temp_name} -> {self.song.name}"

    class Meta:
        ordering = ['subdivision__name']


class Article(models.Model):
    name = models.CharField(max_length=100)
    section = models.ForeignKey(
        Section, on_delete=models.SET_NULL, null=True, related_name='articles'
    )
    image = models.ImageField(upload_to='articles/', blank=True, null=True)    # Добавить дефолтную картинку
    date_release = models.DateTimeField()
    date_change = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    ready_objects = ArticleManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['date_release']


class Subdivision(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name="subdivisions")
    name = models.CharField(max_length=100)

    def __str__(self):
        temp_name = self.name[:10] + ".." if len(self.name) > 10 else self.name
        return f"{self.article.name} -> {temp_name}"

    class Meta:
        ordering = ['article__name']