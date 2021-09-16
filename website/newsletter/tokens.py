import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, obj, timestamp):
        return (
            six.text_type(obj.pk) + six.text_type(timestamp) + 
            six.text_type(obj.is_active)
        )

subscription_newsletter_activation_token = TokenGenerator()