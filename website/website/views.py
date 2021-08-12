from articles.models import *
from django.shortcuts import render
from django.views import generic
from django.db.models import Q
from itertools import chain
from django.http import Http404


def main_page(request):
    last_article = Article.ready_objects.first()
    articles = Article.ready_objects.all()
    filter_singers = []

    if articles.exists():
        articles = articles.exclude(id=last_article.id)
        all_items = [article.subdivisions.all() for article in articles]
        all_items.append(articles)
        songs = []

        for queryset in all_items:
            for queryset_item in queryset:
                if queryset_item.song is not None:
                    songs.append(queryset_item.song)

        all_filter_singers_names = [song.singers_list() for song in songs]
        filter_singers_names = []

        for singer_list in all_filter_singers_names:
            if singer_list is not None:
                filter_singers_names += singer_list

        sorted_filter_singers_names = sorted(set(filter_singers_names))
        filter_singers = [{name: filter_singers_names.count(name)} for name in sorted_filter_singers_names]

    return render(
        request, 
        'main/start_page.html', 
        context={
            'articles': articles,
            'last_article': [last_article],     # must be list
            'filter_singers': filter_singers
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