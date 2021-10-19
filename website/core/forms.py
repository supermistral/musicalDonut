from wagtail.admin.forms import WagtailAdminModelForm
from .utils import widget_providers
import re


class SongLinksForm(WagtailAdminModelForm):

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        error_message = 'Неверная ссылка на трек/альбом'

        for provider in widget_providers:
            data = cleaned_data.get(provider, None)
            if data is not None:
                match = re.match(widget_providers[provider]['regexp'], 
                                 cleaned_data[provider])
                if match is None:
                    self.add_error(provider, error_message)

        return cleaned_data