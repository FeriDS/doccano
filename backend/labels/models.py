import uuid

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from .managers import (
    BoundingBoxManager,
    CategoryManager,
    LabelManager,
    RelationManager,
    SegmentationManager,
    SpanManager,
    TextLabelManager,
)
from examples.models import Example
from label_types.models import CategoryType, RelationType, SpanType


class Label(models.Model):
    objects = LabelManager()

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    prob = models.FloatField(default=0.0)
    manual = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(Label):
    objects = CategoryManager()
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="categories")
    label = models.ForeignKey(to=CategoryType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("example", "user", "label")


class Span(Label):
    objects = SpanManager()
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="spans")
    label = models.ForeignKey(to=SpanType, on_delete=models.CASCADE)
    start_offset = models.IntegerField()
    end_offset = models.IntegerField()

    def __str__(self):
        text = self.example.text[self.start_offset : self.end_offset]
        return f"({text}, {self.start_offset}, {self.end_offset}, {self.label.text})"

    def validate_unique(self, exclude=None):
        allow_overlapping = getattr(self.example.project, "allow_overlapping", False)
        is_collaborative = self.example.project.collaborative_annotation
        if allow_overlapping:
            super().validate_unique(exclude=exclude)
            return

        overlapping_span = (
            Span.objects.exclude(id=self.id)
            .filter(example=self.example)
            .filter(
                models.Q(start_offset__gte=self.start_offset, start_offset__lt=self.end_offset)
                | models.Q(end_offset__gt=self.start_offset, end_offset__lte=self.end_offset)
                | models.Q(start_offset__lte=self.start_offset, end_offset__gte=self.end_offset)
            )
        )
        if is_collaborative:
            if overlapping_span.exists():
                raise ValidationError("This overlapping is not allowed in this project.")
        else:
            if overlapping_span.filter(user=self.user).exists():
                raise ValidationError("This overlapping is not allowed in this project.")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def is_overlapping(self, other: "Span"):
        return (
            (other.start_offset <= self.start_offset < other.end_offset)
            or (other.start_offset < self.end_offset <= other.end_offset)
            or (self.start_offset < other.start_offset and other.end_offset < self.end_offset)
        )

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(start_offset__gte=0), name="startOffset >= 0"),
            models.CheckConstraint(check=models.Q(end_offset__gte=0), name="endOffset >= 0"),
            models.CheckConstraint(check=models.Q(start_offset__lt=models.F("end_offset")), name="start < end"),
        ]


class TextLabel(Label):
    objects = TextLabelManager()
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="texts")
    text = models.TextField()

    def is_same_text(self, other: "TextLabel"):
        return self.text == other.text

    class Meta:
        unique_together = ("example", "user", "text")


class Relation(Label):
    objects = RelationManager()
    from_id = models.ForeignKey(Span, on_delete=models.CASCADE, related_name="from_relations")
    to_id = models.ForeignKey(Span, on_delete=models.CASCADE, related_name="to_relations")
    type = models.ForeignKey(RelationType, on_delete=models.CASCADE)
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="relations")

    def __str__(self):
        text = self.example.text
        from_span = text[self.from_id.start_offset : self.from_id.end_offset]
        to_span = text[self.to_id.start_offset : self.to_id.end_offset]
        type_text = self.type.text
        return f"{from_span} - ({type_text}) -> {to_span}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def clean(self):
        same_example = self.from_id.example == self.to_id.example == self.example
        if not same_example:
            raise ValidationError("You need to label the same example.")
        return super().clean()


class BoundingBox(Label):
    objects = BoundingBoxManager()
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    label = models.ForeignKey(to=CategoryType, on_delete=models.CASCADE)
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="bboxes")

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(x__gte=0), name="x >= 0"),
            models.CheckConstraint(check=models.Q(y__gte=0), name="y >= 0"),
            models.CheckConstraint(check=models.Q(width__gte=0), name="width >= 0"),
            models.CheckConstraint(check=models.Q(height__gte=0), name="height >= 0"),
        ]


class Segmentation(Label):
    objects = SegmentationManager()
    points = models.JSONField(default=list)
    label = models.ForeignKey(to=CategoryType, on_delete=models.CASCADE)
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="segmentations")



