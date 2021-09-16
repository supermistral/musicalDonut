from articles.models import *
from django.shortcuts import render
from django.views import generic
from django.db.models import Q
from itertools import chain
from django.http import Http404, JsonResponse
from django.template.response import SimpleTemplateResponse

SORTING_MESS = {
    'date_asc': "Дата по возрастанию",
    'date_desc': "Дата по убыванию",
}


def filter_articles(request, articles, filter_key, callback, comparison_callback):
    result_articles = []
    filter_data = request.GET.get(filter_key, None)

    if filter_data:
        filter_list = filter_data.split("+")

        for article in articles:
            items = callback(article)
            if not items:
                continue

            for item in items:
                if comparison_callback(item) in filter_list:
                    result_articles.append(article)
                    break
    else:
        result_articles = articles

    return result_articles


def get_filtered_articles(request, articles):
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


def main_page(request):
    last_article = Article.ready_objects.first()
    articles = Article.ready_objects.all()
    
    filters = {}
    # filter_singers = []
    result_articles = []
    sorting_context = {
        "sorting_key": "date_desc",
        "sorting_value": SORTING_MESS["date_desc"]
    }
    empty_message = "Статьи скоро появятся"

    if articles.exists():
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
            return JsonResponse({'html': rendered_template}, safe=False)

        # Singers filter list (ok)
        filter_singers_names = []
        for article in articles:
            filter_singers_names += article.singers_list()

        sorted_filter_singers_names = sorted(set(filter_singers_names))
        # filter_singers = [{name: filter_singers_names.count(name)} for name in sorted_filter_singers_names]
        filter_singers = [{
            "name": name,
            "value": name,
            "count": filter_singers_names.count(name)
        } for name in sorted_filter_singers_names]
        filters["singers"] = filter_singers

        # Genres filter list (ok)
        filter_genres_names = []
        for article in articles:
            filter_genres_names += article.genres()

        sorted_filter_genres_names = sorted(set(filter_genres_names), key=lambda genre: genre.name)
        filter_genres = [{
                "name": genre.name, 
                "value": genre.name_eng, 
                "count": filter_genres_names.count(genre)
            } for genre in sorted_filter_genres_names]
        filters["genres"] = filter_genres

    return render(
        request, 
        'main/start_page.html', 
        context={
            'articles': result_articles,
            'last_article': [last_article],     # must be list
            'filters': filters,
            'empty_message': empty_message,
            **sorting_context
        }
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["articles"] = Article.ready_objects.filter(section=self.object)
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

        print(result)

        for block in textblocks:
            temp_article = block.subdivision.article
            if (temp_article not in result) and (temp_article in ready_articles):
                result.append(temp_article)

        result = sorted(result, key=lambda article: article.date_release, reverse=True)

        print(result)
        
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