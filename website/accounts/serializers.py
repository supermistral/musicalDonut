from rest_framework import serializers
from dj_rest_auth.serializers import LoginSerializer
from .models import User


class CustomLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)