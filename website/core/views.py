from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.template.response import SimpleTemplateResponse
from itertools import chain
from datetime import datetime, timedelta


SORTING_MESS = {
    'date_asc': "Дата по возрастанию",
    'date_desc': "Дата по убыванию",
}


def is_ajax_request(request):
    '''Проверяет, был ли запрос в режиме ajax'''

    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_filtered_articles(request, articles):
    '''Фильтрация по исполнителям и жанрам'''

    result_articles = list(articles)
    
    filter_by_singers = request.GET.get('singers', None)
    if filter_by_singers:
        filter_singers_list = filter_by_singers.split("+")
        result_articles = list(filter(lambda item: item.contains_singers(filter_singers_list), result_articles))

    filter_by_genres = request.GET.get('genres', None)
    if filter_by_genres:
        filter_genres_list = filter_by_genres.split("+")
        result_articles = list(filter(lambda item: item.contains_genres(filter_genres_list), result_articles))

    return result_articles

def get_sorted_articles(request, articles, context=None):
    '''Сортировка по ключу из запроса'''

    result_articles = []
    sorting_key = request.GET.get('sorting', None)
    
    # Принадлежность запрошенного ключа сортировки
    if sorting_key:
        if sorting_key == "date_desc":
            result_articles = articles
        elif sorting_key == "date_asc":
            result_articles = sorted(articles, key=lambda article: article.go_live_at)
        else:
            sorting_key = "date_desc"
            result_articles = articles
        context["sorting_key"] = sorting_key
        context["sorting_value"] = SORTING_MESS[sorting_key]
    else:
        result_articles = articles
    
    return result_articles

    
def get_rendered_content(template, data):
    """Получение отрендеренного кода по шаблону"""

    template = SimpleTemplateResponse(template, context=data)
    rendered_template = template.render().rendered_content
    return {
        'json': True,
        'data': {
            'html': rendered_template
        }
    }


def handle_filtered_request(request, articles, last_article=None):
    """Возвращает словарь с данными для ответа на запрос с фильтрами/сортировкой"""

    filters = {}
    result_articles = []
    sorting_context = {
        "sorting_key": "date_desc",
        "sorting_value": SORTING_MESS["date_desc"]
    }
    empty_message = "Статьи скоро появятся"
    is_ajax = is_ajax_request(request)

    if articles.exists():

        if last_article is not None:
            articles = articles.exclude(id=last_article.id)
        
        # Фильтр
        result_articles = []
        isFilter = request.GET.get('filter', None)
        if isFilter == "true":
            empty_message = "По вашему запросу ничего не найдено"
            result_articles = get_filtered_articles(request, articles)
        else:
            result_articles = articles

        # Сортировка
        result_articles = get_sorted_articles(request, result_articles, sorting_context)

        if is_ajax:     # Запрос через fetch - отдать отрендеренный шаблон
            data_to_render = get_rendered_content(
                'wagtail/articles/article_cards.html', 
                {
                    'articles': result_articles,
                    'cover_section': 'true',
                    'empty_message': empty_message 
                }
            )
            return data_to_render

        # Singers filter list (ok)
        filter_singers_names_lists = []         # список списков певцов (для подсчета)
        for article in articles:
            filter_singers_names_lists.append(article.singers_list())


        filter_singers_names = list(chain(*filter_singers_names_lists))

        sorted_filter_singers_names = sorted(set(filter_singers_names)) # список певцов
        filter_singers = [{
            "name": singer,
            "value": singer,
            "count": len([x for x in filter_singers_names_lists if singer in x])
        } for singer in sorted_filter_singers_names]
        filters["singers"] = filter_singers

        # Genres filter list (ok)
        filter_genres_names_lists = []          # список списков жанров (для подсчета статей)
        for article in articles:
            filter_genres_names_lists.append(article.genres())

        filter_genres_names = list(chain(*filter_genres_names_lists))   # список жанров

        sorted_filter_genres_names = sorted(set(filter_genres_names), key=lambda genre: genre.name)
        filter_genres = [{
                "name": genre.name, 
                "value": genre.name_eng, 
                "count": len([x for x in filter_genres_names_lists if genre in x])
            } for genre in sorted_filter_genres_names]
        filters["genres"] = filter_genres

    elif is_ajax:
        data_to_render = get_rendered_content(
            'wagtail/articles/article_cards.html', 
            {
                'articles': result_articles,
                'cover_section': 'true',
                'empty_message': empty_message 
            }
        )
        return data_to_render

    return {
        'json': is_ajax,
        'data': {
            'filters': filters,
            'articles': result_articles,
            'empty_message': empty_message,
            'last_article': [last_article],
            **sorting_context
        }    
    }


def music_widgets(request, song):
    if is_ajax_request(request):
        # Установка куки song_links_enabled
        service_enabled = request.COOKIES.get('song_links_enabled', None)
        new_service_enabled = '0' if service_enabled == '1' else '1'

        template = SimpleTemplateResponse('wagtail/articles/song_links.html', context={
            'song': song,
            'enabled': new_service_enabled,
        })
        rendered_template = template.render().rendered_content

        if '<' not in rendered_template:
            rendered_template = ""

        reponse = JsonResponse({
            'is_enabled': bool(int(new_service_enabled)),
            'html': rendered_template
        })
        reponse.set_cookie('song_links_enabled',
                           new_service_enabled,
                           expires=datetime.now() + timedelta(days=30))

        return reponse

    raise Http404()