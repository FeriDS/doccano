from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
import pandas as pd
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import base64
from django.http import HttpResponse

from examples.models import Example
from labels.models import Category, Span, Relation
from projects.models import Project
from projects.permissions import IsProjectAdmin, IsProjectStaffAndReadOnly
from perspectives.models import ProjectPerspective, UserPerspectiveAnswer


class AnnotationStatisticsAPI(APIView):
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]

    def get(self, request, *args, **kwargs):
        export_format = request.query_params.get('export_format')
        if export_format:
            return self.export_statistics(request, export_format)
        
        return self.get_statistics(request)

    def get_statistics(self, request):
        project_id = self.kwargs["project_id"]
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        annotator_id = request.query_params.get('annotator')
        perspective = request.query_params.get('perspective')
        label = request.query_params.get('label')
        resolved = request.query_params.get('resolved')
        finished = request.query_params.get('finished')
        example_id = request.query_params.get('example_id')

        # Processar filtros específicos de campos de perspectiva
        perspective_field_filters = {}
        for key, value in request.query_params.items():
            if key.startswith('perspective_') and value:
                field_id = key.replace('perspective_', '')
                perspective_field_filters[field_id] = value

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
        
        # Aplicar filtros de perspectiva (tanto o filtro geral quanto os filtros específicos de campos)
        if perspective or perspective_field_filters:
            filtered_examples = set()
            for ex in examples:
                found = False
                for cat in ex.categories.filter(**annotation_date_filter):
                    if self.user_matches_perspective_filters(ex.project, cat.user, perspective, perspective_field_filters):
                        filtered_examples.add(ex.id)
                        found = True
                        break
                if not found:
                    for span in ex.spans.filter(**annotation_date_filter):
                        if self.user_matches_perspective_filters(ex.project, span.user, perspective, perspective_field_filters):
                            filtered_examples.add(ex.id)
                            found = True
                            break
                if not found:
                    for rel in ex.relations.filter(**annotation_date_filter):
                        if self.user_matches_perspective_filters(ex.project, rel.user, perspective, perspective_field_filters):
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
        disagreements = self._find_disagreements(examples, perspective, annotation_date_filter, perspective_field_filters)
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
            'perspectiveDistribution': self._get_perspective_distribution(examples, perspective, annotation_date_filter, perspective_field_filters),
            'labelDistribution': self._get_label_distribution(examples, perspective, annotation_date_filter, perspective_field_filters),
            'perspectivePatterns': self._get_perspective_patterns(examples, disagreements, perspective, annotation_date_filter, perspective_field_filters)
        }

        return Response(data=statistics, status=status.HTTP_200_OK)

    def user_matches_perspective_filters(self, project, user, perspective=None, perspective_field_filters=None):
        """
        Verifica se um usuário atende aos critérios de filtro de perspectiva.
        """
        try:
            project_perspective = ProjectPerspective.objects.get(project=project)
            user_perspective = UserPerspectiveAnswer.objects.filter(
                project_perspective=project_perspective,
                user=user
            ).first()
            
            if not user_perspective:
                return False
            
            # Verificar filtro geral de perspectiva
            if perspective:
                user_perspective_value = user_perspective.field_values.get('role', 'Default')
                if user_perspective_value != perspective:
                    return False
            
            # Verificar filtros específicos de campos de perspectiva
            if perspective_field_filters:
                for field_id, expected_value in perspective_field_filters.items():
                    # Buscar o nome do campo pelo ID
                    try:
                        field = project_perspective.perspective.fields.get(id=field_id)
                        field_name = field.name
                        user_value = user_perspective.field_values.get(field_name)
                        if user_value != expected_value:
                            return False
                    except:
                        # Se não conseguir encontrar o campo, verificar se existe no field_values
                        user_value = user_perspective.field_values.get(field_id)
                        if user_value != expected_value:
                            return False
            
            return True
            
        except ProjectPerspective.DoesNotExist:
            return False

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

    def _find_disagreements(self, examples, perspective=None, annotation_date_filter=None, perspective_field_filters=None):
        disagreements = []
        for example in examples:
            categories = Category.objects.filter(example=example, **(annotation_date_filter or {}))
            spans = Span.objects.filter(example=example, **(annotation_date_filter or {}))
            relations = Relation.objects.filter(example=example, **(annotation_date_filter or {}))

            # Filtrar anotações pelo role/perspective se necessário
            if perspective or perspective_field_filters:
                categories = [cat for cat in categories if self.user_matches_perspective_filters(example.project, cat.user, perspective, perspective_field_filters)]
                spans = [span for span in spans if self.user_matches_perspective_filters(example.project, span.user, perspective, perspective_field_filters)]
                relations = [rel for rel in relations if self.user_matches_perspective_filters(example.project, rel.user, perspective, perspective_field_filters)]

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

    def _get_perspective_distribution(self, examples, perspective=None, annotation_date_filter=None, perspective_field_filters=None):
        from collections import Counter
        perspectives = []
        for ex in examples:
            for cat in ex.categories.filter(**(annotation_date_filter or {})):
                if not perspective or self.user_matches_perspective_filters(ex.project, cat.user, perspective, perspective_field_filters):
                    perspectives.append(self.get_user_perspective(ex.project, cat.user))
            for span in ex.spans.filter(**(annotation_date_filter or {})):
                if not perspective or self.user_matches_perspective_filters(ex.project, span.user, perspective, perspective_field_filters):
                    perspectives.append(self.get_user_perspective(ex.project, span.user))
            for rel in ex.relations.filter(**(annotation_date_filter or {})):
                if not perspective or self.user_matches_perspective_filters(ex.project, rel.user, perspective, perspective_field_filters):
                    perspectives.append(self.get_user_perspective(ex.project, rel.user))
        counter = Counter(perspectives)
        return [{'perspective': k, 'count': v} for k, v in counter.items()]

    def _get_discussion(self, example):
        # This would need to be implemented based on your discussion model
        return []

    def _get_label_distribution(self, examples, perspective=None, annotation_date_filter=None, perspective_field_filters=None):
        from collections import Counter
        labels = []
        for ex in examples:
            for cat in ex.categories.filter(**(annotation_date_filter or {})):
                if not perspective or self.user_matches_perspective_filters(ex.project, cat.user, perspective, perspective_field_filters):
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

    def _get_perspective_patterns(self, examples, disagreements, perspective=None, annotation_date_filter=None, perspective_field_filters=None):
        from collections import defaultdict
        patterns = defaultdict(lambda: {'total': 0, 'disagreements': 0, 'agreements': 0})
        for ex in examples:
            for cat in ex.categories.filter(**(annotation_date_filter or {})):
                if not perspective or self.user_matches_perspective_filters(ex.project, cat.user, perspective, perspective_field_filters):
                    p = self.get_user_perspective(ex.project, cat.user)
                    patterns[p]['total'] += 1
            for span in ex.spans.filter(**(annotation_date_filter or {})):
                if not perspective or self.user_matches_perspective_filters(ex.project, span.user, perspective, perspective_field_filters):
                    p = self.get_user_perspective(ex.project, span.user)
                    patterns[p]['total'] += 1
            for rel in ex.relations.filter(**(annotation_date_filter or {})):
                if not perspective or self.user_matches_perspective_filters(ex.project, rel.user, perspective, perspective_field_filters):
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

    def post(self, request, *args, **kwargs):
        export_format = request.data.get('export_format')
        if export_format == 'pdf':
            return self.export_statistics(request, export_format, is_post=True)
        return Response({"error": "Unsupported export format"}, status=status.HTTP_400_BAD_REQUEST)

    def export_statistics(self, request, export_format, is_post=False):
        project_id = self.kwargs["project_id"]
        if is_post:
            chart_image = request.data.get('chartImage')
        else:
            chart_image = request.query_params.get('chartImage')
        statistics_data = self.get_statistics(request).data
        if export_format == 'csv':
            return self.export_to_csv(statistics_data)
        elif export_format == 'pdf':
            return self.export_to_pdf(statistics_data, chart_image)
        else:
            return Response({"error": "Unsupported export format"}, status=status.HTTP_400_BAD_REQUEST)

    def export_to_csv(self, statistics_data):
        buffer = io.StringIO()
        # Remove metrics table: do not write stats_df
        # Label Distribution (Pie Chart Data)
        total_labels = sum(statistics_data['labelDistribution'].values())
        label_dist_df = pd.DataFrame({
            'Label': list(statistics_data['labelDistribution'].keys()),
            'Count': list(statistics_data['labelDistribution'].values()),
            'Percentage': [f"{(count/total_labels*100):.2f}%" for count in statistics_data['labelDistribution'].values()]
        })
        perspective_dist_df = pd.DataFrame(statistics_data['perspectiveDistribution'])
        if not perspective_dist_df.empty:
            perspective_dist_df['Percentage'] = perspective_dist_df['count'].apply(
                lambda x: f"{(x/perspective_dist_df['count'].sum()*100):.2f}%"
            )
        disagreement_cat_df = pd.DataFrame(statistics_data['disagreementByCategory'])
        if not disagreement_cat_df.empty:
            total_disagreements = disagreement_cat_df['count'].sum()
            disagreement_cat_df['Percentage'] = disagreement_cat_df['count'].apply(
                lambda x: f"{(x/total_disagreements*100):.2f}%"
            )
        perspective_patterns_df = pd.DataFrame(statistics_data['perspectivePatterns'])
        if not perspective_patterns_df.empty:
            perspective_patterns_df['Agreement Rate'] = perspective_patterns_df.apply(
                lambda x: f"{(x['agreements']/x['total']*100):.2f}%" if x['total'] > 0 else "0%",
                axis=1
            )
            perspective_patterns_df['Disagreement Rate'] = perspective_patterns_df.apply(
                lambda x: f"{(x['disagreements']/x['total']*100):.2f}%" if x['total'] > 0 else "0%",
                axis=1
            )
        buffer.write('=== Label Distribution (Pie Chart) ===\n')
        label_dist_df.to_csv(buffer, index=False)
        if not perspective_dist_df.empty:
            buffer.write('\n=== Perspective Distribution ===\n')
            perspective_dist_df.to_csv(buffer, index=False)
        if not disagreement_cat_df.empty:
            buffer.write('\n=== Disagreement by Category ===\n')
            disagreement_cat_df.to_csv(buffer, index=False)
        if not perspective_patterns_df.empty:
            buffer.write('\n=== Perspective Patterns ===\n')
            perspective_patterns_df.to_csv(buffer, index=False)
        response = Response(
            buffer.getvalue(),
            content_type='text/csv'
        )
        response['Content-Disposition'] = 'attachment; filename=annotation_statistics.csv'
        return response

    def export_to_pdf(self, statistics_data, chart_image=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
        elements.append(Paragraph("Annotation Statistics Report", title_style))
        elements.append(Spacer(1, 20))
        # Add the chart image if provided
        if chart_image:
            if chart_image.startswith('data:image/png;base64,'):
                chart_image = chart_image.split(',')[1]
            imgdata = base64.b64decode(chart_image)
            img_buffer = io.BytesIO(imgdata)
            img = RLImage(img_buffer, width=300, height=300)
            elements.append(Paragraph("Label Distribution (Pie Chart)", styles['Heading2']))
            elements.append(img)
            elements.append(Spacer(1, 20))
        # Remove metrics table (do not add statistics table)
        # Add disagreements table if there are any
        if statistics_data['disagreements']:
            elements.append(Paragraph("Disagreements", styles['Heading2']))
            elements.append(Spacer(1, 10))
            disagreements_data = [['Text ID', 'Category', 'Type', 'Status']]
            for d in statistics_data['disagreements']:
                disagreements_data.append([
                    d['textId'],
                    d['category'],
                    d['type'],
                    d['status']
                ])
            disagreements_table = Table(disagreements_data, colWidths=[1.5*inch, 2*inch, 2*inch, 1.5*inch])
            disagreements_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(disagreements_table)
        doc.build(elements)
        buffer.seek(0)
        response = HttpResponse(
            buffer,
            content_type='application/pdf'
        )
        response['Content-Disposition'] = 'attachment; filename=annotation_statistics.pdf'
        return response

    @action(detail=True, methods=['get'])
    def label_distribution(self, request, project_id, example_id):
        """
        Endpoint para obter distribuição de labels de um exemplo específico com suporte a filtros de perspectiva.
        """
        try:
            # Processar filtros específicos de campos de perspectiva
            perspective_field_filters = {}
            for key, value in request.query_params.items():
                if key.startswith('perspective_') and value:
                    field_id = key.replace('perspective_', '')
                    perspective_field_filters[field_id] = value

            # Buscar o exemplo
            example = Example.objects.get(id=example_id, project=project_id)
            
            # Coletar todas as anotações do exemplo
            categories = Category.objects.filter(example=example)
            spans = Span.objects.filter(example=example)
            relations = Relation.objects.filter(example=example)
            
            # Se há filtros de perspectiva, precisamos calcular o total de usuários elegíveis
            total_eligible_users = 0
            users_with_annotations = set()
            
            if perspective_field_filters:
                # Contar usuários que atendem aos critérios de filtro
                project_perspective = ProjectPerspective.objects.get(project=example.project)
                all_user_answers = UserPerspectiveAnswer.objects.filter(project_perspective=project_perspective)
                
                for user_answer in all_user_answers:
                    if self.user_matches_perspective_filters(example.project, user_answer.user, None, perspective_field_filters):
                        total_eligible_users += 1
                
                # Filtrar categorias por perspectiva
                filtered_categories = []
                for cat in categories:
                    if self.user_matches_perspective_filters(example.project, cat.user, None, perspective_field_filters):
                        filtered_categories.append(cat)
                        users_with_annotations.add(cat.user.id)
                categories = filtered_categories
                
                # Filtrar spans por perspectiva
                filtered_spans = []
                for span in spans:
                    if self.user_matches_perspective_filters(example.project, span.user, None, perspective_field_filters):
                        filtered_spans.append(span)
                        users_with_annotations.add(span.user.id)
                spans = filtered_spans
                
                # Filtrar relations por perspectiva
                filtered_relations = []
                for rel in relations:
                    if self.user_matches_perspective_filters(example.project, rel.user, None, perspective_field_filters):
                        filtered_relations.append(rel)
                        users_with_annotations.add(rel.user.id)
                relations = filtered_relations
            else:
                # Sem filtros, contar todos os usuários que fizeram anotações
                for cat in categories:
                    users_with_annotations.add(cat.user.id)
                for span in spans:
                    users_with_annotations.add(span.user.id)
                for rel in relations:
                    users_with_annotations.add(rel.user.id)
                total_eligible_users = len(users_with_annotations)
            
            # Calcular distribuição de labels
            from collections import Counter
            label_counts = Counter()
            
            # Contar labels de categorias
            for cat in categories:
                label_counts[cat.label.text] += 1
            
            # Contar labels de spans
            for span in spans:
                label_counts[span.label.text] += 1
            
            # Contar labels de relations
            for rel in relations:
                label_counts[rel.type.text] += 1
            
            # Separar labels regulares de labels de abstenção/null
            regular_labels = {}
            abstention_labels = {}
            
            for label, count in label_counts.items():
                label_lower = label.lower()
                # Identificar labels de abstenção/null
                if ('abstração' in label_lower or 
                    'abstraction' in label_lower or 
                    'abstenção' in label_lower or
                    'abstention' in label_lower or
                    'null' in label_lower or
                    label == 'Null' or
                    label == 'null'):
                    abstention_labels[label] = count
                else:
                    regular_labels[label] = count
            
            # Calcular percentagens
            total_annotations = sum(label_counts.values())
            
            if total_eligible_users == 0:
                return Response({'labels': {}, 'null': 0}, status=status.HTTP_200_OK)
            
            # Calcular percentagens para labels regulares
            distribution = {}
            for label, count in regular_labels.items():
                percentage = (count / total_eligible_users) * 100
                distribution[label] = round(percentage, 2)
            
            # Calcular percentagem total de abstenção/null
            total_abstention_count = sum(abstention_labels.values())
            users_without_annotations = total_eligible_users - len(users_with_annotations)
            total_abstention_percentage = ((total_abstention_count + users_without_annotations) / total_eligible_users) * 100
            
            return Response({
                'labels': distribution,
                'null': round(total_abstention_percentage, 2)
            }, status=status.HTTP_200_OK)
            
        except Example.DoesNotExist:
            return Response({"error": "Example not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LabelDistributionAPI(APIView):
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]

    def get(self, request, project_id, example_id):
        """
        Endpoint para obter distribuição de labels de um exemplo específico com suporte a filtros de perspectiva.
        """
        try:
            # Processar filtros específicos de campos de perspectiva
            perspective_field_filters = {}
            for key, value in request.query_params.items():
                if key.startswith('perspective_') and value:
                    field_id = key.replace('perspective_', '')
                    perspective_field_filters[field_id] = value

            # Buscar o exemplo
            example = Example.objects.get(id=example_id, project=project_id)
            
            # Coletar todas as anotações do exemplo
            categories = Category.objects.filter(example=example)
            spans = Span.objects.filter(example=example)
            relations = Relation.objects.filter(example=example)
            
            # Se há filtros de perspectiva, precisamos calcular o total de usuários elegíveis
            total_eligible_users = 0
            users_with_annotations = set()
            
            if perspective_field_filters:
                # Contar usuários que atendem aos critérios de filtro
                project_perspective = ProjectPerspective.objects.get(project=example.project)
                all_user_answers = UserPerspectiveAnswer.objects.filter(project_perspective=project_perspective)
                
                for user_answer in all_user_answers:
                    if self.user_matches_perspective_filters(example.project, user_answer.user, None, perspective_field_filters):
                        total_eligible_users += 1
                
                # Filtrar categorias por perspectiva
                filtered_categories = []
                for cat in categories:
                    if self.user_matches_perspective_filters(example.project, cat.user, None, perspective_field_filters):
                        filtered_categories.append(cat)
                        users_with_annotations.add(cat.user.id)
                categories = filtered_categories
                
                # Filtrar spans por perspectiva
                filtered_spans = []
                for span in spans:
                    if self.user_matches_perspective_filters(example.project, span.user, None, perspective_field_filters):
                        filtered_spans.append(span)
                        users_with_annotations.add(span.user.id)
                spans = filtered_spans
                
                # Filtrar relations por perspectiva
                filtered_relations = []
                for rel in relations:
                    if self.user_matches_perspective_filters(example.project, rel.user, None, perspective_field_filters):
                        filtered_relations.append(rel)
                        users_with_annotations.add(rel.user.id)
                relations = filtered_relations
            else:
                # Sem filtros, contar todos os usuários que fizeram anotações
                for cat in categories:
                    users_with_annotations.add(cat.user.id)
                for span in spans:
                    users_with_annotations.add(span.user.id)
                for rel in relations:
                    users_with_annotations.add(rel.user.id)
                total_eligible_users = len(users_with_annotations)
            
            # Calcular distribuição de labels
            from collections import Counter
            label_counts = Counter()
            
            # Contar labels de categorias
            for cat in categories:
                label_counts[cat.label.text] += 1
            
            # Contar labels de spans
            for span in spans:
                label_counts[span.label.text] += 1
            
            # Contar labels de relations
            for rel in relations:
                label_counts[rel.type.text] += 1
            
            # Separar labels regulares de labels de abstenção/null
            regular_labels = {}
            abstention_labels = {}
            
            for label, count in label_counts.items():
                label_lower = label.lower()
                # Identificar labels de abstenção/null
                if ('abstração' in label_lower or 
                    'abstraction' in label_lower or 
                    'abstenção' in label_lower or
                    'abstention' in label_lower or
                    'null' in label_lower or
                    label == 'Null' or
                    label == 'null'):
                    abstention_labels[label] = count
                else:
                    regular_labels[label] = count
            
            # Calcular percentagens
            total_annotations = sum(label_counts.values())
            
            if total_eligible_users == 0:
                return Response({'labels': {}, 'null': 0}, status=status.HTTP_200_OK)
            
            # Calcular percentagens para labels regulares
            distribution = {}
            for label, count in regular_labels.items():
                percentage = (count / total_eligible_users) * 100
                distribution[label] = round(percentage, 2)
            
            # Calcular percentagem total de abstenção/null
            total_abstention_count = sum(abstention_labels.values())
            users_without_annotations = total_eligible_users - len(users_with_annotations)
            total_abstention_percentage = ((total_abstention_count + users_without_annotations) / total_eligible_users) * 100
            
            return Response({
                'labels': distribution,
                'null': round(total_abstention_percentage, 2)
            }, status=status.HTTP_200_OK)
            
        except Example.DoesNotExist:
            return Response({"error": "Example not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def user_matches_perspective_filters(self, project, user, perspective=None, perspective_field_filters=None):
        """
        Verifica se um usuário atende aos critérios de filtro de perspectiva.
        """
        try:
            project_perspective = ProjectPerspective.objects.get(project=project)
            user_perspective = UserPerspectiveAnswer.objects.filter(
                project_perspective=project_perspective,
                user=user
            ).first()
            
            if not user_perspective:
                return False
            
            # Verificar filtro geral de perspectiva
            if perspective:
                user_perspective_value = user_perspective.field_values.get('role', 'Default')
                if user_perspective_value != perspective:
                    return False
            
            # Verificar filtros específicos de campos de perspectiva
            if perspective_field_filters:
                for field_id, expected_value in perspective_field_filters.items():
                    # Buscar o nome do campo pelo ID
                    try:
                        field = project_perspective.perspective.fields.get(id=field_id)
                        field_name = field.name
                        user_value = user_perspective.field_values.get(field_name)
                        if user_value != expected_value:
                            return False
                    except:
                        # Se não conseguir encontrar o campo, verificar se existe no field_values
                        user_value = user_perspective.field_values.get(field_id)
                        if user_value != expected_value:
                            return False
            
            return True
            
        except ProjectPerspective.DoesNotExist:
            return False