from rest_framework import serializers
from .models import Perspective, PerspectiveField


class PerspectiveFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerspectiveField
        fields = ("id","name", "type", "options")


class PerspectiveSerializer(serializers.ModelSerializer):
    fields = PerspectiveFieldSerializer(many=True, write_only=True)

    class Meta:
        model = Perspective
        fields = ("id", "name", "project", "type", "fields")
        read_only_fields = ("id",)

    def create(self, validated_data):
        fields_data = validated_data.pop("fields", [])
        perspective = Perspective.objects.create(**validated_data)
        for field_data in fields_data:
            PerspectiveField.objects.create(perspective=perspective, **field_data)
        return perspective
