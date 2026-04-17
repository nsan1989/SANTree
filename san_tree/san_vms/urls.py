from django.urls import path

from .views import *

app_name = "vms"

urlpatterns = [
    path("admin/dashboard/", AdminDashboardView, name="vms_admin_dashboard"),
    path(
        "admin/all_cab_requests/", AdminCabRequestsView, name="vms_admin_cab_requests"
    ),
    path("admin/all_trips/", AdminTripsView, name="vms_admin_trips"),
    path(
        "admin/all_cab_requests/update_booking_status/<int:booking_id>/",
        AdminUpdateBookingStatusView,
        name="update_booking_status",
    ),
    path("staff/dashboard/", StaffDashboardView, name="vms_staff_dashboard"),
    path("staff/cab_request/", CabRequestView, name="vms_cab_request"),
    path("staff/upcoming_trips/", UpcomingTripsView, name="vms_upcoming_trips"),
    path(
        "staff/upcoming_trips/update_booking_status/<int:booking_id>/",
        StaffUpdateBookingStatusView,
        name="staff_update_booking_status",
    ),
    path("staff/all_trips/", AllTripsView, name="vms_all_trips"),
    path("admin/all_vehicles/", VehiclesView, name="vms_all_vehicles"),
    path("admin/all_staffs/", StaffView, name="vms_all_staffs"),
    path("admin/add_schedule/", ScheduleForm, name="add_schedule"),
    path(
        "incharge/dashboard/schedules/edit_schedule/<int:id>/",
        ShiftEditView,
        name="edit_schedule",
    ),
    path("admin/driver_schedule/", DriverScheduleView, name="driver_schedule"),
    path("schedule-toggle/<int:pk>/", ToggleSchedule, name="toggle_schedule"),
]
