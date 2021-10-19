from django.db import models
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from wagtail.admin.edit_handlers import (
    FieldPanel, StreamFieldPanel, PageChooserPanel, MultiFieldPanel, InlinePanel)
from wagtail.core.fields import StreamField
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.models import Page, Orderable, Collection
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet
from wagtail.images.models import Image

from . import blocks as custom_blocks
from .edit_handlers import SingleInlinePanel
from .utils import MusicWidget
from .forms import SongLinksForm
from .views import handle_filtered_request, music_widgets


class HomePage(RoutablePageMixin, Page):
    template = 'wagtail/home/home.html'
    max_count = 1

    banner_image = models.ForeignKey(
        'wagtailimages.Image', 
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        ImageChooserPanel("banner_image"),
    ]

    class Meta:
        verbose_name = "Home page"

    @property
    def articles(self):
        return ArticlePage.objects.live().public().order_by('-go_live_at')

    # def get_context(self, request, *args, **kwargs):
    #     context = super().get_context(request, *args, **kwargs)
    #     articles = ArticlePage.objects.live().public()

    #     if articles.exists():
    #         articles = articles.order_by('-go_live_at')
    #         last_article = articles.first()
    #         other_articles = articles.exclude(id=last_article.id)
    #         context = {
    #             **context,
    #             'articles': other_articles,
    #             'last_article': [last_article],
    #         }

    #     return context

    @route(r'^articles/song/(\d+)/links/$')
    def music_widgets(self, request, pk):
        song = get_object_or_404(Song, pk=pk)
        return music_widgets(request, song)

    @route(r'^$')
    def default_route(self, request):
        articles = self.articles
        last_article = articles.first()
        
        data_to_render = handle_filtered_request(request, articles, last_article)

        if data_to_render['json']:
            return JsonResponse(data_to_render['data'], safe=False)
        
        return render(request, self.template, { 
            **data_to_render['data'],
            'self': self
        })


class SectionPage(Page):
    parent_page_types = ['core.HomePage']
    subpage_types = ['core.ArticlePage']

    template = 'wagtail/home/section.html'

    class Meta:
        verbose_name = "Section page"
        verbose_name_plural = "Section Pages"

    @property
    def articles(self):
        return self.get_children().live().public().specific().order_by('-go_live_at')

    def serve(self, request):
        articles = self.articles
        print(articles)
        
        data_to_render = handle_filtered_request(request, articles)
        print(data_to_render)

        if data_to_render['json']:
            return JsonResponse(data_to_render['data'], safe=False)
        
        return render(request, self.template, { 
            **data_to_render['data'],
            'self': self
        })


class ArticlePage(Page):
    related_page = models.ForeignKey(
        to='core.SectionPage', 
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='+',
        default=1
    )
    preview_image = models.ForeignKey(
        'wagtailimages.Image', 
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='+'
    )
    number = models.PositiveIntegerField(blank=True, default=1)
    content = StreamField([
        ("song_block", custom_blocks.SimpleSongBlock()), 
    ], min_num=1, blank=True, null=True)

    content_panels = Page.content_panels + [
        PageChooserPanel('related_page'),
        ImageChooserPanel('preview_image'),
        FieldPanel('number'),
        StreamFieldPanel('content')
    ]

    parent_page_types = ['core.SectionPage']
    subpage_types = []

    template = 'wagtail/articles/article.html'

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.number:
            article_pages = ArticlePage.objects.descendant_of(self.related_page)
            article_pages_count = article_pages.count()
            self.number = article_pages_count + 1

        self.slug = self.number

        if not self.preview_image:
            collection = Collection.objects.filter(name='default')
            if collection.exists():
                image = Image.objects.filter(
                    collection=collection.first(), 
                    title='article preview_image'
                )
                if image.exists():
                    self.preview_image = image.first()
        
        return super().save(*args, **kwargs)

    def singers_list(self):
        singers = []
        
        for block in self.content:
            song = block.value['song']
            singers += song.singers_list()
        
        return singers

    def genres(self):
        genres = []

        for block in self.content:
            song = block.value['song']
            if song.genre:
                genres.append(song.genre)

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

    


