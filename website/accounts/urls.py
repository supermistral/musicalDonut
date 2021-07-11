from django.urls import path, include
from .views import *
from dj_rest_auth import urls

urlpatterns = [
    path('registration/', include('dj_rest_auth.registration.urls')),
    path('allauth/', include('allauth.urls')),

    path('auth/', include('dj_rest_auth.urls')),
    path('login/', CustomLoginView.as_view(), name="custom_login"),
    path('profile/', profile, name="profile"),
]