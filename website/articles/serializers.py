from rest_framework import serializers
from .models import *


class SingerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Singer
        fields = ('__all__')


class SongSerializer(serializers.ModelSerializer):

    class Meta:
        model = Song
        fields = ('__all__')