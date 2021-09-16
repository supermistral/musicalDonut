from .models import NewsletterSubscribedUsers


def save_subscribed_user(email: str) -> NewsletterSubscribedUsers or None:
    try:
        subscribe_user = NewsletterSubscribedUsers.objects.get(email=email)
    except NewsletterSubscribedUsers.DoesNotExist:
        subscribe_user = NewsletterSubscribedUsers.objects.create(email=email)
    except Exception as e:
        # Error into logging
        print(e)
        return None

    subscribe_user.save()

    return subscribe_user


def delete_subscribed_user(email: str) -> None:
    NewsletterSubscribedUsers.objects.get(email=email).delete()