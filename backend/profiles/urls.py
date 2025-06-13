# profiles/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, PermissionListView

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('permissions/', PermissionListView.as_view(), name='permission-list'),
    path('', include(router.urls)),
]


