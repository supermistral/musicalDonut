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


def get_filtered_articles(request, articles):
    # Для фильтра исполнителей
    result_articles = []
    filter_singers_data = request.GET.get('singers', None)

    if filter_singers_data:
        filter_singers_list = filter_singers_data.split("+")

        for article in articles:
            singers_list = article.singers_list()
            if not singers_list:
                continue

            for singer in singers_list:
                if singer in filter_singers_list:
                    result_articles.append(article)
                    break
    else:
        result_articles = articles
    
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
    
    filter_singers = []
    result_articles = []
    sorting_context = {
        "sorting_key": "date_desc",
        "sorting_value": SORTING_MESS["date_desc"]
    }
    empty_message = "Статьи скоро появятся"

    if articles.exists():
        articles = articles.exclude(id=last_article.id)
        # all_items = [article.subdivisions.all() for article in articles]
        # all_items.append(articles)

        filter_singers_names = []
        for article in articles:
            filter_singers_names += article.singers_list()

        sorted_filter_singers_names = sorted(set(filter_singers_names))
        filter_singers = [{name: filter_singers_names.count(name)} for name in sorted_filter_singers_names]

        # Фильтр
        result_articles = []
        isFilter = request.GET.get('filter', None)
        if isFilter == "true":
            empty_message = "По вашему запросу ничего не найдено"
            result_articles = get_filtered_articles(request, articles)
        else:
            result_articles = articles

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

        # for queryset in all_items:
        #     for queryset_item in queryset:
        #         if queryset_item.song is not None:
        #             songs.append(queryset_item.song)

        # all_filter_singers_names = [song.singers_list() for song in songs]
        # filter_singers_names = []

        # for singer_list in all_filter_singers_names:
        #     if singer_list is not None:
        #         filter_singers_names += singer_list

    return render(
        request, 
        'main/start_page.html', 
        context={
            'articles': result_articles,
            'last_article': [last_article],     # must be list
            'filter_singers': filter_singers,
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