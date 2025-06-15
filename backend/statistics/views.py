from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from examples.models import Example
from labels.models import Category, Span, Relation
from projects.models import Project
from projects.permissions import IsProjectAdmin, IsProjectStaffAndReadOnly
from perspectives.models import ProjectPerspective, UserPerspectiveAnswer


class AnnotationStatisticsAPI(APIView):
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]

    def get(self, request, *args, **kwargs):
        project_id = self.kwargs["project_id"]
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        annotator_id = request.query_params.get('annotator')
        perspective = request.query_params.get('perspective')
        label = request.query_params.get('label')
        resolved = request.query_params.get('resolved')
        example_id = request.query_params.get('example_id')

        # Base queryset
        examples = Example.objects.filter(project=project_id)
        
        # Apply filters
        if example_id:
            examples = examples.filter(id=example_id)
        if start_date and end_date:
            examples = examples.filter(created_at__range=[start_date, end_date])
        if annotator_id:
            examples = examples.filter(annotations__user=annotator_id)
        if perspective:
            examples = examples.filter(annotations__perspective=perspective)
        if label:
            examples = examples.filter(categories__label__text=label)
        if resolved is not None:
            if resolved.lower() == 'true':
                examples = examples.filter(is_confirmed=True)
            elif resolved.lower() == 'false':
                examples = examples.filter(is_confirmed=False)

        # Calculate statistics
        total_annotations = examples.count()
        disagreements = self._find_disagreements(examples)
        disagreement_count = len(disagreements)
        resolved_disagreements = len([d for d in disagreements if d['status'] == 'resolved'])
        unique_perspectives = 1

        statistics = {
            'statistics': {
                'disagreementRate': (disagreement_count / total_annotations * 100) if total_annotations > 0 else 0,
                'perspectiveCount': unique_perspectives,
                'resolutionRate': (resolved_disagreements / disagreement_count * 100) if disagreement_count > 0 else 0,
                'averageAnnotationTime': self._calculate_avg_annotation_time(examples),
            },
            'disagreements': disagreements,
            'disagreementByCategory': self._get_disagreement_by_category(disagreements),
            'perspectiveDistribution': self._get_perspective_distribution(examples),
            'labelDistribution': self._get_label_distribution(examples),
            'perspectivePatterns': self._get_perspective_patterns(examples, disagreements)
        }

        return Response(data=statistics, status=status.HTTP_200_OK)

    def get_user_perspective(self, project, user):
        try:
            project_perspective = ProjectPerspective.objects.get(project=project)
            user_perspective = UserPerspectiveAnswer.objects.filter(
                project_perspective=project_perspective,
                user=user
            ).first()
            if user_perspective:
                # Ajuste conforme o campo real do modelo
                return str(user_perspective)
        except ProjectPerspective.DoesNotExist:
            pass
        return 'Default'

    def _find_disagreements(self, examples):
        disagreements = []
        
        for example in examples:
            # Get all annotations for this example
            categories = Category.objects.filter(example=example)
            spans = Span.objects.filter(example=example)
            relations = Relation.objects.filter(example=example)

            # Check for disagreements in categories
            if categories.count() > 1:
                category_labels = categories.values_list('label__text', flat=True).distinct()
                if len(category_labels) > 1:
                    disagreements.append({
                        'id': example.id,
                        'textId': str(example.id),
                        'category': 'Category',
                        'type': 'Label Disagreement',
                        'annotators': list(categories.values_list('user__username', flat=True)),
                        'status': 'resolved' if example.states.exists() else 'pending',
                        'text': example.text,
                        'annotations': [
                            {
                                'id': cat.id,
                                'annotator': cat.user.username,
                                'label': cat.label.text,
                                'perspective': self.get_user_perspective(example.project, cat.user)
                            } for cat in categories
                        ],
                        'discussion': self._get_discussion(example)
                    })

            # Check for disagreements in spans
            if spans.count() > 1:
                span_labels = spans.values_list('label__text', flat=True).distinct()
                if len(span_labels) > 1:
                    disagreements.append({
                        'id': example.id,
                        'textId': str(example.id),
                        'category': 'Span',
                        'type': 'Label Disagreement',
                        'annotators': list(spans.values_list('user__username', flat=True)),
                        'status': 'resolved' if example.states.exists() else 'pending',
                        'text': example.text,
                        'annotations': [
                            {
                                'id': span.id,
                                'annotator': span.user.username,
                                'label': span.label.text,
                                'perspective': self.get_user_perspective(example.project, span.user)
                            } for span in spans
                        ],
                        'discussion': self._get_discussion(example)
                    })

            # Check for disagreements in relations
            if relations.count() > 1:
                relation_types = relations.values_list('type__text', flat=True).distinct()
                if len(relation_types) > 1:
                    disagreements.append({
                        'id': example.id,
                        'textId': str(example.id),
                        'category': 'Relation',
                        'type': 'Type Disagreement',
                        'annotators': list(relations.values_list('user__username', flat=True)),
                        'status': 'resolved' if example.states.exists() else 'pending',
                        'text': example.text,
                        'annotations': [
                            {
                                'id': rel.id,
                                'annotator': rel.user.username,
                                'label': rel.type.text,
                                'perspective': self.get_user_perspective(example.project, rel.user)
                            } for rel in relations
                        ],
                        'discussion': self._get_discussion(example)
                    })

        return disagreements

    def _get_disagreement_by_category(self, disagreements):
        category_counts = {}
        for disagreement in disagreements:
            category = disagreement['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return [{'category': k, 'count': v} for k, v in category_counts.items()]

    def _get_perspective_distribution(self, examples):
        from collections import Counter
        perspectives = []
        for ex in examples:
            for cat in ex.categories.all():
                perspectives.append(self.get_user_perspective(ex.project, cat.user))
            for span in ex.spans.all():
                perspectives.append(self.get_user_perspective(ex.project, span.user))
            for rel in ex.relations.all():
                perspectives.append(self.get_user_perspective(ex.project, rel.user))
        counter = Counter(perspectives)
        return [{'perspective': k, 'count': v} for k, v in counter.items()]

    def _get_discussion(self, example):
        # This would need to be implemented based on your discussion model
        return []

    def _get_label_distribution(self, examples):
        # Conta a frequência de cada label nas categorias
        from collections import Counter
        labels = []
        for ex in examples:
            labels += list(ex.categories.values_list('label__text', flat=True))
        return dict(Counter(labels))

    def _calculate_avg_annotation_time(self, examples):
        # Exemplo: diferença média entre created_at e updated_at das anotações
        from datetime import timedelta
        times = []
        for ex in examples:
            for cat in ex.categories.all():
                if cat.created_at and cat.updated_at:
                    delta = cat.updated_at - cat.created_at
                    times.append(delta.total_seconds())
        if times:
            return round(sum(times) / len(times), 2)
        return 0

    def _get_perspective_patterns(self, examples, disagreements):
        # Conta total, desacordos e acordos por perspetiva
        from collections import defaultdict
        patterns = defaultdict(lambda: {'total': 0, 'disagreements': 0, 'agreements': 0})
        for ex in examples:
            for cat in ex.categories.all():
                p = getattr(cat, 'perspective', None) or 'Default'
                patterns[p]['total'] += 1
        for d in disagreements:
            for ann in d['annotations']:
                p = ann.get('perspective', 'Default')
                patterns[p]['disagreements'] += 1
        for p in patterns:
            patterns[p]['agreements'] = patterns[p]['total'] - patterns[p]['disagreements']
        return [ {'perspective': p, **v} for p, v in patterns.items() ] 