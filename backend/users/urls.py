from django.urls import include, path

from .views import Me, UserCreation, Users, delete_user #change (luz)

urlpatterns = [
    path(route="me", view=Me.as_view(), name="me"),
    path(route="users", view=Users.as_view(), name="user_list"),
    path(route="users/create", view=UserCreation.as_view(), name="user_create"),
    #delete user change (luz)
    #path('delete/<int:user_id>/', delete_user, name='delete_user'),
    #end user delete (luz)
    path("auth/", include("dj_rest_auth.urls")),
]
