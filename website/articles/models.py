from django.db import models


class Singer(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Genre(models.Model):
    name = models.CharField(max_length=20, unique=True)


class Song(models.Model):
    singer = models.ForeignKey(Singer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    date_release = models.DateField()
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)


class Section(models.Model):
    name = models.CharField(max_length=20, unique=True)


# Классы блоков для css: center, left, right
class TextBlockClass(models.Model):
    name = models.CharField(max_length=20)


class TextBlock(models.Model):
    text = models.TextField()
    image = models.FileField(upload_to='text_blocks/', blank=True)
    text_class = models.ForeignKey(TextBlockClass, on_delete=models.SET_DEFAULT, default="center")


class Article(models.Model):
    songs = models.ManyToManyField(Song)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    text_blocks = models.ManyToManyField(TextBlock)
    date_release = models.DateTimeField()
    date_change = models.DateTimeField()