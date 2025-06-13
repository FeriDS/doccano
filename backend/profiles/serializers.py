# profiles/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import Permission
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

class UserProfileSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=True
    )

    class Meta:
        model = UserProfile
        fields = ['id', 'name', 'description', 'permissions']

    def to_representation(self, instance):
        logger.info(f"Serializing profile: {instance.name}")
        data = super().to_representation(instance)
        logger.info(f"Serialized data: {data}")
        return data

    def validate_name(self, value):
        if UserProfile.objects.filter(name=value).exists():
            raise serializers.ValidationError("Já existe um perfil com este nome.")
        return value

    def validate_permissions(self, value):
        if not value:
            raise serializers.ValidationError("É necessário selecionar pelo menos uma permissão.")
        return value

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']
        extra_kwargs = {
            'content_type': {'read_only': True}
        }
