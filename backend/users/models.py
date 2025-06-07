from django.db import models
from django.contrib.auth.models import User

class UserCreation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='creation_info')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users_creation'
