from rest_framework import serializers
from .models import AnnotationRule, VotingConfig

class AnnotationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnotationRule
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')

class VotingConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = VotingConfig
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')