from django.contrib.auth.models import Group
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from users.models import AlfredUser


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]


class AlfredUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = AlfredUser
        fields = ("id", "email", "password")


class AlfredUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = AlfredUser
        fields = ("id", "email")
