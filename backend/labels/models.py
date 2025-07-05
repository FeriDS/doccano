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
    example = models.ForeignKey(to=Example, on_delete=models.CASCADE, related_name="dataset_versions")
    label = models.ForeignKey(to=CategoryType, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    version = models.IntegerField(default=1, help_text="Version number of this dataset response")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Whether this version is currently active")

    class Meta:
        db_table = "labels_datasetversion"
        unique_together = ("example", "version", "user", "label")
        ordering = ["-version", "-created_at"]

    def __str__(self):
        return f"Dataset {self.example.id} - Version {self.version} - {self.label.text} - {self.user.username}"

    @classmethod
    def get_all_versions_for_example(cls, example_id):
        """Get all version numbers for a given example (dataset)."""
        return cls.objects.filter(example_id=example_id).values_list('version', flat=True).distinct().order_by('version')

    @classmethod
    def get_full_data_for_example(cls, example_id):
        """
        Retorna todas as linhas da tabela labels_datasetversion associadas a um example_id.
        Inclui joins para user e label para fácil acesso à informação.
        """
        return cls.objects.filter(example_id=example_id)\
            .select_related("user", "label")\
            .order_by("version", "created_at")

    @classmethod
    def get_voting_statistics(cls, example_id, version, perspective_filters=None):
        qs = cls.objects.filter(example_id=example_id, version=version)
        if perspective_filters:
            for field, value in perspective_filters.items():
                # Supondo que o campo JSON está em user.profile.perspective
                lookup = {f'user__profile__perspective__{field}': value}
                qs = qs.filter(**lookup)
        total = qs.count()
        labels = {}
        for dv in qs:
            label_name = f'label_{dv.label.text}'
            labels[label_name] = labels.get(label_name, 0) + 1
        # Converter para percentagem com símbolo %
        percent_labels = {}
        for k, v in labels.items():
            percent_labels[k] = f'{round((v / total) * 100, 2)}%' if total > 0 else '0%'
        return {
            'total': total,
            **percent_labels
        }