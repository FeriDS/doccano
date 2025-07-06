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

        # Buscar nomes dos campos de perspectiva
        perspective_field_names = {}
        if project_id:
            try:
                project_perspective = ProjectPerspective.objects.get(project=project_id)
                for field in project_perspective.perspective.fields.all():
                    perspective_field_names[str(field.id)] = field.name
            except Exception:
                pass

        # Montar dicionário de filtros aplicados para exportação
        applied_filters = {
            'Data Início': start_date,
            'Data Fim': end_date,
            'Categoria': label,
            'Status': resolved,
            'Perspectiva': perspective,
            'Exemplo': example_id,
        }
        # Adicionar campos de perspectiva com nome legível
        for k, v in perspective_field_filters.items():
            field_name = perspective_field_names.get(str(k), f'Campo {k}')
            applied_filters[f'Perspectiva {field_name}'] = v

        annotation_date_filter = {}
        if start_date and end_date:
            annotation_date_filter = {
                'created_at__gte': start_date,
                'updated_at__lte': end_date
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

        # Preparar exemplos com distribuição de labels para exportação
        examples_with_distribution = []
        for example in examples:
            if example.is_finished:  # Apenas exemplos finalizados
                # Calcular distribuição de labels para este exemplo
                example_label_dist = self._get_example_label_distribution(
                    example, perspective, annotation_date_filter, perspective_field_filters
                )
                
                examples_with_distribution.append({
                    'id': example.id,
                    'text': example.text,
                    'label_distribution': example_label_dist,
                    'is_resolved': example.is_resolved,
                    'annotation_start_date': example.created_at.strftime('%Y-%m-%d') if example.created_at else None,
                    'annotation_end_date': example.updated_at.strftime('%Y-%m-%d') if example.updated_at else None
                })

        statistics = {
            'statistics': {
                'disagreementRate': disagreement_rate,
                'perspectiveCount': unique_perspectives,
                'resolutionRate': (resolved_disagreements / disagreement_count * 100) if disagreement_count > 0 else 0,
                'averageAnnotationTime': self._calculate_avg_annotation_time(examples),
            },
            'examples': examples_with_distribution,  # Adicionar exemplos com distribuição
            'disagreements': disagreements,
            'disagreementByCategory': self._get_disagreement_by_category(disagreements),
            'perspectiveDistribution': self._get_perspective_distribution(examples, perspective, annotation_date_filter, perspective_field_filters),
            'labelDistribution': self._get_label_distribution(examples, perspective, annotation_date_filter, perspective_field_filters),
            'perspectivePatterns': self._get_perspective_patterns(examples, disagreements, perspective, annotation_date_filter, perspective_field_filters),
            'applied_filters': applied_filters
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

    def _get_example_label_distribution(self, example, perspective=None, annotation_date_filter=None, perspective_field_filters=None):
        """
        Calcula a distribuição de labels para um exemplo específico (apenas categorias).
        """
        from collections import Counter
        
        # Coletar apenas as categorias do exemplo
        categories = Category.objects.filter(example=example)
        
        # Aplicar filtros de data se especificados
        if annotation_date_filter:
            categories = categories.filter(**annotation_date_filter)
        
        # Filtrar por perspectiva se necessário
        if perspective or perspective_field_filters:
            categories = [cat for cat in categories if self.user_matches_perspective_filters(example.project, cat.user, perspective, perspective_field_filters)]
        
        # Contar labels
        label_counts = Counter()
        for cat in categories:
            label_counts[cat.label.text] += 1
        
        # Calcular percentagens
        total_annotations = sum(label_counts.values())
        if total_annotations == 0:
            return {}
        
        distribution = {}
        for label, count in label_counts.items():
            percentage = (count / total_annotations) * 100
            distribution[label] = round(percentage, 2)
        
        return distribution

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
        if is_post or request.method == 'POST':
            chartImages = request.data.get('chartImages')
            screenExamples = request.data.get('screenExamples')
        else:
            chartImages = None
            screenExamples = None
        statistics_data = self.get_statistics(request).data
        if export_format == 'csv':
            return self.export_to_csv(statistics_data, screenExamples)
        elif export_format == 'pdf':
            return self.export_to_pdf(statistics_data, chartImages, screenExamples)
        else:
            return Response({"error": "Unsupported export format"}, status=status.HTTP_400_BAD_REQUEST)

    def export_to_csv(self, statistics_data, screenExamples=None):
        buffer = io.StringIO()
        
        # Seção 1: Resumo Geral
        buffer.write('RESUMO GERAL\n')
        buffer.write('-' * 20 + '\n')
        buffer.write('Métrica;Valor\n')
        buffer.write(f'Total de Exemplos Finalizados;{len(statistics_data.get("examples", []))}\n')
        filtros = statistics_data.get('applied_filters', {})
        filtros_written = False
        for k, v in filtros.items():
            if v:
                buffer.write(f'Filtros Aplicados;{k}: {v}\n')
                filtros_written = True
        if not filtros_written:
            buffer.write('Filtros Aplicados;Nenhum filtro aplicado\n')
        buffer.write('\n')

        # Seção 2: Distribuição de Labels por Exemplo (tabelas igual ao PDF)
        buffer.write('DISTRIBUIÇÃO DE LABELS POR EXEMPLO\n')
        buffer.write('-' * 40 + '\n')
        
        examples = screenExamples if screenExamples is not None else statistics_data.get("examples", [])
        if examples:
            for i, example in enumerate(examples):
                example_text = example.get('text', f'Exemplo {i+1}')
                # Truncar texto muito longo para o título
                if len(example_text) > 100:
                    example_text = example_text[:97] + '...'
                buffer.write(f'{example_text}\n')
                buffer.write('-' * len(example_text) + '\n')
                labels_data = example.get('labelsChartData', {})
                abstraction_data = example.get('abstractionChartData', {})
                if not labels_data and not abstraction_data and example.get('label_distribution'):
                    labels_data = {'labels': list(example['label_distribution'].keys()), 'data': list(example['label_distribution'].values())}
                    abstraction_data = {'labels': [], 'data': []}
                all_labels = list(labels_data.get('labels', [])) + [l for l in abstraction_data.get('labels', []) if l not in labels_data.get('labels', [])]
                regular_total = 0
                non_voted_total = 0
                buffer.write('Label;Percentagem (%)\n')
                for label in all_labels:
                    if label in labels_data.get('labels', []):
                        idx = labels_data['labels'].index(label)
                        value = labels_data['data'][idx]
                    elif label in abstraction_data.get('labels', []):
                        idx = abstraction_data['labels'].index(label)
                        value = abstraction_data['data'][idx]
                    else:
                        value = 0
                    buffer.write(f'{label};{value}%\n')
                    if (label.lower().find('abstração') != -1 or 
                        label.lower().find('abstraction') != -1 or 
                        label.lower().find('abstenção') != -1 or
                        label.lower().find('abstention') != -1 or
                        label.lower().find('null') != -1 or
                        label in ['Null', 'null']):
                        if label in abstraction_data.get('labels', []):
                            idx = abstraction_data['labels'].index(label)
                            non_voted_total += float(abstraction_data['data'][idx])
                        elif label in labels_data.get('labels', []):
                            idx = labels_data['labels'].index(label)
                            non_voted_total += float(labels_data['data'][idx])
                    else:
                        if label in labels_data.get('labels', []):
                            idx = labels_data['labels'].index(label)
                            regular_total += float(labels_data['data'][idx])
                        elif label in abstraction_data.get('labels', []):
                            idx = abstraction_data['labels'].index(label)
                            regular_total += float(abstraction_data['data'][idx])
                buffer.write(f'Total Labels Regulares;{regular_total:.1f}%\n')
                buffer.write(f'Total Non-Voted;{non_voted_total:.1f}%\n')
                buffer.write('\n')
        else:
            buffer.write('Nenhum exemplo exibido na tela para os filtros aplicados.\n\n')
        
        # Adicionar BOM UTF-8 para compatibilidade com Excel
        bom = '\ufeff'
        response = HttpResponse(
            bom + buffer.getvalue(),
            content_type='text/csv; charset=utf-8'
        )
        response['Content-Disposition'] = 'attachment; filename=estatisticas_por_texto.csv'
        return response

    def export_to_pdf(self, statistics_data, chartImages=None, screenExamples=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # DEBUG: Verificar chartImages recebido
        print('DEBUG chartImages:', chartImages)
        
        # Título principal
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
        elements.append(Paragraph("Estatísticas por Texto", title_style))
        elements.append(Spacer(1, 20))
        
        # Seção 1: Resumo Geral
        elements.append(Paragraph("Resumo Geral", styles['Heading2']))
            elements.append(Spacer(1, 10))
        
        # Montar descrição dos filtros aplicados
        filtros = statistics_data.get('applied_filters', {})
        filtros_strs = []
        for k, v in filtros.items():
            if v:
                filtros_strs.append(f"{k}: {v}")
        filtros_descr = '\n'.join(filtros_strs) if filtros_strs else 'Nenhum filtro aplicado'
        
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de Exemplos Finalizados', str(len(statistics_data.get("examples", [])))],
            ['Filtros Aplicados', filtros_descr]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Seção 2: Distribuição de Labels por Exemplo
        elements.append(Paragraph("Distribuição de Labels por Exemplo", styles['Heading2']))
        elements.append(Spacer(1, 10))
        examples = screenExamples if screenExamples is not None else statistics_data.get("examples", [])
        if examples:
            for i, example in enumerate(examples[:10]):  # Limitar a 10 exemplos para não sobrecarregar
                elements.append(Paragraph(f"Exemplo {example['id']}: {example['text'][:50]}...", styles['Heading3']))
                elements.append(Spacer(1, 5))
                # Inserir gráficos se enviados
                chart_key_str = str(example['id'])
                chart_key_int = int(example['id']) if isinstance(example['id'], str) and str(example['id']).isdigit() else example['id']
                imgs = None
                if chartImages:
                    imgs = chartImages.get(chart_key_str) or chartImages.get(chart_key_int)
                print('DEBUG imgs for example', example['id'], ':', imgs)
                if imgs:
                    if imgs.get('labels'):
                        print('DEBUG labels image (first 100 chars):', imgs['labels'][:100])
                        try:
                            imgdata = base64.b64decode(imgs['labels'].split(',')[1] if ',' in imgs['labels'] else imgs['labels'])
                            img_buffer = io.BytesIO(imgdata)
                            img = RLImage(img_buffer, width=4*inch, height=2.5*inch)
                            elements.append(Paragraph("Gráfico: Distribuição de Labels", styles['Normal']))
                            elements.append(img)
                            elements.append(Spacer(1, 8))
                        except Exception as e:
                            print('ERROR ao inserir imagem de labels no PDF:', e)
                    if imgs.get('abstraction'):
                        print('DEBUG abstraction image (first 100 chars):', imgs['abstraction'][:100])
                        try:
                            imgdata = base64.b64decode(imgs['abstraction'].split(',')[1] if ',' in imgs['abstraction'] else imgs['abstraction'])
                            img_buffer = io.BytesIO(imgdata)
                            img = RLImage(img_buffer, width=4*inch, height=2.5*inch)
                            elements.append(Paragraph("Gráfico: Abstenção e Null", styles['Normal']))
                            elements.append(img)
                            elements.append(Spacer(1, 8))
                        except Exception as e:
                            print('ERROR ao inserir imagem de abstenção no PDF:', e)
                # Montar tabela de labels exatamente como no gráfico
                labels_data = example.get('labelsChartData', {})
                abstraction_data = example.get('abstractionChartData', {})
                # Juntar todas as labels dos dois gráficos
                all_labels = list(labels_data.get('labels', [])) + [l for l in abstraction_data.get('labels', []) if l not in labels_data.get('labels', [])]
                if all_labels:
                    dist_data = [['Label', 'Percentagem (%)']]
                    for label in all_labels:
                        # Buscar valor na ordem: labelsChartData, abstractionChartData
                        if label in labels_data.get('labels', []):
                            idx = labels_data['labels'].index(label)
                            value = labels_data['data'][idx]
                        elif label in abstraction_data.get('labels', []):
                            idx = abstraction_data['labels'].index(label)
                            value = abstraction_data['data'][idx]
                        else:
                            value = 0
                        dist_data.append([label, f"{value}%"])
                    # Calcular totais
                    regular_total = 0
                    non_voted_total = 0
                    for label in all_labels:
                        if (label.lower().find('abstração') != -1 or 
                            label.lower().find('abstraction') != -1 or 
                            label.lower().find('abstenção') != -1 or
                            label.lower().find('abstention') != -1 or
                            label.lower().find('null') != -1 or
                            label in ['Null', 'null']):
                            # Buscar valor
                            if label in abstraction_data.get('labels', []):
                                idx = abstraction_data['labels'].index(label)
                                non_voted_total += float(abstraction_data['data'][idx])
                            elif label in labels_data.get('labels', []):
                                idx = labels_data['labels'].index(label)
                                non_voted_total += float(labels_data['data'][idx])
                        else:
                            if label in labels_data.get('labels', []):
                                idx = labels_data['labels'].index(label)
                                regular_total += float(labels_data['data'][idx])
                            elif label in abstraction_data.get('labels', []):
                                idx = abstraction_data['labels'].index(label)
                                regular_total += float(abstraction_data['data'][idx])
                    dist_data.append(['', ''])
                    dist_data.append(['Total Labels Regulares', f"{regular_total:.1f}%"])
                    dist_data.append(['Total Non-Voted', f"{non_voted_total:.1f}%"])
                    dist_table = Table(dist_data, colWidths=[3*inch, 1.5*inch])
                    dist_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
                        ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
                        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -2), 9),
                        ('BACKGROUND', (0, -2), (-1, -1), colors.lightgrey),
                        ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                    ]))
                    elements.append(dist_table)
                    elements.append(Spacer(1, 15))
        else:
            elements.append(Paragraph("Nenhum exemplo exibido na tela para os filtros aplicados.", styles['Normal']))
            elements.append(Spacer(1, 15))
        
        doc.build(elements)
        buffer.seek(0)
        response = HttpResponse(
            buffer,
            content_type='application/pdf'
        )
        response['Content-Disposition'] = 'attachment; filename=estatisticas_por_texto.pdf'
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


