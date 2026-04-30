from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import *


# tasks types resources
class TaskTypeResources(resources.ModelResource):
    class Meta:
        models = TasksTypes
        fields = ("id", "name", "department")


@admin.register(TasksTypes)
class TaskTypeAdmin(ImportExportModelAdmin):
    resource_class = TaskTypeResources
    list_display = ("name", "department")


# tasks resources
class TasksResources(resources.ModelResource):
    class Meta:
        models = Tasks
        fields = (
            "id",
            "tasks_number",
            "tasks_types",
            "location",
            "status",
            "task_frequency",
            "department",
            "created_by",
            "assigned_to",
            "created_at",
            "next_date",
            "attachment",
        )


@admin.register(Tasks)
class TasksAdmin(ImportExportModelAdmin):
    resource_class = TasksResources
    list_display = (
        "tasks_number",
        "tasks_types",
        "location",
        "status",
        "task_frequency",
        "department",
        "created_by",
        "assigned_to",
        "created_at",
        "next_date",
        "attachment",
    )
    list_filter = ("status", "created_at", "next_date")


# tasks remarks resources.
class TasksRemarksResources(resources.ModelResource):
    class Meta:
        models = TasksRemarks
        fields = ("id", "tasks", "remarks", "created_by", "created_at", "attachment")


@admin.register(TasksRemarks)
class TasksRemarksAdmin(ImportExportModelAdmin):
    resource_class = TasksRemarksResources
    list_display = ("tasks", "remarks", "created_by", "created_at", "attachment")


class TaskHandoverResources(resources.ModelResource):
    class Meta:
        models = TaskHandover
        fields = (
            "id",
            "tasks",
            "from_user",
            "to_user",
            "reason",
            "created_by",
            "created_at",
        )


@admin.register(TaskHandover)
class TaskHandoverAdmin(ImportExportModelAdmin):
    resource_class = TaskHandoverResources
    list_display = ("tasks", "from_user", "to_user", "created_by", "created_at")


class TaskChecklistItemResources(resources.ModelResource):
    class Meta:
        models = TaskChecklistItem
        fields = (
            "id",
            "tasks",
            "item_text",
            "is_completed",
            "completed_by",
            "completed_at",
        )


@admin.register(TaskChecklistItem)
class TaskChecklistItemAdmin(ImportExportModelAdmin):
    resource_class = TaskChecklistItemResources
    list_display = ("tasks", "item_text", "is_completed", "completed_by", "completed_at")
