from django.shortcuts import render, get_object_or_404
from .models import *
from .permissions import StaffPermission
from .serializers import *
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated, AllowAny
from rest_framework import generics
from django.views import generic
from django.http import Http404, JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.template.response import SimpleTemplateResponse
from datetime import datetime, timedelta


class BaseViewForCreate(generics.ListCreateAPIView):
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, StaffPermission]
        return [permission() for permission in permission_classes]


class BaseViewForUpdate(generics.RetrieveUpdateDestroyAPIView):
    def get_permission(self):
        if self.request.method in SAFE_METHODS:
            permission_classes = [AllowAny]
        else:
            permission_classes = [isAuthenticated, StaffPermission]
        return [permission() for permission in permission_classes]


class SingerListCreate(BaseViewForCreate):
    queryset = Singer.objects.all()
    serializer_class = SingerSerializer


class SingerDetail(BaseViewForUpdate):
    queryset = Singer
    serializer_class = None


class SongListCreate(BaseViewForCreate):
    queryset = Song.objects.all()
    serializer_class = SongSerializer


class SongDetail(BaseViewForUpdate):
    queryset = Song
    serializer_class = None


class ArticlePreviewList(generic.ListView):
    model = Article
    template_name = 'main/section_page.html'
    context_object_name = 'articles'

    def get_queryset(self):
        if not self.request.user.is_staff:
            raise Http404()
        return Article.objects.filter(is_active=False)


# class SongRefsListView(generic.DetailView):
#     model = Song
#     context_object_name = 'song_refs'

#     def get_object(self, queryset=None):
#         song = super().get_object(queryset)
        
#         refs = [song.ref_vk, song.ref_yandex, song.spotify, 
#                 song.apple, song.youtube, song.deezer]
            
#         return refs

@require_http_methods(['GET'])
def song_widgets(request: HttpResponse, pk: int) -> JsonResponse:
    song = get_object_or_404(Song, pk=pk)

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if is_ajax:
        # Установка куки song_refs_enabled
        service_enabled = request.COOKIES.get('song_refs_enabled', None)
        new_service_enabled = '0' if service_enabled == '1' else '1'

        template = SimpleTemplateResponse('articles/song_refs.html', context={
            'song': song,
            'enabled': new_service_enabled
        })
        rendered_template = template.render().rendered_content
        
        if "<" not in rendered_template:
            rendered_template = ""
            
        response = JsonResponse({'is_enabled': bool(int(new_service_enabled)),
                                 'html': rendered_template })
        
        response.set_cookie('song_refs_enabled', 
                            new_service_enabled, 
                            expires=datetime.now() + timedelta(days=30))

        return response

    raise Http404()