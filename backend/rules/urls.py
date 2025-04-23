from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'annotation-rules', views.AnnotationRuleViewSet)
router.register(r'voting-configs', views.VotingConfigViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/rules/', include('rules.urls')),
    path('projects/<int:project_id>/rules/', your_view_para_frontend, name='project-rules'),
]