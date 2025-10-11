from django.contrib import admin
from .models import *
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# complaint resources.
class ComplaintResource(resources.ModelResource):
    class Meta:
        models = Complaint
        fields = ('id', 'complaint_number', 'complaint_type', 'description', 'assigned_to', 'location', 'status', 'priority', 'department', 'created_by', 'created_at', 'completed_at', 'attachment')

@admin.register(Complaint)
class ComplaintAdmin(ImportExportModelAdmin):
    resource_class = ComplaintResource
    list_display = ('complaint_number', 'complaint_type', 'description', 'assigned_to', 'location', 'status', 'priority', 'department', 'created_by', 'created_at', 'completed_at', 'attachment')
    list_filter = ('status', 'department', 'location', 'created_by')

# complaint type resources.
class ComplaintTypeResource(resources.ModelResource):
    class Meta:
        models = ComplaintType
        fields = ('id', 'name', 'department')

@admin.register(ComplaintType)
class ComplaintTypeAdmin(ImportExportModelAdmin):
    resource_class = ComplaintTypeResource
    list_display = ('name', 'department')

# complaint history resources
class ComplaintHistoryResources(resources.ModelResource):
    class Meta:
        models = ComplaintHistory
        fields = ('id', 'complaint', 'status', 'changed_by', 'timestamp')

@admin.register(ComplaintHistory)
class ComplaintHistoryAdmin(ImportExportModelAdmin):
    resource_class = ComplaintHistoryResources
    list_display = ('complaint', 'status_changed_to', 'changed_by', 'timestamp')

# reassigned complaint resources
class ReassignedComplaintResources(resources.ModelResource):
    class Meta:
        models = ReassignedComplaint
        fields = ('id', 'complaint', 'reassigned_to', 'duration', 'timestamp')

@admin.register(ReassignedComplaint)
class ReassignedComplaintAdmin(ImportExportModelAdmin):
    resource_class = ReassignedComplaintResources
    list_display = ('complaint', 'reassigned_to', 'duration', 'timestamp')

# reassigned department resources
class ReassignedDepartmentResources(resources.ModelResource):
    class Meta:
        models = ReassignDepartment
        fields = ('id', 'complaint', 'reassign_to', 'timestamp')

@admin.register(ReassignDepartment)
class ReassignedDepartmentAdmin(ImportExportModelAdmin):
    resource_class = ReassignedDepartmentResources
    list_display = ('complaint', 'reassign_to', 'timestamp')

# complaint remarks resources
class ComplaintRemarksResources(resources.ModelResource):
    class Meta:
        models = ComplaintRemarks
        fields = ('id', 'complaint', 'remarks', 'created_by', 'created_at', 'attachment')

@admin.register(ComplaintRemarks)
class ComplaintRemarksAdmin(ImportExportModelAdmin):
    resource_class = ComplaintRemarksResources
    list_display = ('complaint', 'remarks', 'created_by', 'created_at', 'attachment')
