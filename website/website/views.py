from articles.models import *
from django.shortcuts import render
from django.views import generic
from django.db.models import Q, QuerySet
from itertools import chain
from django.http import Http404, JsonResponse, HttpRequest, HttpResponse
from django.template.response import SimpleTemplateResponse

SORTING_MESS = {
    'date_asc': "Дата по возрастанию",
    'date_desc': "Дата по убыванию",
}


def get_filtered_articles(request: HttpRequest, articles: QuerySet or list) -> list:
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

def get_sorted_articles(request: HttpRequest, articles: QuerySet or list, 
                        context: dict or None = None) -> list:
    result_articles = []
    sorting_key = request.GET.get('sorting', None)
    
    if sorting_key:
        if sorting_key == "date_desc":
            result_articles = articles
        elif sorting_key == "date_asc":
            result_articles = sorted(articles, key=lambda article: article.date_release)
        else:
            sorting_key = "date_desc"
            result_articles = articles
        context["sorting_key"] = sorting_key
        context["sorting_value"] = SORTING_MESS[sorting_key]
    else:
        result_articles = articles
    
    return result_articles


def handle_filtered_request(request: HttpRequest, articles: QuerySet or list, 
                            last_article: Article or None = None) -> dict:
    """Возвращает словарь с данными для ответа на запрос с фильтрами"""

    filters = {}
    result_articles = []
    sorting_context = {
        "sorting_key": "date_desc",
        "sorting_value": SORTING_MESS["date_desc"]
    }
    empty_message = "Статьи скоро появятся"

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

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        if is_ajax:     # Запрос через fetch - отдать отрендеренный шаблон
            template = SimpleTemplateResponse('articles/article_cards.html', context={
                'articles': result_articles,
                'cover_section': 'true',
                'empty_message': 'По вашему запросу ничего не найдено'
            })
            rendered_template = template.render().rendered_content
            return {
                'json': True,
                'data': {
                    'html': rendered_template
                }
            }

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

    return {
        'json': False,
        'data': {
            'filters': filters,
            'articles': result_articles,
            'empty_message': empty_message,
            'last_article': [last_article],
            **sorting_context
        }    
    }


def main_page(request: HttpRequest) -> HttpResponse or JsonReponse:
    last_article = Article.ready_objects.first()
    articles = Article.ready_objects.all()

    data_to_render = handle_filtered_request(request, articles, last_article)
    
    if data_to_render['json']:
        return JsonResponse({**data_to_render['data']}, safe=False)

    return render(
        request, 
        'main/start_page.html', 
        context={**data_to_render['data']}
    )


class ArticleList(generic.ListView):
    model = Article
    template_name = 'main/start_page.html'

    def get_queryset(self):
        return Article.ready_objects.all()


class SectionDetail(generic.DetailView):
    model = Section
    template_name = 'main/section_page.html'
    context_object_name = 'section'
    slug_field = 'name_for_url'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        data_to_render = handle_filtered_request(request, context['articles'])

        if data_to_render['json']:
            return JsonResponse({**data_to_render['data']}, safe=False)

        return self.render_to_response({**context, **data_to_render['data']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.ready_objects.filter(section=self.object)
        
        return context


class SearchArticlesList(generic.ListView):
    model = Article
    template_name = 'main/search_articles.html'
    context_object_name = 'articles'

    def get_queryset(self):
        query = self.request.GET.get('q', None)

        print(query)

        if query is None:
            return Article.ready_objects.none()

        textblocks = TextBlock.objects.search(query)
        articles = Article.ready_objects.search(query)

        result = chain(articles)
        ready_articles = Article.ready_objects.all()

        for block in textblocks:
            temp_article = block.subdivision.article
            if (temp_article not in result) and (temp_article in ready_articles):
                result.append(temp_article)

        result = sorted(result, key=lambda article: article.date_release, reverse=True)
        
        return result


class ArticleDetail(generic.DetailView):
    model = Article
    template_name = 'main/article.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        articles = Article.ready_objects.all()

        if not (obj in articles) and not self.request.user.is_staff:
            raise Http404()
            
        return obj


def handler404(request, exception=None):
    return render(request, 'error/page404.html')