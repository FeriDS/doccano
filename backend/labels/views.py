from functools import partial
from typing import Type

from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import CanEditLabel
from .serializers import (
    BoundingBoxSerializer,
    CategorySerializer,
    RelationSerializer,
    SegmentationSerializer,
    SpanSerializer,
    TextLabelSerializer,
)
from labels.models import (
    BoundingBox,
    Category,
    Label,
    Relation,
    Segmentation,
    Span,
    TextLabel,
    DatasetVersion,
)
from projects.models import Project
from projects.permissions import IsProjectMember
from perspectives.permissions import HasCompletePerspective


class BaseListAPI(generics.ListCreateAPIView):
    label_class: Type[Label]
    pagination_class = None
    permission_classes = [
        IsAuthenticated & 
        IsProjectMember & 
        HasCompletePerspective
    ]
    swagger_schema = None

    @property
    def project(self):
        return get_object_or_404(Project, pk=self.kwargs["project_id"])

    def get_queryset(self):
        queryset = self.label_class.objects.filter(example=self.kwargs["example_id"])
        if not self.project.collaborative_annotation:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        request.data["example"] = self.kwargs["example_id"]
        try:
            response = super().create(request, args, kwargs)
        except ValidationError as err:
            response = Response({"detail": err.messages}, status=status.HTTP_400_BAD_REQUEST)
        return response

    def perform_create(self, serializer):
        serializer.save(example_id=self.kwargs["example_id"], user=self.request.user)

    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BaseDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = "annotation_id"
    swagger_schema = None

    @property
    def project(self):
        return get_object_or_404(Project, pk=self.kwargs["project_id"])

    def get_permissions(self):
        if self.project.collaborative_annotation:
            self.permission_classes = [IsAuthenticated & IsProjectMember]
        else:
            self.permission_classes = [IsAuthenticated & IsProjectMember & partial(CanEditLabel, self.queryset)]
        return super().get_permissions()


class CategoryListAPI(BaseListAPI):
    label_class = Category
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        if self.project.single_class_classification:
            self.get_queryset().delete()
        return super().create(request, args, kwargs)


class CategoryDetailAPI(BaseDetailAPI):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SpanListAPI(BaseListAPI):
    label_class = Span
    serializer_class = SpanSerializer


class SpanDetailAPI(BaseDetailAPI):
    queryset = Span.objects.all()
    serializer_class = SpanSerializer


class TextLabelListAPI(BaseListAPI):
    label_class = TextLabel
    serializer_class = TextLabelSerializer


class TextLabelDetailAPI(BaseDetailAPI):
    queryset = TextLabel.objects.all()
    serializer_class = TextLabelSerializer


class RelationList(BaseListAPI):
    label_class = Relation
    serializer_class = RelationSerializer


class RelationDetail(BaseDetailAPI):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer


class BoundingBoxListAPI(BaseListAPI):
    label_class = BoundingBox
    serializer_class = BoundingBoxSerializer


class BoundingBoxDetailAPI(BaseDetailAPI):
    queryset = BoundingBox.objects.all()
    serializer_class = BoundingBoxSerializer


class SegmentationListAPI(BaseListAPI):
    label_class = Segmentation
    serializer_class = SegmentationSerializer


class SegmentationDetailAPI(BaseDetailAPI):
    queryset = Segmentation.objects.all()
    serializer_class = SegmentationSerializer


class DatasetVersionVotingStatsAPI(APIView):
    permission_classes = [AllowAny]
    def get(self, request, project_id, example_id, version):
        # Extrair filtros de perspectiva dos parâmetros da query
        perspective_filters = {}
        for key, value in request.query_params.items():
            if key.startswith('perspective_'):
                field = key.replace('perspective_', '')
                perspective_filters[field] = value
        stats = DatasetVersion.get_voting_statistics(example_id, version, perspective_filters)
        return Response(stats, status=status.HTTP_200_OK)


class DatasetVersionAllVersionsAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, project_id, example_id):
        versions = list(DatasetVersion.get_all_versions_for_example(example_id))
        return Response({'versions': versions}, status=status.HTTP_200_OK)


class DatasetVersionPerspectivesAPI(APIView):
    def get(self, request, example_id):
        perspectives = DatasetVersion.get_perspectives_for_example(example_id)
        return Response({'perspectives': perspectives}, status=status.HTTP_200_OK)

class DatasetVersionFullDataAPI(APIView):
    def get(self, request, example_id):
        data = DatasetVersion.get_full_data_for_example(example_id)
        serialized = [
            {
                "example_id": dv.example_id,
                "version": dv.version,
                "user": dv.user.username,
                "label": dv.label.text,
                "is_active": dv.is_active,
                "created_at": dv.created_at,
            }
            for dv in data
        ]
        return Response({"data": serialized}, status=status.HTTP_200_OK)

@api_view(['GET'])
def example_versions(request, example_id):
    versions = list(DatasetVersion.get_all_versions_for_example(example_id))
    return Response({"versions": versions})

@method_decorator(csrf_exempt, name='dispatch')
class DatasetVersionBulkVersionsAPI(APIView):
    def post(self, request):
        example_ids = request.data.get("example_ids", [])
        result = {}
        for ex_id in example_ids:
            versions = list(DatasetVersion.get_all_versions_for_example(ex_id))
            result[str(ex_id)] = versions
        return Response({str(k): v for k, v in result.items()}, status=status.HTTP_200_OK)