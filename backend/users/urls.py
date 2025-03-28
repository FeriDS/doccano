from django.urls import include, path

from .views import Me, UserCreation, Users, UserDelete, UserRetrieve

urlpatterns = [
    path(route="me", view=Me.as_view(), name="me"),
    path(route="users", view=Users.as_view(), name="user_list"),
    path(route="users/create", view=UserCreation.as_view(), name="user_create"),
    path("auth/", include("dj_rest_auth.urls")),
    path("users/get-id/<str:username>", UserRetrieve.as_view(), name="user_get_id"),  # New endpoint to lookup id by username
    path("users/delete/<int:id>", UserDelete.as_view(), name="user_delete"),  # Delete endpoint using id
]
