from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import CustomUsers, Departments, Location


# Department resource class
class DepartmentResource(resources.ModelResource):
    class Meta:
        model = Departments
        fields = ("id", "name")


@admin.register(Departments)
class DepartmentsAdmin(ImportExportModelAdmin):
    resource_class = DepartmentResource
    list_display = ("name",)
    search_fields = ("name",)


# Users resource class
class UsersResource(resources.ModelResource):
    class Meta:
        model = CustomUsers
        fields = ("id", "username", "role", "department", "designation", "employee_id")


@admin.register(CustomUsers)
class UsersAdmin(ImportExportModelAdmin):
    resource_class = UsersResource
    list_display = (
        "username",
        "role",
        "department",
        "designation",
        "employee_id",
        "status",
    )
    search_fields = ("username", "employee_id")


# Users location class
class UsersResource(resources.ModelResource):
    class Meta:
        model = Location
        fields = ("id", "name")


@admin.register(Location)
class UsersAdmin(ImportExportModelAdmin):
    resource_class = UsersResource
    list_display = ("name",)
