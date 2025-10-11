from django.contrib import admin
from .models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Service generate resource class
class ServiceGenerateResource(resources.ModelResource):
    class Meta:
        model = AnonymousServiceGenerate
        fields = ('id', 'service_number', 'service_type', 'assigned_to', 'status', 'block', 'from_location', 'to_location', 'generate_at', 'completed_at')

@admin.register(AnonymousServiceGenerate)
class ServiceGenerateAdmin(ImportExportModelAdmin):
    resource_class = ServiceGenerateResource
    list_display = ('service_number', 'service_type', 'assigned_to', 'status', 'block', 'from_location', 'to_location', 'generate_at', 'completed_at')
    list_filter = ('status', 'block')