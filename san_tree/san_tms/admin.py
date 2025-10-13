from django.contrib import admin
from .models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# tasks types resources
class TaskTypeResources(resources.ModelResource):
    class Meta:
        models = TasksTypes
        fields = ('id', 'name', 'department')

@admin.register(TasksTypes)
class TaskTypeAdmin(ImportExportModelAdmin):
    resource_class = TaskTypeResources
    list_display = ('name', 'department')

# tasks resources
class TasksResources(resources.ModelResource):
    class Meta:
        models = Tasks
        fields = ('id', 'tasks_number', 'tasks_types', 'location', 'status', 'priority', 'department', 'created_by', 'assigned_to', 'created_at', 'completed_at', 'waiting_time', 'attachment')

@admin.register(Tasks)
class TasksAdmin(ImportExportModelAdmin):
    resource_class = TasksResources
    list_display = ('tasks_number', 'tasks_types', 'location', 'status', 'priority', 'department', 'created_by', 'assigned_to', 'created_at', 'completed_at', 'waiting_time', 'attachment')
    list_filter = ('status', 'priority', 'created_at', 'completed_at')

# tasks remarks resources.
class TasksRemarksResources(resources.ModelResource):
    class Meta:
        models = TasksRemarks
        fields = ('id', 'tasks', 'remarks', 'created_by', 'created_at', 'attachment')

@admin.register(TasksRemarks)
class TasksRemarksAdmin(ImportExportModelAdmin):
    resource_class = TasksRemarksResources
    list_display = ('tasks', 'remarks', 'created_by', 'created_at', 'attachment')
