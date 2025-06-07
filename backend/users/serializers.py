from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "first_name", "last_name", "is_superuser", "is_staff", "created_by")
        read_only_fields = ("id", "created_by")

    def get_created_by(self, obj):
        try:
            return obj.creation_info.created_by_id
        except:
            return None
