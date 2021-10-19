from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.snippets.blocks import SnippetChooserBlock


class SongEmbedBlock(blocks.StructBlock):
    yandex = blocks.URLBlock(max_length=200, required=False)
    spotify = blocks.URLBlock(max_length=200, required=False)
    apple = blocks.URLBlock(max_length=200, required=False)
    youtube = blocks.URLBlock(max_length=200, required=False)
    deezer = blocks.URLBlock(max_length=200, required=False)

    class Meta:
        label = 'Ссылки на треки'
        template = 'wagtail/articles/widgets_block.html'

    def get_form_context(self, value, prefix='', errors=None):
        context = super().get_form_context(value, prefix=prefix, errors=errors)
        print(context)
        return context


class SliderBlock(blocks.StreamBlock):
    title = blocks.CharBlock(max_length=100, required=False)
    image = ImageChooserBlock()
    video = EmbedBlock(max_width=800, max_height=800)

    class Meta:
        icon = 'image'
        label = 'Изображение/видео'
        template = 'wagtail/articles/slider_block.html'


class SimpleSongBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        required=False,
        help_text="Оставляй пустым, если если хочешь отображение песни"
    )
    song = SnippetChooserBlock('core.Song')
    content = blocks.StreamBlock([
        ('text', blocks.RichTextBlock()),
        ('slider', SliderBlock()),
    ])

    class Meta:
        label = 'Блок песни'
        template = 'wagtail/articles/song_block.html'
        icon = 'edit'