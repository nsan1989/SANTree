from django.urls import path
from .views import *

urlpatterns = [
    path('super_admin_dashboard/', SuperAdminDashboard, name='super_admin'),
    path('super_admin_dashboard/all_departments/', DepartmentView, name='all_departments'),
    path('super_admin_dashboard/all_departments/<int:id>/department_detail/', DepartmentDetails, name='department_detail'),
    path('super_admin_dashboard/all_departments/<int:id>/department_detail/department_complaint/', DepartmentComplaints, name='department_complaints'),
    path('super_admin_dashboard/all_departments/<int:id>/department_detail/department_task/', DepartmentTasks, name='department_tasks'),
    path('main_dashboard/', MainDashboard, name='main_dashboard'),
    path('track/', TrackView, name='track'),
    path('dept_complaint_pie_chart/<int:id>/', DeptComplaintPieChart, name='dept_complaint_pie_chart'),
    path('dept_task_pie_chart/<int:id>/', DeptTaskPieChart, name='dept_task_pie_chart'),
    path('all_complaints_pie_chart/', AllComplaintPieChart, name='all_complaints_pie_chart'),
    path('all_tasks_pie_chart/', AllTasksPieChart, name='all_tasks_pie_chart'),
    path('all_service_pie_chart/', AllServicePieChart, name='all_service_pie_chart'),
    path('super_admin_dashboard/all_complaints/', ComplaintView, name='all_complaints'),
    path('super_admin_dashboard/all_complaints/<int:id>/complaint_detail/', ComplaintDetailView, name='complaint_detail'),
    path('super_admin_dashboard/all_tasks/', TaskView, name='all_tasks'),
    path('super_admin_dashboard/all_tasks/<int:id>/task_detail/', TaskDetailView, name='task_detail'),
    path('super_admin_dashboard/all_services/', ServiceView, name='all_services'),
     path('super_admin_dashboard/all_services/<int:id>/service_detail/', ServiceDetailView, name='service_detail'),
    path('add_department/', AddDepartmentView, name='add_department'),
    path('add_complaint_type/', AddComplaintTypeView, name='add_complaint_type'),
    path('add_task_type/', AddTaskTypeView, name='add_task_type'),
    path('add_location/', AddLocationView, name='add_location'),
    path('add_service_type/', AddServiceTypeView, name='add_service_type'),
    path('add_block/', AddBlockView, name='add_block'),
    path('profile/', ProfileView, name='profile'),
    path('webpush/save_information/', save_information, name='save_subscription'),
    path('anonymous_service_generate/', AnonymousServiceView, name='anonymous_service_generate'),
    path('anonymous_service_generate/success_page/', ServiceSuccessView, name='success_page'),
    path('generate_qr/', GenerateQRCode, name='generate_qr')
]
