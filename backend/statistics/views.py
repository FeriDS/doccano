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
        finished = request.query_params.get('finished')
        example_id = request.query_params.get('example_id')

        annotation_date_filter = {}
        if start_date and end_date:
            annotation_date_filter = {
                'annotation_start_date__gte': start_date,
                'annotation_end_date__lte': end_date
            }
        
        # Base queryset
        examples = Example.objects.filter(project=project_id)
        
        # Filtros de data aplicados nas anotações
        if example_id:
            examples = examples.filter(id=example_id)
        if annotator_id:
            examples = examples.filter(categories__user_id=annotator_id)
        if label:
            examples = examples.filter(categories__label__text=label)
        if resolved is not None:
            if resolved.lower() == 'true':
                examples = examples.filter(is_resolved=True)
            elif resolved.lower() == 'false':
                examples = examples.filter(is_resolved=False)
        if finished is not None:
            if finished.lower() == 'true':
                examples = examples.filter(is_finished=True)
            elif finished.lower() == 'false':
                examples = examples.filter(is_finished=False)
        if perspective:
            filtered_examples = set()
            for ex in examples:
                found = False
                for cat in ex.categories.filter(**annotation_date_filter):
                    if self.get_user_perspective(ex.project, cat.user) == perspective:
                        filtered_examples.add(ex.id)
                        found = True
                        break
                if not found:
                    for span in ex.spans.filter(**annotation_date_filter):
                        if self.get_user_perspective(ex.project, span.user) == perspective:
                            filtered_examples.add(ex.id)
                            found = True
                            break
                if not found:
                    for rel in ex.relations.filter(**annotation_date_filter):
                        if self.get_user_perspective(ex.project, rel.user) == perspective:
                            filtered_examples.add(ex.id)
                            break
            examples = Example.objects.filter(id__in=filtered_examples)
        elif annotation_date_filter:
            filtered_examples = set()
            for ex in examples:
                if ex.categories.filter(**annotation_date_filter).exists() or \
                   ex.spans.filter(**annotation_date_filter).exists() or \
                   ex.relations.filter(**annotation_date_filter).exists():
                    filtered_examples.add(ex.id)
            examples = Example.objects.filter(id__in=filtered_examples)

        # Calculate statistics
        total_examples = examples.count()
        disagreements = self._find_disagreements(examples, perspective, annotation_date_filter)
        disagreement_count = len(disagreements)
        disagreement_rate = (disagreement_count / total_examples * 100) if total_examples > 0 else 0
        resolved_disagreements = len([d for d in disagreements if d['status'] == 'resolved'])
        unique_perspectives = 1

        statistics = {
            'statistics': {
                'disagreementRate': disagreement_rate,
                'perspectiveCount': unique_perspectives,
                'resolutionRate': (resolved_disagreements / disagreement_count * 100) if disagreement_count > 0 else 0,
                'averageAnnotationTime': self._calculate_avg_annotation_time(examples),
            },
            'disagreements': disagreements,
            'disagreementByCategory': self._get_disagreement_by_category(disagreements),
            'perspectiveDistribution': self._get_perspective_distribution(examples, perspective, annotation_date_filter),
            'labelDistribution': self._get_label_distribution(examples, perspective, annotation_date_filter),
            'perspectivePatterns': self._get_perspective_patterns(examples, disagreements, perspective, annotation_date_filter)
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
                return user_perspective.field_values.get('role', 'Default')
        except ProjectPerspective.DoesNotExist:
            pass
        return 'Default'

    def _find_disagreements(self, examples, perspective=None, annotation_date_filter=None):
        disagreements = []
        for example in examples:
            categories = Category.objects.filter(example=example, **(annotation_date_filter or {}))
            spans = Span.objects.filter(example=example, **(annotation_date_filter or {}))
            relations = Relation.objects.filter(example=example, **(annotation_date_filter or {}))

            # Filtrar anotações pelo role/perspective se necessário
            if perspective:
                categories = [cat for cat in categories if self.get_user_perspective(example.project, cat.user) == perspective]
                spans = [span for span in spans if self.get_user_perspective(example.project, span.user) == perspective]
                relations = [rel for rel in relations if self.get_user_perspective(example.project, rel.user) == perspective]

            # Check for disagreements in categories
            if len(categories) > 1:
                category_labels = set([cat.label.text for cat in categories])
                if len(category_labels) > 1:
                    disagreements.append({
                        'id': example.id,
                        'textId': str(example.id),
                        'category': 'Category',
                        'type': 'Label Disagreement',
                        'annotators': [cat.user.username for cat in categories],
                        'status': 'resolved' if example.is_resolved else 'pending',
                        'text': example.text,
                        'annotations': [
                            {
                                'id': cat.id,
                                'annotator': cat.user.username,
                                'label': cat.label.text,
                                'perspective': self.get_user_perspective(example.project, cat.user)
                            } for cat in categories
                        ],
                        'discussion': self._get_discussion(example),
                        'labelsAgreement': self.get_label_agreement([{ 'label__text': cat.label.text, 'user__username': cat.user.username } for cat in categories])
                    })

            # Check for disagreements in spans
            if len(spans) > 1:
                span_labels = set([span.label.text for span in spans])
                if len(span_labels) > 1:
                    disagreements.append({
                        'id': example.id,
                        'textId': str(example.id),
                        'category': 'Span',
                        'type': 'Label Disagreement',
                        'annotators': [span.user.username for span in spans],
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
                        'discussion': self._get_discussion(example),
                        'labelsAgreement': self.get_label_agreement([{ 'label__text': span.label.text, 'user__username': span.user.username } for span in spans])
                    })

            # Check for disagreements in relations
            if len(relations) > 1:
                relation_types = set([rel.type.text for rel in relations])
                if len(relation_types) > 1:
                    disagreements.append({
                        'id': example.id,
                        'textId': str(example.id),
                        'category': 'Relation',
                        'type': 'Type Disagreement',
                        'annotators': [rel.user.username for rel in relations],
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
                        'discussion': self._get_discussion(example),
                        'labelsAgreement': self.get_label_agreement([{ 'label__text': rel.type.text, 'user__username': rel.user.username } for rel in relations])
                    })

        return disagreements

    def _get_disagreement_by_category(self, disagreements):
        category_counts = {}
        for disagreement in disagreements:
            category = disagreement['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return [{'category': k, 'count': v} for k, v in category_counts.items()]

    def _get_perspective_distribution(self, examples, perspective=None, annotation_date_filter=None):
        from collections import Counter
        perspectives = []
        for ex in examples:
            for cat in ex.categories.filter(**(annotation_date_filter or {})):
                if not perspective or self.get_user_perspective(ex.project, cat.user) == perspective:
                    perspectives.append(self.get_user_perspective(ex.project, cat.user))
            for span in ex.spans.filter(**(annotation_date_filter or {})):
                if not perspective or self.get_user_perspective(ex.project, span.user) == perspective:
                    perspectives.append(self.get_user_perspective(ex.project, span.user))
            for rel in ex.relations.filter(**(annotation_date_filter or {})):
                if not perspective or self.get_user_perspective(ex.project, rel.user) == perspective:
                    perspectives.append(self.get_user_perspective(ex.project, rel.user))
        counter = Counter(perspectives)
        return [{'perspective': k, 'count': v} for k, v in counter.items()]

    def _get_discussion(self, example):
        # This would need to be implemented based on your discussion model
        return []

    def _get_label_distribution(self, examples, perspective=None, annotation_date_filter=None):
        from collections import Counter
        labels = []
        for ex in examples:
            for cat in ex.categories.filter(**(annotation_date_filter or {})):
                if not perspective or self.get_user_perspective(ex.project, cat.user) == perspective:
                    labels.append(cat.label.text)
            # Repita para spans e relations se necessário
        return Counter(labels)

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

    def _get_perspective_patterns(self, examples, disagreements, perspective=None, annotation_date_filter=None):
        from collections import defaultdict
        patterns = defaultdict(lambda: {'total': 0, 'disagreements': 0, 'agreements': 0})
        for ex in examples:
            for cat in ex.categories.filter(**(annotation_date_filter or {})):
                if not perspective or self.get_user_perspective(ex.project, cat.user) == perspective:
                    p = self.get_user_perspective(ex.project, cat.user)
                    patterns[p]['total'] += 1
            for span in ex.spans.filter(**(annotation_date_filter or {})):
                if not perspective or self.get_user_perspective(ex.project, span.user) == perspective:
                    p = self.get_user_perspective(ex.project, span.user)
                    patterns[p]['total'] += 1
            for rel in ex.relations.filter(**(annotation_date_filter or {})):
                if not perspective or self.get_user_perspective(ex.project, rel.user) == perspective:
                    p = self.get_user_perspective(ex.project, rel.user)
                    patterns[p]['total'] += 1
        for d in disagreements:
            for ann in d['annotations']:
                p = ann.get('perspective', 'Default')
                patterns[p]['disagreements'] += 1
        result = []
        for p, v in patterns.items():
            agreements = v['total'] - v['disagreements']
            v['agreements'] = agreements if agreements >= 0 else 0
            if v['total'] > 0 or v['disagreements'] > 0:
                result.append({'perspective': p, **v})
        return result

    def get_label_agreement(self, annotations):
        from collections import Counter
        total = len(annotations)
        label_counts = Counter([a['label__text'] for a in annotations])
        result = []
        for label, count in label_counts.items():
            result.append({
                'label': label,
                'concordaram': count,
                'discordaram': total - count
            })
        return result