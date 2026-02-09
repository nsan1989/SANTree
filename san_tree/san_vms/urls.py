from django.urls import path
from .views import *

app_name = "vms"

urlpatterns = [
    path('admin/dashboard/', AdminDashboardView, name='vms_admin_dashboard'),
    path('staff/dashboard/', StaffDashboardView, name='vms_staff_dashboard'),
    path('staff/cab_request/', CabRequestView, name='vms_cab_request'),
    path('staff/all_trips/', AllTripsView, name='vms_all_trips'),
    path('staff/upcoming_trips/', UpcomingTripsView, name='vms_upcoming_trips'),
]