class DatasetVersion(models.Model):
    """
    Model to store different versions of dataset responses.
    Based on Category structure but with version tracking.
    """
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="dataset_versions")
    label = models.ForeignKey(to=CategoryType, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    version = models.IntegerField(default=1, help_text="Version number of this dataset response")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Whether this version is currently active")
    
    class Meta:
        unique_together = ("example", "version", "user", "label")
        ordering = ["-version", "-created_at"]
    
    def __str__(self):
        return f"Dataset {self.example.id} - Version {self.version} - {self.label.text} - {self.user.username}"
    
    @classmethod
    def create_new_version(cls, example, label, user):
        """Create a new version for the given example, label, and user."""
        # Get the latest version number for this combination
        latest_version = cls.objects.filter(
            example=example,
            label=label,
            user=user
        ).aggregate(models.Max('version'))['version__max'] or 0
        
        # Create new version
        return cls.objects.create(
            example=example,
            label=label,
            user=user,
            version=latest_version + 1
        )
    
    @classmethod
    def get_latest_version(cls, example, label, user):
        """Get the latest version for the given example, label, and user."""
        return cls.objects.filter(
            example=example,
            label=label,
            user=user,
            is_active=True
        ).order_by('-version').first()
    
    @classmethod
    def get_version_history(cls, example, label, user):
        """Get all versions for the given example, label, and user."""
        return cls.objects.filter(
            example=example,
            label=label,
            user=user
        ).order_by('-version')
    
    @classmethod
    def get_responses_by_version_and_example(cls, example_id, version):
        """Get all responses for a specific example and version."""
        return cls.objects.filter(
            example_id=example_id,
            version=version,
            is_active=True
        ).select_related('user', 'label')
    
    @classmethod
    def get_total_possible_votes(cls, example_id, version):
        """Get total number of possible votes for a specific example and version."""
        from examples.models import Assignment
        # Count all assignments for this example
        return Assignment.objects.filter(example_id=example_id).count()
    
    @classmethod
    def get_total_votes_cast(cls, example_id, version):
        """Get total number of votes actually cast for a specific example and version."""
        return cls.objects.filter(
            example_id=example_id,
            version=version,
            is_active=True
        ).count()
    
    @classmethod
    def get_abstention_count(cls, example_id, version):
        """Get number of people who abstained from voting for a specific example and version."""
        from examples.models import Assignment
        from examples.models import Example
        
        # Get all assignments for this example
        assignments = Assignment.objects.filter(example_id=example_id)
        assigned_user_ids = set(assignments.values_list('assignee_id', flat=True))
        
        # Get users who actually voted in this version
        voted_user_ids = set(cls.objects.filter(
            example_id=example_id,
            version=version,
            is_active=True
        ).values_list('user_id', flat=True))
        
        # Get users who confirmed but didn't vote (abstention)
        example = Example.objects.get(id=example_id)
        confirmed_user_ids = set()
        if hasattr(example, 'states'):
            confirmed_user_ids = set(example.states.values_list('confirmed_by_id', flat=True))
        
        # Abstention = confirmed users who didn't vote
        abstention_user_ids = confirmed_user_ids - voted_user_ids
        return len(abstention_user_ids)
    
    @classmethod
    def get_null_vote_count(cls, example_id, version):
        """Get number of people who voted null for a specific example and version."""
        from examples.models import Assignment
        
        # Get all assignments for this example
        assignments = Assignment.objects.filter(example_id=example_id)
        assigned_user_ids = set(assignments.values_list('assignee_id', flat=True))
        
        # Get users who actually voted in this version
        voted_user_ids = set(cls.objects.filter(
            example_id=example_id,
            version=version,
            is_active=True
        ).values_list('user_id', flat=True))
        
        # Get users who confirmed
        from examples.models import Example
        example = Example.objects.get(id=example_id)
        confirmed_user_ids = set()
        if hasattr(example, 'states'):
            confirmed_user_ids = set(example.states.values_list('confirmed_by_id', flat=True))
        
        # Null votes = assigned users who didn't vote and didn't confirm
        null_user_ids = assigned_user_ids - voted_user_ids - confirmed_user_ids
        return len(null_user_ids)
    
    @classmethod
    def get_voting_statistics(cls, example_id, version):
        """Get comprehensive voting statistics for a specific example and version."""
        total_possible = cls.get_total_possible_votes(example_id, version)
        total_cast = cls.get_total_votes_cast(example_id, version)
        abstentions = cls.get_abstention_count(example_id, version)
        null_votes = cls.get_null_vote_count(example_id, version)
        
        return {
            'total_possible_votes': total_possible,
            'total_votes_cast': total_cast,
            'abstentions': abstentions,
            'null_votes': null_votes,
            'participation_rate': round((total_cast / total_possible * 100), 2) if total_possible > 0 else 0
        }

    @classmethod
    def get_all_versions_for_example(cls, example_id):
        """Get all version numbers for a given example (dataset)."""
        return cls.objects.filter(example_id=example_id).values_list('version', flat=True).distinct().order_by('version')

    @classmethod
    def get_perspectives_for_example(cls, example_id):
        """Get all users (perspectives) who voted for each version of a given example."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        qs = cls.objects.filter(example_id=example_id).values('version', 'user_id').distinct()
        # Agrupar por versão
        perspectives = {}
        for row in qs:
            version = row['version']
            user_id = row['user_id']
            if version not in perspectives:
                perspectives[version] = []
            perspectives[version].append(user_id)
        return perspectives
