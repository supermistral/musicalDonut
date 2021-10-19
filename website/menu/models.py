from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import MultiFieldPanel, FieldPanel, InlinePanel, PageChooserPanel
from wagtail.core.models import Orderable
from wagtail.snippets.models import register_snippet
from django_extensions.db.fields import AutoSlugField


class MenuItem(Orderable):
    link_title = models.CharField(max_length=30, blank=True, null=True)
    link_url = models.CharField(max_length=30, blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page', 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="+"
    )

    page = ParentalKey('Menu', on_delete=models.CASCADE, related_name='menu_items')

    panels = [
        FieldPanel("link_title"),
        FieldPanel("link_url"),
        PageChooserPanel("link_page"),
    ]

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_url:
            return self.link_url

        return "#"

    @property
    def title(self):
        if self.link_page and not self.link_title:
            return self.link_page.title
        elif self.link_title:
            return self.link_title

        return 'Unknown title'


@register_snippet
class Menu(ClusterableModel):
    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="title", editable=True)

    panels = [
        MultiFieldPanel([
            FieldPanel("title"),
            FieldPanel("slug")
        ], heading="Menu"),
        InlinePanel("menu_items", label="Menu items")
    ]

    def __str__(self):
        return self.title