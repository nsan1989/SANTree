from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import *


# Vehicle Resources.
class VehicleResources(resources.ModelResource):
    class Meta:
        model = Vehicle
        fields = (
            "id",
            "vehicle_number",
            "vehicle_type",
            "capacity_weight",
            "capacity_volume",
            "fuel_type",
            "status",
            "maintenance_due_date",
            "is_emergency_active",
        )


# Vehicle Admin.
@admin.register(Vehicle)
class VehicleAdmin(ImportExportModelAdmin):
    resource_class = VehicleResources
    list_display = (
        "id",
        "vehicle_number",
        "vehicle_type",
        "capacity_weight",
        "capacity_volume",
        "fuel_type",
        "status",
        "maintenance_due_date",
        "is_emergency_active",
    )


# Driver Resources.
class DriverResources(resources.ModelResource):
    class Meta:
        model = Driver
        fields = (
            "id",
            "user",
            "license_number",
        )


# Driver Admin.
@admin.register(Driver)
class DriverAdmin(ImportExportModelAdmin):
    resource_class = DriverResources
    list_display = (
        "id",
        "user",
        "license_number",
    )


# Booking Resources.
class BookingResources(resources.ModelResource):
    class Meta:
        model = Booking
        fields = (
            "id",
            "booking_type",
            "priority",
            "department_priority",
            "pickup_location",
            "drop_location",
            "pickup_time",
            "drop_time",
            "passengers",
            "description",
            "vehicle",
            "driver",
            "booked_by",
            "assigned_to",
            "is_recurring",
            "recurrence_pattern",
            "status",
            "created_at",
        )


# Booking Admin.
@admin.register(Booking)
class BookingAdmin(ImportExportModelAdmin):
    resource_class = BookingResources
    list_display = (
        "id",
        "booking_type",
        "priority",
        "department_priority",
        "pickup_location",
        "drop_location",
        "pickup_time",
        "drop_time",
        "passengers",
        "description",
        "vehicle",
        "driver",
        "booked_by",
        "assigned_to",
        "is_recurring",
        "recurrence_pattern",
        "status",
        "created_at",
    )


# Driver Schedule Resources.
class ScheduleResources(resources.ModelResource):
    class Meta:
        model = DriverSchedule
        fields = (
            "id",
            "shift_staffs",
            "shift_type",
            "start_time",
            "end_time",
            "status",
            "is_active",
        )


# Driver Schedule Admin.
@admin.register(DriverSchedule)
class ScheduleAdmin(ImportExportModelAdmin):
    resource_class = ScheduleResources
    list_display = (
        "id",
        "shift_staffs",
        "shift_type",
        "start_time",
        "end_time",
        "status",
        "is_active",
    )


# Vehicle Maintenance Resources.
class MaintenanceResources(resources.ModelResource):
    class Meta:
        model = VehicleMaintenance
        fields = ("id", "vehicle", "description", "start_date", "end_date")


# Vehicle Maintenance Admin.
class MaintenanceAdmin(ImportExportModelAdmin):
    resource_class = MaintenanceResources
    list_display = ("id", "vehicle", "description", "start_date", "end_date")
