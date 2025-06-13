from rest_framework import serializers
from .models import Perspective, PerspectiveField, ProjectPerspective, UserPerspectiveAnswer

class PerspectiveFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerspectiveField
        fields = ('id', 'name', 'description', 'field_type', 'choices', 
                 'required', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class PerspectiveSerializer(serializers.ModelSerializer):
    fields = PerspectiveFieldSerializer(many=True, required=False)
    created_by_username = serializers.SerializerMethodField()

    class Meta:
        model = Perspective
        fields = ('id', 'name', 'description', 'fields', 'created_by', 
                 'created_by_username', 'created_at', 'updated_at')
        read_only_fields = ('created_by', 'created_at', 'updated_at')

    def get_created_by_username(self, obj):
        return obj.created_by.username if obj.created_by else None

    def create(self, validated_data):
        fields_data = validated_data.pop('fields', [])
        perspective = Perspective.objects.create(**validated_data)
        
        for field_data in fields_data:
            field = PerspectiveField.objects.create(**field_data)
            perspective.fields.add(field)
        
        return perspective

class ProjectPerspectiveSerializer(serializers.ModelSerializer):
    perspective = PerspectiveSerializer(read_only=True)
    is_annotation_open = serializers.SerializerMethodField()

    class Meta:
        model = ProjectPerspective
        fields = ('id', 'project', 'perspective', 'created_by', 'created_at', 'updated_at', 'is_annotation_open')
        read_only_fields = ('created_at', 'updated_at')

    def get_perspective_name(self, obj):
        return obj.perspective.name

    def get_perspective_fields(self, obj):
        return PerspectiveFieldSerializer(obj.perspective.fields.all(), many=True).data

    def get_is_annotation_open(self, obj):
        return obj.project.is_annotation_open

class UserPerspectiveAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPerspectiveAnswer
        fields = ('id', 'project_perspective', 'user', 'field_values', 
                 'is_complete', 'created_at', 'updated_at')
        read_only_fields = ('is_complete', 'created_at', 'updated_at')

    def validate_field_values(self, field_values):
        project_perspective = self.instance.project_perspective if self.instance else \
                     ProjectPerspective.objects.get(id=self.initial_data.get('project_perspective'))
        
        required_fields = project_perspective.perspective.fields.filter(required=True).values_list('name', flat=True)
        missing_fields = [field for field in required_fields if field not in field_values]
        
        if missing_fields:
            raise serializers.ValidationError(
                f"The following required fields are missing: {', '.join(missing_fields)}"
            )
        
        return field_values 