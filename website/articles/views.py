from django.shortcuts import render
from .models import *
from .permissions import StaffPermission
from .serializers import *
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated, AllowAny
from rest_framework import generics
from django.views import generic
from django.http import Http404


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
    