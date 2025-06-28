from rest_framework import serializers

from .models import Assignment, Comment, Example, ExampleState


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "username",
            "example",
            "text",
            "created_at",
        )
        read_only_fields = ("user", "example")


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ("id", "assignee", "example", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ExampleSerializer(serializers.ModelSerializer):
    annotation_approver = serializers.SerializerMethodField()
    is_confirmed = serializers.SerializerMethodField()
    assignments = serializers.SerializerMethodField()
    label_distribution = serializers.SerializerMethodField()

    @classmethod
    def get_annotation_approver(cls, instance):
        approver = instance.annotations_approved_by
        return approver.username if approver else None

    def get_is_confirmed(self, instance):
        user = self.context.get("request").user
        if instance.project.collaborative_annotation:
            states = instance.states.all()
        else:
            states = instance.states.filter(confirmed_by_id=user.id)
        return states.count() > 0

    def get_assignments(self, instance):
        return [
            {
                "id": assignment.id,
                "assignee": assignment.assignee.username,
                "assignee_id": assignment.assignee.id,
            }
            for assignment in instance.assignments.all()
        ]

    def get_label_distribution(self, obj):
        from labels.models import Category
        from examples.models import Assignment
        from collections import Counter

        # 1. Labels votados
        labels = Category.objects.filter(example=obj)
        total_labels = labels.count()
        label_counter = Counter(label.label.text for label in labels if hasattr(label, 'label') and label.label)
        label_percent = {k: round(v / total_labels * 100, 2) for k, v in label_counter.items()} if total_labels else {}

        # 2. Assignees
        assignees = list(obj.assignments.all())
        assignee_ids = set(a.assignee_id for a in assignees)
        voted_users = set(label.user_id for label in labels)

        # 3. Abstenção e Null
        abstencao_users = set()
        null_users = set()
        # Buscar estados confirmados para este exemplo
        confirmed_ids = set()
        if hasattr(obj, 'states'):
            confirmed_ids = set(obj.states.values_list('confirmed_by_id', flat=True))
        for a in assignees:
            if a.assignee_id in voted_users:
                continue  # já votou
            if a.assignee_id in confirmed_ids:
                abstencao_users.add(a.assignee_id)
            else:
                null_users.add(a.assignee_id)

        total_assignees = len(assignee_ids)
        percent_abstencao = round(len(abstencao_users) / total_assignees * 100, 2) if total_assignees else 0
        percent_null = round(len(null_users) / total_assignees * 100, 2) if total_assignees else 0

        result = dict(label_percent)
        if percent_abstencao > 0:
            result['abstenção'] = percent_abstencao
        if percent_null > 0:
            result['null'] = percent_null
        return result

    class Meta:
        model = Example
        fields = [
            "id",
            "filename",
            "meta",
            "annotation_approver",
            "comment_count",
            "text",
            "is_confirmed",
            "upload_name",
            "score",
            "assignments",
            "has_discrepancy",
            "label_distribution",
            "annotation_start_date",
            "annotation_end_date",
            "is_finished",
            "is_resolved",
        ]
        read_only_fields = ["filename", "is_confirmed", "upload_name", "assignments"]


class ExampleStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleState
        fields = ("id", "example", "confirmed_by", "confirmed_at")
        read_only_fields = ("id", "example", "confirmed_by", "confirmed_at")
