from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import *


# facility resources.
class FacilityResource(resources.ModelResource):
    class Meta:
        model = Facility
        fields = ("id", "name", "is_active")


# facility admin.
@admin.register(Facility)
class FacilityAdmin(ImportExportModelAdmin):
    resource_class = FacilityResource
    list_display = ("name", "is_active")


# block resources.
class BlockResources(resources.ModelResource):
    class Meta:
        model = Block
        fields = ("id", "facility", "name", "is_active")


# block admin.
@admin.register(Block)
class BlockAdmin(ImportExportModelAdmin):
    resource_class = BlockResources
    list_display = ("facility", "name", "is_active")


# department block admin resources.
class DepartmentBlockAdminResources(resources.ModelResource):
    class Meta:
        model = DepartmentBlockAdmin
        fields = ("id", "block", "department", "department_admin", "is_active")


# department block admin.
@admin.register(DepartmentBlockAdmin)
class DepartmentBlockAdminAdmin(ImportExportModelAdmin):
    resource_class = DepartmentBlockAdminResources
    list_display = ("block", "department", "department_admin", "is_active")


# location resources.
class LocationResources(resources.ModelResource):
    class Meta:
        model = Location
        fields = ("id", "name", "block", "is_active")


# location admin.
@admin.register(Location)
class LocationAdmin(ImportExportModelAdmin):
    resource_class = LocationResources
    list_display = ("name", "block", "is_active")


# complaint resources.
class ComplaintResource(resources.ModelResource):
    class Meta:
        model = Complaint
        fields = (
            "id",
            "complaint_number",
            "complaint_type",
            "description",
            "assigned_to",
            "facility",
            "block",
            "location",
            "status",
            "priority",
            "department",
            "created_by",
            "created_at",
            "completed_at",
            "attachment",
        )


@admin.register(Complaint)
class ComplaintAdmin(ImportExportModelAdmin):
    resource_class = ComplaintResource
    list_display = (
        "complaint_number",
        "complaint_type",
        "description",
        "assigned_to",
        "facility",
        "block",
        "location",
        "status",
        "priority",
        "department",
        "created_by",
        "created_at",
        "completed_at",
        "attachment",
    )
    list_filter = ("status",)
    search_fields = (
        "complaint_number",
        "assigned_to__username",
        "created_by__username",
    )


# complaint type resources.
class ComplaintTypeResource(resources.ModelResource):
    class Meta:
        models = ComplaintType
        fields = ("id", "name", "department")


@admin.register(ComplaintType)
class ComplaintTypeAdmin(ImportExportModelAdmin):
    resource_class = ComplaintTypeResource
    list_display = ("name", "department")


# complaint history resources
class ComplaintHistoryResources(resources.ModelResource):
    class Meta:
        models = ComplaintHistory
        fields = ("id", "complaint", "status", "changed_by", "timestamp")


@admin.register(ComplaintHistory)
class ComplaintHistoryAdmin(ImportExportModelAdmin):
    resource_class = ComplaintHistoryResources
    list_display = ("complaint", "status_changed_to", "changed_by", "timestamp")


# reassigned complaint resources
class ReassignedComplaintResources(resources.ModelResource):
    class Meta:
        models = ReassignedComplaint
        fields = (
            "id",
            "complaint",
            "reassigned_to",
            "duration",
            "message",
            "timestamp",
        )


@admin.register(ReassignedComplaint)
class ReassignedComplaintAdmin(ImportExportModelAdmin):
    resource_class = ReassignedComplaintResources
    list_display = ("complaint", "reassigned_to", "duration", "message", "timestamp")


# reassigned department resources
class ReassignedDepartmentResources(resources.ModelResource):
    class Meta:
        models = ReassignDepartment
        fields = ("id", "complaint", "reassign_to", "reason", "timestamp")


@admin.register(ReassignDepartment)
class ReassignedDepartmentAdmin(ImportExportModelAdmin):
    resource_class = ReassignedDepartmentResources
    list_display = ("complaint", "reassign_to", "reason", "timestamp")


# complaint remarks resources
class ComplaintRemarksResources(resources.ModelResource):
    class Meta:
        models = ComplaintRemarks
        fields = (
            "id",
            "complaint",
            "remarks",
            "created_by",
            "created_at",
            "attachment",
        )


@admin.register(ComplaintRemarks)
class ComplaintRemarksAdmin(ImportExportModelAdmin):
    resource_class = ComplaintRemarksResources
    list_display = ("complaint", "remarks", "created_by", "created_at", "attachment")
