from django.urls import path
from .views import *

urlpatterns = [
    path('incharge/dashboard/', AdminDashboard, name='admin_dashboard'),
    path('staff/dashboard/', StaffDashboard, name='staff_dashboard'),
    path('incharge/profile/', ProfileView, name='admin_profile'),
    path('staff/profile/', ProfileView, name='staff_profile'),
    path('incharge/all_services/', AllServiceView, name='admin_service'),
    path('staff/all_services/', AllServiceView, name='staff_service'),
]