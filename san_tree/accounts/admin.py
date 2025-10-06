from django.contrib import admin
from .models import Departments, CustomUsers, Location
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Department resource class
class DepartmentResource(resources.ModelResource):
    class Meta:
        model = Departments
        fields = ('id', 'name')

@admin.register(Departments)
class DepartmentsAdmin(ImportExportModelAdmin):
    resource_class = DepartmentResource
    list_display = ('name',)

# Users resource class
class UsersResource(resources.ModelResource):
    class Meta:
        model = CustomUsers
        fields = ('id', 'username', 'role', 'department', 'designation', 'employee_id')

@admin.register(CustomUsers)
class UsersAdmin(ImportExportModelAdmin):
    resource_class = UsersResource
    list_display = ('username', 'role', 'department', 'designation', 'employee_id')

# Users location class
class UsersResource(resources.ModelResource):
    class Meta:
        model = CustomUsers
        fields = ('id', 'name')

@admin.register(Location)
class UsersAdmin(ImportExportModelAdmin):
    resource_class = UsersResource
    list_display = ('name',)
