from django.contrib import admin
from import_export import fields, resources, widgets
from import_export.admin import ImportExportModelAdmin

from .models import *


# service types resources
class ServiceTypesResources(resources.ModelResource):
    class Meta:
        models = ServiceTypes
        fields = ("id", "name", "department")


@admin.register(ServiceTypes)
class ServiceTypesAdmin(ImportExportModelAdmin):
    resource_class: ServiceTypesResources
    list_display = ("name", "department")


# blocks resources
class BlockResources(resources.ModelResource):
    class Meta:
        models = Blocks
        fields = ("id", "name")


@admin.register(Blocks)
class BlockAdmin(ImportExportModelAdmin):
    resource_class = BlockResources
    list_display = ("name",)


# shift schedule resources
class ShiftScheduleResources(resources.ModelResource):
    class Meta:
        models = ShiftSchedule
        fields = (
            "id",
            "shift_type",
            "shift_block",
            "shift_staffs",
            "start_time",
            "end_time",
            "status",
            "is_active",
        )


@admin.register(ShiftSchedule)
class ShiftScheduleAdmin(ImportExportModelAdmin):
    resource_class = ShiftScheduleResources
    list_display = (
        "shift_type",
        "shift_block",
        "shift_staffs",
        "start_time",
        "end_time",
        "status",
        "is_active",
    )


# service resources
class ServiceResources(resources.ModelResource):
    assigned_to = fields.Field(column_name="assigned_to")

    def dehydrate_assigned_to(self, obj):
        if obj.assigned_to and obj.assigned_to.shift_staffs:
            return obj.assigned_to.shift_staffs.username
        return "-"

    class Meta:
        model = Service
        fields = (
            "id",
            "service_number",
            "service_type",
            "service_block",
            "from_location",
            "to_location",
            "UHID",
            "status",
            "assigned_to",
            "handled_by",
            "description",
            "created_by",
            "created_at",
            "started_at",
            "completed_at",
        )


@admin.register(Service)
class ServiceAdmin(ImportExportModelAdmin):
    resource_class = ServiceResources
    list_display = (
        "service_number",
        "service_type",
        "service_block",
        "from_location",
        "to_location",
        "UHID",
        "status",
        "get_assigned_staff",
        "handled_by",
        "description",
        "created_by",
        "created_at",
        "started_at",
        "completed_at",
    )
    list_filter = ("service_block", "status")

    def get_assigned_staff(self, obj):
        if obj.assigned_to is None:
            return "-"
        return str(obj.assigned_to)

    get_assigned_staff.short_description = "Assigned Staff"


# service queue resources
class ServiceQueueResources(resources.ModelResource):
    class Meta:
        models = ServiceRequestQueue
        fields = ("id", "service_request", "created_at")


@admin.register(ServiceRequestQueue)
class ServiceQueueAdmin(ImportExportModelAdmin):
    resource_class = ServiceQueueResources
    list_display = ("service_request", "created_at")


# generate service resources
class GenerateServiceResources(resources.ModelResource):
    class Meta:
        models = GenerateService
        fields = (
            "id",
            "generate_number",
            "service_type",
            "from_location",
            "to_location",
            "generate_by",
            "status",
            "generate_at",
            "completed_at",
            "attachment",
        )


@admin.register(GenerateService)
class GenerateServiceAdmin(ImportExportModelAdmin):
    resource_class = GenerateServiceResources
    list_display = (
        "generate_number",
        "service_type",
        "from_location",
        "to_location",
        "generate_by",
        "status",
        "generate_at",
        "completed_at",
        "attachment",
    )


# service remark resources.
class ServiceRemarkResources(resources.ModelResource):
    class Meta:
        models = ServiceRemarks
        fields = ("id", "service", "remarks", "created_by", "created_at", "attachment")


@admin.register(ServiceRemarks)
class ServiceRemarkAdmin(ImportExportModelAdmin):
    resource_class = ServiceRemarkResources
    list_display = ("service", "remarks", "created_by", "created_at", "attachment")
