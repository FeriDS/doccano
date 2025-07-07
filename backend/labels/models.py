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
    label = models.ForeignKey(to=CategoryType, on_delete=models.CASCADE, null=True, blank=True)
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
        """
        Retorna estatísticas de votação para um exemplo e versão específicos.
        Se perspective_filters for fornecido, filtra apenas pelos utilizadores com esses valores de perspectiva.
        """
        from perspectives.models import get_users_with_perspective_value, ProjectPerspective
        
        qs = cls.objects.filter(example_id=example_id, version=version)
        
        # Se há filtros de perspectiva, obter primeiro os utilizadores válidos
        valid_users = None
        if perspective_filters:
            try:
                # Obter o ProjectPerspective para este exemplo
                from examples.models import Example
                example = Example.objects.get(id=example_id)
                project_perspective = ProjectPerspective.objects.get(project=example.project)
                
                # Para cada filtro de perspectiva, obter os utilizadores correspondentes
                user_sets = []
                for field_name, value in perspective_filters.items():
                    users = get_users_with_perspective_value(project_perspective, field_name, value)
                    user_sets.append(set(users))
                
                # Fazer interseção de todos os conjuntos para obter utilizadores que atendem TODOS os filtros
                if user_sets:
                    valid_users = user_sets[0]
                    for user_set in user_sets[1:]:
                        valid_users = valid_users.intersection(user_set)
                else:
                    valid_users = set()
                    
            except Exception as e:
                print(f"Error filtering by perspective: {e}")
                valid_users = set()
        
        # Filtrar por utilizadores válidos se especificado
        if valid_users is not None:
            qs = qs.filter(user__in=valid_users)
        
        total = qs.count()
        labels = {}
        
        # Contar votos por label
        for dv in qs:
            if dv.label is None:
                label_name = 'abstencao'
            else:
                label_name = f'label_{dv.label.text}'
            labels[label_name] = labels.get(label_name, 0) + 1
        
        # Converter para percentagem
        percent_labels = {}
        for k, v in labels.items():
            percent_labels[k] = f'{round((v / total) * 100, 2)}%' if total > 0 else '0%'
        
        # Lista de votos detalhada
        votes = []
        for dv in qs:
            votes.append({
                "label": dv.label.text if dv.label else None,
                "user": dv.user.username,
                "user_id": dv.user.id,
                "created_at": dv.created_at.isoformat()
            })
        
        result = {
            'total': total,
            'votes': votes,
            **percent_labels  # Adicionar percentuais como campos diretos
        }
        
        return result

    @classmethod
    def get_voting_user_stats(cls, example_id, version, abstention_labels=("abstention", "null"), perspective_filters=None):
        """
        Retorna estatísticas de votação dos membros do projeto para um exemplo e versão.
        Se perspective_filters for fornecido, conta apenas os utilizadores que atendem aos critérios de perspectiva.
        """
        from projects.models import Member
        from examples.models import Example
        from perspectives.models import get_users_with_perspective_value, ProjectPerspective
        
        example = Example.objects.get(id=example_id)
        project = example.project
        
        # Obter todos os membros do projeto
        members = Member.objects.filter(project=project)
        all_usernames = set(m.username for m in members)
        all_users = set(m.user for m in members)
        
        # Se há filtros de perspectiva, filtrar os membros
        valid_users = all_users
        if perspective_filters:
            try:
                project_perspective = ProjectPerspective.objects.get(project=project)
                
                # Para cada filtro de perspectiva, obter os utilizadores correspondentes
                user_sets = []
                for field_name, value in perspective_filters.items():
                    users = get_users_with_perspective_value(project_perspective, field_name, value)
                    user_sets.append(set(users))
                
                # Fazer interseção de todos os conjuntos
                if user_sets:
                    valid_users = user_sets[0]
                    for user_set in user_sets[1:]:
                        valid_users = valid_users.intersection(user_set)
                else:
                    valid_users = set()
                    
            except Exception as e:
                print(f"Error filtering by perspective: {e}")
                valid_users = set()
        
        # Obter votos apenas dos utilizadores válidos
        qs = cls.objects.filter(example_id=example_id, version=version, user__in=valid_users)
        
        # Agrupar votos por utilizador
        votes_by_user = {}
        for dv in qs.select_related('user', 'label'):
            username = dv.user.username
            if dv.label is None:
                label = None
            else:
                label = dv.label.text.lower()
            votes_by_user.setdefault(username, []).append(label)
        
        # Determinar usernames válidos (só os que atendem aos filtros de perspectiva)
        valid_usernames = set(u.username for u in valid_users)
        
        # Utilizadores que votaram em pelo menos uma label regular (não abstenção)
        users_voted = set(
            username for username, labels in votes_by_user.items()
            if any(lab is not None and lab not in abstention_labels for lab in labels)
        )
        
        # Utilizadores que votaram apenas em abstenção/null
        users_with_abstention = set(
            username for username, labels in votes_by_user.items()
            if any(lab is None for lab in labels) and username not in users_voted
        )
        
        # Utilizadores que não votaram (da lista de utilizadores válidos)
        users_not_voted = valid_usernames - set(votes_by_user.keys())
        
        return {
            'total_users': len(valid_usernames),
            'users_voted': len(users_voted),
            'users_only_abstention': len(users_with_abstention),
            'users_not_voted': len(users_not_voted),
            'usernames': list(valid_usernames),
            'usernames_voted': list(users_voted),
            'usernames_only_abstention': list(users_with_abstention),
            'usernames_not_voted': list(users_not_voted),
        }