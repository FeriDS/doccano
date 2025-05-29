# profiles/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import Permission
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True
    )

    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'description', 'permissions']
