from django.db import models
from django.utils import timezone
from django.db.models import Q
from .utils import replaceQuotes
import re


class ArticleManager(models.Manager):
    
    def get_queryset(self):
        return super().get_queryset().filter(date_release__lte=timezone.now(), is_active=True)\
            .order_by('-date_release')

    def search(self, query=None):
        queryset = self.get_queryset()
        if query is not None:
            search_lookup = (
                Q(name__icontains=query) |
                Q(image_caption__icontains=query)
            )
            queryset = queryset.filter(search_lookup).distinct()
        return queryset


class TextBlockManager(models.Manager):

    def search(self, query=None):
        queryset = self.get_queryset()
        if query is not None:
            search_lookup = (
                Q(text__icontains=query) |
                Q(song__name__icontains=query) |
                Q(song__genre__name__icontains=query) |
                Q(song__singer__name__icontains=query)
            )
            queryset = queryset.filter(search_lookup).distinct()
        return queryset


class Singer(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Музыкальная группа"
        verbose_name_plural = "Музыкальные группы"


class Genre(models.Model):
    name = models.CharField(max_length=30, unique=True)
    name_eng = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Song(models.Model):
    name = models.CharField(max_length=100)
    date_release = models.DateField(null=True, blank=True)
    genre = models.ForeignKey(
        Genre, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='songs'
    )
    # genre_choices = (
    #     (None, 'без жанра'),
    #     ('pop', 'Поп'),
    #     ('rock', 'Рок'),
    #     ('indie', 'Инди'),
    #     ('metal', 'Метал'),
    #     ('alternative', 'Альтернатива'),
    #     ('electronics', 'Электроника'),
    #     ('dance', 'Танцевальная'),
    #     ('rap', 'Рэп'),
    #     ('jazz', 'Джаз'),
    #     ('blues', 'Блюз'),
    #     ('reggae', 'Регги'),
    #     ('punk', 'Панк')
    # )
    # genre = models.CharField(max_length=30, choices=genre_choices, default=None, blank=True, null=True)
    is_album = models.BooleanField(default=False)

    ref_vk = models.CharField(max_length=500, blank=True, null=True)
    ref_yandex = models.CharField(max_length=500, blank=True, null=True)
    ref_spotify = models.CharField(max_length=500, blank=True, null=True)
    ref_apple = models.CharField(max_length=500, blank=True, null=True)
    ref_youtube = models.CharField(max_length=500, blank=True, null=True)
    ref_deezer = models.CharField(max_length=500, blank=True, null=True)

    def replace_ref_width(self, ref, height=150):
        if not ref:
            return ref
        regex = re.compile(r' height=\W\d+\W ')
        return regex.sub(f' height="{height}" ', ref)

    def save(self, *args, **kwargs):
        if self.is_album:
            self.ref_yandex = self.replace_ref_width(self.ref_yandex, 500)
            self.ref_spotify = self.replace_ref_width(self.ref_spotify, 500)
            self.ref_apple = self.replace_ref_width(self.ref_apple, 500)
        else:
            self.ref_yandex = self.replace_ref_width(self.ref_yandex)
            self.ref_spotify = self.replace_ref_width(self.ref_spotify)
            self.ref_apple = self.replace_ref_width(self.ref_apple)
        return super().save(*args, **kwargs)

    def _get_singers(self):
        related_singers = SongSingerRelation.objects.filter(song=self)
        singers_str = None

        if related_singers.exists():
            related_singers_is_feat = related_singers.filter(is_feat=True)
            related_singers_is_not_feat = related_singers.filter(is_feat=False)
            singers_str = ", ".join([obj.singer.name for obj in related_singers_is_not_feat])
            
            if related_singers_is_feat.exists():
                singers_str += " feat. " + ", ".join([obj.singer.name for obj in related_singers_is_feat])
        
        return singers_str

    def __str__(self):
        param_album = "| Альбом" if self.is_album else ""
        singers_str = self._get_singers()
        if singers_str is None:
            singers_str = "[исполнители не указаны]"
        return f"{singers_str} -> {self.name} {param_album}"

    def singers(self):
        singers_str = self._get_singers()
        if singers_str is None:
            singers_str = "Неизвестен"
        return singers_str

    def full_name(self):
        singers_str = self.singers()
        return f"{singers_str} - {self.name}"

    def singers_list(self):
        related_singers = SongSingerRelation.objects.filter(song=self)
        if related_singers.exists():
            return [obj.singer.name for obj in related_singers]
        return None

    class Meta:
        verbose_name = "Песня"
        verbose_name_plural = "Песни"


class SongSingerRelation(models.Model):
    song = models.ForeignKey(
        Song, 
        on_delete=models.CASCADE, 
        related_name='related_singers',
    )
    singer = models.ForeignKey(
        Singer, 
        on_delete=models.CASCADE, 
        related_name='related_songs',
    )
    is_feat = models.BooleanField(default=False)

    def __str__(self):
        is_feat_str = " (feat)" if self.is_feat else ""
        return f"{self.singer.name} - {self.song.name}{is_feat_str}"

    class Meta:
        verbose_name = "Песня и связанные группы"
        verbose_name_plural = "Песни и связанные группы"


class Section(models.Model):
    name = models.CharField(max_length=40, unique=True)
    name_for_url = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.name


# Классы блоков для css: center, left, right
# class TextBlockClass(models.Model):
#     name = models.CharField(max_length=20)

#     def __str__(self):
#         return self.name


class TextBlock(models.Model):
    subdivision = models.ForeignKey(
        'Subdivision',
        on_delete=models.CASCADE, 
        related_name="textblocks"
    )
    text = models.TextField()
    slider = models.OneToOneField(
        'ImageSlider',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    text_classes_choices = (
        ('center', 'по центру'), 
        ('left', 'текст слева'), 
        ('right', 'текст справа'),
    )
    text_class = models.CharField(max_length=20, choices=text_classes_choices, default='center')

    objects = TextBlockManager()

    def __str__(self):
        temp_name = ""
        if self.subdivision:
            temp_name = self.subdivision.article.__str__() + " -> "
            if self.subdivision.name:
                if len(self.subdivision.name) > 30:
                    temp_name += self.subdivision.name[:30] + ".."
                else:
                    temp_name += self.subdivision.name
            else:
                temp_name += self.subdivision.song.full_name()

        temp_text = ""
        if self.text:
            if len(self.text) > 30:
                temp_text = " | " + self.text[:30] + ".."
            else:
                temp_text = " | " + self.text

        return f"{temp_name}{temp_text}"

    def save(self, *args, **kwargs):
        self.text = replaceQuotes(self.text)
        self.text = self.text\
            .replace("<ж>", "<b>").replace("</ж>", "</b>")\
            .replace("<к>", "<i>").replace("</к>", "</i>")\
            .replace("<ц>", "<blockquote class='decoration'>").replace("</ц>", "</blockquote>")
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Текстовый блок"
        verbose_name_plural = "Текстовые блоки"


class Article(models.Model):
    name = models.CharField(max_length=200)
    section = models.ForeignKey(
        Section, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='articles'
    )
    image = models.ImageField(
        upload_to='articles',
        default='default/article.jpg',
        blank=True
    )
    slider = models.OneToOneField(
        'ImageSlider', 
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    song = models.ForeignKey(
        Song, 
        on_delete=models.CASCADE, 
        related_name='articles',
        blank=True,
        null=True
    )
    date_release = models.DateTimeField()
    date_change = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    number = models.IntegerField(blank=True, null=True)

    objects = models.Manager()
    ready_objects = ArticleManager()

    def __str__(self):
        return f"{self.section.name} №{self.number}"

    def save(self, *args, **kwargs):
        if self.number is None:
            objects = Article.objects.filter(section=self.section)
            self.number = len(objects) + 1
        return super().save(*args, **kwargs)

    def singers_list(self):
        sd_list = Subdivision.objects.filter(article=self)
        
        singers = []
        if self.song is not None and self.song.singers_list() is not None:
            singers += self.song.singers_list()
        
        for sd in sd_list:
            song = sd.song
            if song is not None and song.singers_list() is not None:
                singers += sd.song.singers_list()
        
        return singers

    def genres(self):
        sd_list = Subdivision.objects.filter(article=self)
        song_list = Song.objects.filter(Q(articles__in=[self]) | Q(subdivisions__in=sd_list))
        
        genres = Genre.objects.filter(songs__in=song_list)
        return genres

    def contains_singers(self, search_params):
        singers_list = self.singers_list()
        if not singers_list:
            return False

        return any([item in search_params for item in singers_list])

    def contains_genres(self, search_params):
        genres_list = self.genres()
        if not genres_list.exists():
            return False

        return any([item.name_eng in search_params for item in genres_list])

    class Meta:
        ordering = ['-date_release']
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"


class Subdivision(models.Model):
    article = models.ForeignKey(
        'Article', 
        on_delete=models.CASCADE, 
        related_name="subdivisions"
    )
    name = models.CharField(max_length=100, blank=True, null=True)
    song = models.ForeignKey(
        Song, 
        on_delete=models.CASCADE, 
        related_name='subdivisions',
        blank=True,
        null=True
    )

    @property
    def format_name(self):
        if self.name and len(self.name) > 30:
            return self.name[:30] + ".." 
        return self.name or self.song and self.song.full_name()

    def __str__(self):
        temp_name = self.format_name
        if not temp_name and self.song:
            temp_name = self.song.full_name()
        return f"{self.article} -> {temp_name}"

    class Meta:
        ordering = ['article__name']
        verbose_name = "Раздел статьи"
        verbose_name_plural = "Разделы статьи"


class ImageSlider(models.Model):
    name = models.CharField(max_length=70)

    def get_relation(self, str_relation, class_name):
        try:
            obj = class_name.objects.get(slider=self)
            temp_name = ""
            if str_relation:
                str_relation += " | "
            if class_name == TextBlock:
                temp_name = obj.subdivision.format_name
            else:
                temp_name = obj.name
            temp_name = temp_name[:40] + ".." if len(temp_name) > 40 else temp_name
            str_relation += temp_name
        except:
            pass
        return str_relation

    @property
    def bindings(self):
        obj_relation = ""
        for class_name in [Article, TextBlock]:
            obj_relation = self.get_relation(obj_relation, class_name)
        if not obj_relation:
            obj_relation = "(без привязки)"

        return obj_relation

    def __str__(self):
        obj_relation = self.bindings
        if obj_relation:
            obj_relation = "| " + obj_relation
            
        return f"{self.name} {obj_relation}"

    class Meta:
        ordering = ['name']
        verbose_name = "Слайдер изображений"
        verbose_name_plural = "Слайдеры изображений"


class ImageUnit(models.Model):
    slider = models.ForeignKey(
        ImageSlider, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to="sliders", blank=True, null=True)
    video = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.video is not None:
            self.video = self.video.strip()
            if "</iframe>" not in self.video:
                regex = re.search(r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})', self.video)
                if regex is not None:
                    video_code = regex.group(1)
                    widget = f"<iframe width='800' height='450' src='https://youtube.com/embed/{video_code}' title='Youtube video player' frameborder='0'" +\
                        " allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture' allowfullscreen></iframe>"
                    self.video = widget

        return super().save(*args, **kwargs)

    def __str__(self):
        first_image = ImageUnit.objects.filter(slider=self.slider).first()
        id_diff = self.id - first_image.id + 1
        is_video = " (видео)" if self.video else ""
        return f"{self.slider.name} | {id_diff}{is_video}"

    class Meta:
        ordering = ['slider__name']
        verbose_name = "Изображение для слайдера"
        verbose_name_plural = "Изображения для слайдера"