# profiles/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import Permission
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'description', 'permissions']

    def validate_name(self, value):
        if UserProfile.objects.filter(name=value).exists():
            raise serializers.ValidationError("Já existe um perfil com este nome.")
        return value

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name']
