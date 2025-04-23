from rest_framework import serializers

from .models import Discrepancy

class DiscrepancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Discrepancy
        fields = '__all__'
        
class AnnotationSerializer(serializers.Serializer):
    user = serializers.CharField()
    label = serializers.CharField()

class ExampleAnnotationsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    annotations = AnnotationSerializer(many=True)
