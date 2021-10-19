import re


widget_height = {
    'track': 200,
    'album': 500
}

widget_providers = {
    'vk': {
        'regexp': r'^.*(vk\.com\/music\/album\/)([\-\d]+)_([\d]+)_([\w]+)',
        'code': '<div id="vk-widget-{id}"></div><script type="text/javascript">VK.Widgets.Playlist("vk-widget-{id}", {owner_id}, {playlist_id}, "{id}");</script>'
    },
    'youtube': {
        'regexp': r'^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*',
        'code': '<iframe height="{height}" src="https://www.youtube.com/embed/{id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
    },
    'spotify': {
        'regexp': r'^.*(open\.spotify\.com\/)([\w\/\w]+).*',
        'code': '<iframe src="https://open.spotify.com/embed/{id}" width="100%" height="{height}" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>'
    },
    'yandex': {
        'regexp': r'^.*(music\.yandex\.ru\/)([\w\/]+).*',
        'code': '<iframe frameborder="0" style="border:none;width:100%;" width="100%" height="{height}" src="https://music.yandex.ru/iframe/#{id}"></iframe>'
    },
    'apple': {
        'regexp': r'^.*(music\.apple\.com\/\S*\/album\/(.*))',
        'code': '<iframe allow="autoplay *; encrypted-media *; fullscreen *" frameborder="0" height="{height}" style="width:100%;overflow:hidden;background:transparent;" sandbox="allow-forms allow-popups allow-same-origin allow-scripts allow-storage-access-by-user-activation allow-top-navigation-by-user-activation" src="https://embed.music.apple.com/ru/album/{id}"></iframe>'
    },
    'deezer': {
        'regexp': r'^.*(deezer\.com\/\S*\/)([track|album].*)',
        'code': '<iframe title="deezer-widget" src="https://widget.deezer.com/widget/dark/{id}" width="100%" height="{height}" frameborder="0" allowtransparency="true" allow="encrypted-media; clipboard-write"></iframe>'
    }
}


class MusicWidget:

    @staticmethod
    def get_code(url, provider, is_album):
        provider_item = widget_providers.get(provider, None)
        if provider is None:
            return None

        song_match = re.match(provider_item['regexp'], url)
        if song_match is None:
            return None

        code_data = {}

        if provider == 'vk':
            owner_id = song_match.group(2)
            playlist_id = song_match.group(3)
            song_id = song_match.group(4)

            code_data.update({
                'owner_id': owner_id,
                'playlist_id': playlist_id,
            })
        else:
            song_id = song_match.group(2)

        return provider_item['code'].format(
            height=widget_height['album' if is_album else 'track'],
            id=song_id,
            **code_data
        )