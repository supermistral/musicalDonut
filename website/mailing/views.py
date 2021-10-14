from django.shortcuts import render
from django.http import HttpResponse, JsonReponse
from .models import Subscribe
from .utils import SendSubscribeMail


def subscribe(request):
    if request.method == 'POST':
        email = request.POST['email']
        email_queryset = Subscribe.objects.filter(email=email)
        if email_queryset.exists():
            return JsonReponse({"status": 404})
        
        Subscribe.objects.create(email=email)
        SendSubscribeMail(email)

    return HttpResponse('/')