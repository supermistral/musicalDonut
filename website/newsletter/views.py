from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from .newsletter_obj_utility import delete_subscribed_user, save_subscribed_user
from .services import generate_subscription_email, verify_subscribed_user, validate_email


def subscribe(request):
    if request.method == "POST":
        email = request.POST.get('email', None)
        error_msg = validate_email(email)

        if error_msg:
            return JsonResponse({'msg_type': 'error', 'msg': error_msg})

        subscribed_user = save_subscribed_user(email)
        print(subscribed_user)

        if subscribed_user:
            generation_status = generate_subscription_email(email, subscribed_user)
            
            if generation_status:
                return JsonResponse({
                    'msg_type': 'success', 
                    'msg': 'На указанный адрес отправлен код подтверждения'
                })
            else:
                delete_subscribed_user(email)
                return JsonResponse({
                    'msg_type': 'error',
                    'msg': 'Произошла ошибка отправки письма подтверждения'
                })
        else:
            return JsonResponse({
                'msg_type': 'error',
                'msg': 'Произошла неизвестная ошибка'
            })

    return HttpResponseRedirect(reverse('home'))
     

def activate(request, uidb64, token):
    if request.method != "GET":
        raise Http404

    verify_subscribed_user_status = verify_subscribed_user(uidb64, token)

    if verify_subscribed_user_status:
        pass
   
    return HttpResponseRedirect(reverse('home'))
        