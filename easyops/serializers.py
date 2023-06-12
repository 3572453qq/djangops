from django.db.models import fields
from rest_framework import serializers
from .models import app,Server

class appSerializer(serializers.ModelSerializer):
    class Meta:
        model=app
        fields= "__all__"

class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Server
        fields= "__all__"