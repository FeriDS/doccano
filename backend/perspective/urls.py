from django.urls import path
from .views import PerspectiveList, PerspectiveDetail

urlpatterns = [
    path('api/perspective/', PerspectiveList.as_view(), name='perspective-list'),
    path('api/perspective/<int:id>/', PerspectiveDetail.as_view(), name='perspective-detail'),
]