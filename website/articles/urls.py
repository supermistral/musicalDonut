from django.urls import path, include
from .views import *


app_name = 'articles'

urlpatterns = [
    path('song/<int:pk>/refs/', song_widgets, name="song_widgets"),
    path('singer/', SingerListCreate.as_view()),
    path('song/', SongListCreate.as_view()),
    path('preview/', ArticlePreviewList.as_view(), name="articles_preview"),
]