from articles.models import Article, Section
from django.shortcuts import render
from django.views import generic


def main_page(request):
    last_article = Article.ready_objects.all()[-1]
    sections = Section.objects.all()

    return render(
        request, 
        'main/start_page.html', 
        context={
            'last_article': last_article,
            'sections': sections
        }
    )


class ArticleList(generic.ListView):
    model = Article
    template_name = 'main/start_page.html'

    def get_queryset(self):
        return Article.ready_objects.all().order_by('-date_release')


class SectionDetail(generic.DetailView):
    model = Section
    template_name = 'main/section_page.html'
    slug_field = 'name_for_url'

    def get_object(self, **kwargs):
        return Section.articles.ready_objects.all().order_by('-date_release')
    