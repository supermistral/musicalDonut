from assets.python.disposable_emails import disposable_emails
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from .models import NewsletterSubscribedUsers
from .tokens import subscription_newsletter_activation_token
from .email_utility import send_subscription_email
from requests import Response
from typing import Tuple
import re


def validate_email(email: str or None) -> str or None:
    msg = None

    if email is None:
        msg = 'Требуется email'
    elif NewsletterSubscribedUsers.objects.filter(email=email).exists():
        msg = 'Данный email уже зарегистрирован'
    elif not re.match(r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$", email):
        msg = "Неверный email"
    elif email.split("@")[-1] in disposable_emails:
        msg = "Неверный email"
    
    return msg


def _encode_subscribed_user(obj: NewsletterSubscribedUsers) -> Tuple[str, str]:
    """Возвращает uid, token по экземпляру"""

    token = subscription_newsletter_activation_token.make_token(obj)
    uid = urlsafe_base64_encode(force_bytes(token))
    return uid, token


def _decode_subscribed_user(uidb64: str) -> NewsletterSubscribedUsers or None:
    """Возвращает экземпляр объекта по uidb64"""

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        subscribed_user = NewsletterSubscribedUsers.objects.get(pk=uid)
    except Exception as e:
        # Invalid link
        print(e)
        subscribed_user = None

    return subscribed_user
    
    if (
        subscribed_user is not None and
        subscription_newsletter_activation_token.check_token(subscribed_user, token)
    ):
        subscribed_user.is_active = True
        subscribed_user.is_verified = True
        subscribed_user.save()
        return True
    
    return False


def generate_subscription_email(email: str, obj: NewsletterSubscribedUsers) -> bool or Response:
    """Создает и отправляет письмо активации подписки на рассылку"""
    
    uid, token = _encode_subscribed_user(obj)
    return send_subscription_email(email=email, uid=uid, token=token)


def _verify_subscribed_user_token(obj: NewsletterSubscribedUsers, token: str) -> bool:
    """Сверяет правильность токена для пользователя"""
    
    return subscription_newsletter_activation_token.check_token(subscribed_user, token)


def verify_subscribed_user(uidb64: str, token: str) -> bool:
    """Проверка пользователя по uidb64, token"""
    
    subscribed_user = _decode_subscribed_user(uidb64)

    if subscribed_user is not None and _verify_subscribed_user_token(subscribed_user, token):
        return True

    return False