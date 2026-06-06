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


# PatientBooking Resources.
class PatientBookingResources(resources.ModelResource):
    class Meta:
        model = PatientBooking
        fields = (
            "id",
            "booking_number",
            "service_type",
            "patient_name",
            "patient_uhid",
            "patient_phone",
            "hospital_location",
            "drop_location_text",
            "drop_latitude",
            "drop_longitude",
            "scheduled_drop_time",
            "distance_km_estimated",
            "distance_km_final",
            "base_fare",
            "per_km_rate",
            "extra_charges",
            "discount_amount",
            "total_amount",
            "status",
            "remarks",
            "booked_by",
            "assigned_vehicle",
            "assigned_driver",
            "created_at",
            "updated_at",
        )


# PatientBooking Admin.
@admin.register(PatientBooking)
class PatientBookingAdmin(ImportExportModelAdmin):
    resource_class = PatientBookingResources
    list_display = (
        "id",
        "booking_number",
        "service_type",
        "patient_name",
        "patient_uhid",
        "status",
        "total_amount",
        "booked_by",
        "assigned_driver",
        "created_at",
    )


# PatientPayment Resources.
class PatientPaymentResources(resources.ModelResource):
    class Meta:
        model = PatientPayment
        fields = (
            "id",
            "booking",
            "amount",
            "currency",
            "payment_provider",
            "payment_method",
            "gateway_order_id",
            "gateway_payment_id",
            "status",
            "initiated_at",
            "paid_at",
            "failure_reason",
        )


# PatientPayment Admin.
@admin.register(PatientPayment)
class PatientPaymentAdmin(ImportExportModelAdmin):
    resource_class = PatientPaymentResources
    list_display = (
        "id",
        "booking",
        "amount",
        "status",
        "payment_provider",
        "initiated_at",
        "paid_at",
    )
