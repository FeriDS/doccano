from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PerspectiveViewSet, 
    PerspectiveFieldViewSet,
    ProjectPerspectiveViewSet,
    UserPerspectiveAnswerViewSet,
    get_project_perspective,
    get_user_perspective_answers,
    update_user_perspective_answer,
    users_with_perspective_value
)

router = DefaultRouter()
router.register(r'fields', PerspectiveFieldViewSet)
router.register(r'perspectives', PerspectiveViewSet)
router.register(r'project-perspectives', ProjectPerspectiveViewSet, basename='project-perspective')
router.register(r'user-answers', UserPerspectiveAnswerViewSet, basename='user-perspective-answer')

user_answers_list = UserPerspectiveAnswerViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

urlpatterns = [
    path('', include(router.urls)),
    path('projects/<int:project_id>/perspective/', get_project_perspective),
    path('projects/<int:project_id>/user-answers/', get_user_perspective_answers),
    path('projects/<int:project_id>/user-answers/update/', update_user_perspective_answer),
    path('users_with_perspective_value/', users_with_perspective_value, name='users_with_perspective_value'),
]