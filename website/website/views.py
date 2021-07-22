from articles.models import *
from django.shortcuts import render
from django.views import generic
from django.db.models import Q
from itertools import chain


def main_page(request):
    last_article = Article.ready_objects.first()
    articles = Article.ready_objects.all()
    if articles.exists():
        articles = articles.exclude(id=last_article.id)

    return render(
        request, 
        'main/start_page.html', 
        context={
            'articles': articles,
            'last_article': last_article
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
    