from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import *
from django.contrib.auth import authenticate, login
from django.urls import reverse
from dj_rest_auth.views import LoginView
import requests


class CustomLoginView(LoginView):
    def get(self, request):
        form = LoginForm()
        return render(request, "registration/login.html", context={"form": form})
    
    def post(self, request):
        form = LoginForm(request.POST)
        
        if form.is_valid():
            data = {
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password']
            }
            r = requests.post(
                request.build_absolute_uri(reverse('rest_login')),
                data=data
            )
            if r.status_code != 200:
                return HttpResponse("Неверные данные")
            return redirect('/')

        return redirect('/')


def login(request):
    if request.user.is_authenticated:
        return redirect('/') # Адрес

    if request.method == "GET":
        return render(request, 'registration/login.html')