from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import handler404
from . import views


app_name = 'website'

handler404 = 'website.views.handler404'


urlpatterns = [
    path('admin/', admin.site.urls),

    # path('auth/', include('accounts.urls')),
    path('articles/', include('articles.urls', namespace="articles")),
    
    path('', views.main_page, name="home"),
    # path('', views.ArticleList.as_view(), name="main_page"),
    path('section/<slug:slug>/', views.SectionDetail.as_view(), name="section_page"),
    path('search/', views.SearchArticlesList.as_view(), name="search_articles"),
    path('articles/<int:pk>/', views.ArticleDetail.as_view(), name="article"),
    path('accounts/', include('accounts.urls')),
    #path('newsletter/', include('newsletter.urls', namespace='newsletter')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)