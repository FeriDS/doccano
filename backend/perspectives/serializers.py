from rest_framework import serializers
from .models import PerspectiveField, UserPerspectiveAnswer

class PerspectiveFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerspectiveField
        fields = ['id', 'name', 'field_type', 'description']


class UserPerspectiveAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPerspectiveAnswer
        fields = ['id', 'user', 'project', 'field', 'value_string', 'value_int', 'value_bool']