@register_snippet
class Singer(models.Model):
    name = models.CharField(max_length=150)

    panels = [
        MultiFieldPanel([
            FieldPanel('name')
        ], heading="Name"),
    ]

    class Meta:
        verbose_name = "Исполнитель"
        verbose_name_plural = "Исполнители"

    def __str__(self):
        return self.name


class SingerSongOrderable(Orderable):
    song = ParentalKey(
        'core.Song',
        on_delete=models.CASCADE,
        related_name="singersong_songs"
    )
    singer = models.ForeignKey(
        Singer,
        on_delete=models.CASCADE,
        related_name='singersong_singers'
    )
    is_feat = models.BooleanField(default=False)

    panels = [
        SnippetChooserPanel("singer"),
        FieldPanel("is_feat"),
    ]


@register_snippet
class SongLinks(models.Model):
    song = models.OneToOneField(
        'Song', 
        on_delete=models.CASCADE,
        related_name='links',
        null=True
    )
    vk = models.URLField(max_length=200, null=True, blank=True)
    yandex = models.URLField(max_length=200, null=True, blank=True)
    spotify = models.URLField(max_length=200, null=True, blank=True)
    apple = models.URLField(max_length=200, null=True, blank=True)
    youtube = models.URLField(max_length=200, null=True, blank=True)
    deezer = models.URLField(max_length=200, null=True, blank=True)

    base_form_class = SongLinksForm

    class Meta:
        verbose_name = 'Ссылки на трек'
        verbose_name_plural = 'Ссылки на треки'

    def __str__(self):
        return self.song.name

    @property
    def widgets(self):
        '''Получение встраиваемых кодов всех виджетов'''

        widgets = []
        links_data = [('vk', self.vk), ('yandex', self.yandex), ('spotify', self.spotify),
                      ('apple', self.apple), ('youtube', self.youtube), ('deezer', self.deezer)]
        
        is_album = self.song.is_album
        for provider, value in links_data:
            if value is not None:
                widgets.append({
                    'provider': provider, 
                    'code': MusicWidget.get_code(value, provider, is_album)
                })

        return widgets


@register_snippet
class Song(ClusterableModel):
    name = models.CharField(max_length=150)
    genre = models.ForeignKey(
        'Genre', 
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="songs"
    )
    date_release = models.DateField(null=True, blank=True)
    is_album = models.BooleanField(default=False)
    
    panels = [
        FieldPanel('name'),
        SnippetChooserPanel('genre'),
        FieldPanel('is_album'),
        MultiFieldPanel([
            InlinePanel('singersong_songs', min_num=1, max_num=1),
        ], heading="Исполнители")
    ]

    class Meta:
        verbose_name = "Песня"
        verbose_name_plural = "Песни"

    def __str__(self):
        param_album = "| Альбом" if self.is_album else ""
        singers_str = self._get_singers()
        if singers_str is None:
            singers_str = "[исполнители не указаны]"
        return f"{singers_str} -> {self.name} {param_album}"

    def _get_singers(self):
        related_singers = self.singersong_songs.all()
        singers_str = None

        if related_singers.exists():
            related_singers_is_feat = related_singers.filter(is_feat=True)
            related_singers_is_not_feat = related_singers.filter(is_feat=False)
            singers_str = ", ".join([obj.singer.name for obj in related_singers_is_not_feat])
            
            if related_singers_is_feat.exists():
                singers_str += " feat. " + ", ".join([obj.singer.name for obj in related_singers_is_feat])
        
        return singers_str

    @property
    def singers(self):
        singers_str = self._get_singers()
        if singers_str is None:
            singers_str = "Неизвестен"
        return singers_str

    @property
    def full_name(self):
        return f"{self.singers} - {self.name}"

    def singers_list(self):
        related_singers = self.singersong_songs.all()
        if related_singers.exists():
            return [obj.singer.name for obj in related_singers]
        return None


@register_snippet
class Genre(models.Model):
    name = models.CharField(max_length=30, unique=True)
    name_eng = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


