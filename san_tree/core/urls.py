from django.urls import path
from .views import MainDashboard, TrackView, SuperAdminDashboard, DepartmentView, DepartmentDetails, DeptComplaintPieChart, DeptTaskPieChart, AllComplaintPieChart, AllTasksPieChart, UserView

urlpatterns = [
    path('super_admin_dashboard/', SuperAdminDashboard, name='super_admin'),
    path('super_admin_dashboard/all_departments/', DepartmentView, name='all_departments'),
    path('super_admin_dashboard/all_departments/<int:id>/department_detail/', DepartmentDetails, name='department_detail'),
    path('super_admin_dashboard/all_users/', UserView, name='all_users'),
    path('main_dashboard/', MainDashboard, name='main_dashboard'),
    path('track/', TrackView, name='track'),
    path('dept_complaint_pie_chart/<int:id>/', DeptComplaintPieChart, name='dept_complaint_pie_chart'),
    path('dept_task_pie_chart/<int:id>/', DeptTaskPieChart, name='dept_task_pie_chart'),
    path('all_complaints_pie_chart/', AllComplaintPieChart, name='all_complaints_pie_chart'),
    path('all_tasks_pie_chart/', AllTasksPieChart, name='all_tasks_pie_chart'),
]
