"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views


app_name = 'website'


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
    path('newsletter/', include('newsletter.urls', namespace='newsletter')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)