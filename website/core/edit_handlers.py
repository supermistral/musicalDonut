from wagtail.admin.edit_handlers import InlinePanel
from django.template.loader import render_to_string


class SingleInlinePanel(InlinePanel):
    template = 'wagtail/edit_handlers/single_inline_panel.html'

    def __init__(self, relation_name, panels=None, heading='', label='', *args, **kwargs):
        super().__init__(relation_name=relation_name, heading=heading, panels=panels, *args, **kwargs)
        self.heading = heading or label
        self.relation_name = relation_name
        self.panels = panels
        self.label = label
        self.min_num = 1
        self.max_num = 1

    def render(self):
        return render_to_string(self.template, { 'self': self })