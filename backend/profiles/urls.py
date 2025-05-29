# profiles/urls.py
from django.urls import path, include
from .views import UserProfileViewSet

urlpatterns = [
    path("profiles/create_profile", UserProfileViewSet.as_view(), name='profile_create'),
]


