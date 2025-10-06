from django.urls import path
from .views import *

app_name = "srm"

urlpatterns = [
    path('incharge/dashboard/', AdminDashboard, name='admin_dashboard'),
    path('incharge/dashboard/request_service/', ServiceView, name='admin_request_service'),
    path('incharge/dashboard/schedules/', ShiftSchedules, name='schedule'),
    path('incharge/dashboard/schedules/set_schedule/', ShiftScheduleView, name='shift_schedule'),
    path('incharge/dashboard/schedules/edit_schedule/<int:id>/', ShiftEditView, name='edit_schedule'),
    path('staff/dashboard/', StaffDashboard, name='staff_dashboard'),
    path('staff/dashboard/request_service/', ServiceView, name='request_service'),
    path('staff/dashboard/generate_service/', GenerateServiceView, name='generate_service'),
    path('staff/dashboard/all_generate_service/', AllGeneratedService, name='all_generate_service'),
    path('staff/dashboard/service/<int:id>/update_status/', free_up_completed_staff, name='staff_update_service_status'),
    path('incharge/all_services/', RequestServiceView, name='admin_service'),
    path('staff/all_services/', RequestServiceView, name='staff_service'),
    path('service_pie_chart/', ServicePieChart, name='service_pie_chart'),
    path('service_remark/<int:id>/remark/', ServiceRemark, name='service_remarks'),
    path('update_status/', UpdateUserStatus, name='update_status'),
]