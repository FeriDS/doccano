from django.contrib import admin
from .models import Perspective, PerspectiveField

class PerspectiveFieldInline(admin.TabularInline):
    model = PerspectiveField
    extra = 0

class PerspectiveAdmin(admin.ModelAdmin):
    inlines = [PerspectiveFieldInline]
    list_display = ("name", "project")

admin.site.register(Perspective, PerspectiveAdmin)
admin.site.register(PerspectiveField)
