from django.urls import path
from .views import *

app_name = "tms"

urlpatterns = [
    path('tasks_admin/dashboard/', TaskDashboard, name='admin_dashboard'),
    path('tasks_staff/dashboard/', StaffDashboard, name='staff_dashboard'),
    path('tasks_pie_chart/', TasksPieChart, name='all_tasks_pie_chart'),
    path('tasks_admin/assigned_tasks/', TasksView, name='assigned_tasks'),
    path('tasks_admin/all_tasks/', AllTasks, name='tasks'),
    path('tasks_admin/all_tasks/all_tasks_details/<int:id>/', AllTasksDetails, name='admin_tasks_details'),
    path('tasks_admin/all_tasks/all_tasks_details/update_status/<int:id>/', UpdateStatus, name='admin_update_task_status'),
    path('tasks_staff/my_tasks/', MyTasks, name='my_tasks'),
    path('tasks_staff/my_tasks/tasks_details/<int:id>/', TasksDetails, name='staff_tasks_details'),
    path('tasks_staff/my_tasks/tasks_details/update_status/<int:id>/', UpdateStatus, name='staff_update_task_status'),
    path('ajax/load-tasks-types/', load_tasks_types, name='ajax_load_tasks_types'),
    path('ajax/load-staff/', load_tasks_staffs, name='ajax_load_staff'),
    path('tasks_remarks/<int:task_id>/remark/', RemarkComplaint, name='tasks_remarks'),
]