class ExportStatisticsAPI(APIView):
    """
    API para exportação de relatórios de estatísticas em formatos CSV e PDF.
    
    Endpoints:
    - GET /v1/projects/{project_id}/statistics/export/csv - Exporta estatísticas em CSV
    - GET /v1/projects/{project_id}/statistics/export/pdf - Exporta estatísticas em PDF
    
    Parâmetros de query (opcionais):
    - start_date: Data de início (YYYY-MM-DD)
    - end_date: Data de fim (YYYY-MM-DD)
    - label: Filtro por categoria/label
    - resolved: Filtro por status resolvido (true/false)
    - perspective: Filtro por perspectiva
    - perspective_{field_id}: Filtros específicos de campos de perspectiva
    """
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]

    def get(self, request, *args, **kwargs):
        """
        Exporta estatísticas baseado no formato especificado na URL.
        """
        project_id = self.kwargs["project_id"]
        path = request.path
        
        if path.endswith('/csv'):
            return self.export_csv(request)
        elif path.endswith('/pdf'):
            return self.export_pdf(request)
        else:
            return Response(
                {"error": "Formato de exportação não especificado. Use /csv ou /pdf"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def export_csv(self, request):
            statistics_view = AnnotationStatisticsAPI()
            statistics_view.kwargs = self.kwargs
            statistics_data = statistics_view.get_statistics(request).data
        screenExamples = request.data.get('screenExamples') if hasattr(request, 'data') else None
        return statistics_view.export_to_csv(statistics_data, screenExamples)

    def export_pdf(self, request):
        try:
            statistics_view = AnnotationStatisticsAPI()
            statistics_view.kwargs = self.kwargs
            statistics_data = statistics_view.get_statistics(request).data
            chartImages = request.data.get('chartImages') if request.method == 'POST' else None
            screenExamples = request.data.get('screenExamples') if request.method == 'POST' else None
            return statistics_view.export_to_pdf(statistics_data, chartImages, screenExamples)
        except Exception as e:
            return Response(
                {"error": f"Erro ao exportar PDF: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, *args, **kwargs):
        """
        Método POST para compatibilidade com a view principal.
        Redireciona para GET com base no formato especificado.
        """
        return self.get(request, *args, **kwargs)