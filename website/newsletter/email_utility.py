import requests
from requests import Response
from django.conf import settings
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.core.mail import send_mail as django_send_email


def send_email(data: dict) -> bool or Response:
    # print(data)
    # try:
    #     url = f'https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages'
    #     response = requests.post(
    #         url,
    #         auth=("api", settings.MAILGUN_API_KEY),
    #         data={
    #             "from": f"Musical Donut <mailgun@{settings.MAILGUN_DOMAIN}>",
    #             "to": ["mediamart37@gmail.com"],
    #             # "subject": data["subject"],
    #             # "text": data["text"],
    #             # "html": data["html"]
    #             "subject": "hello",
    #             "text": "Testing"
    #         }
    #     )
    #     print(response)
    #     return response
    # except Exception as e:
    #     print(e)

    try:
        return django_send_email(
            data["subject"],
            data["text"],
            f"Musical Donut <mailgun@{settings.MAILGUN_DOMAIN}>",
            [data["email"]],
            html_message=data["html"]
        )
    except Exception as e:
        print(e)
    
    return False


def send_subscription_email(email: str, uid: str, token: str) -> bool or Response:
    template = get_template('email/subscription_newsletter.html')
    data = {}
    data['html'] = template.render({
        'uid': uid,
        'token': token,
        'email': email,
    })
    data['subject'] = "Confirm your request"
    data['email'] = email
    data['text'] = strip_tags(data['html'])
    
    return send_email(data)