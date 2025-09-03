from django.shortcuts import render, get_object_or_404
from accounts.models import Departments, CustomUsers
from san_cms.models import Complaint, ComplaintRemarks, ComplaintType
from san_tms.models import Tasks, TasksRemarks, TasksTypes
from django.db.models import Q
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.http import HttpResponse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from threading import Lock
plot_lock = Lock()
from django.core.paginator import Paginator
from django.conf import settings
from webpush import send_user_notification
import json
from .forms import *
from django.contrib import messages
from django.core.exceptions import ValidationError

# Home View.
def Home(request):
    context = {
        'vapid_key': settings.WEBPUSH_SETTINGS['VAPID_PUBLIC_KEY']
    }
    return render(request, 'home.html', context)

# Main Dashboard View
def MainDashboard(request):
    user = request.user
    staff_new_comp = Complaint.objects.filter(
        Q(assigned_to = user) &
        (Q(status='In Progress') | Q(status='Open'))
        )
    new_comp = staff_new_comp.all().count()
    staff_new_task = Tasks.objects.filter(
        Q(assigned_to = user) &
        (Q(status='Open'))
        )
    new_task = staff_new_task.all().count()
    context = {
        'show_alert': new_comp,
        'show_alert_tms': new_task,
    }
    return render(request, 'mains_dashboard.html', context)

# Track 
def TrackView(request):
    query = request.GET.get('q', '').strip().upper()
    if not query:
        return JsonResponse({'found': False, 'error': 'Please enter a tracking number.'})

    complaint = Complaint.objects.filter(complaint_number=query).first()
    if complaint:
        return JsonResponse({
            'found': True,
            'type': str(complaint.complaint_type),
            'assigned_to': str(complaint.assigned_to),
            'status': str(complaint.status),
        })

    task = Tasks.objects.filter(tasks_number=query).first()
    if task:
        return JsonResponse({
            'found': True,
            'type': str(task.tasks_types),
            'assigned_to': str(task.assigned_to),
            'status': str(task.status),
        })

    return JsonResponse({'found': False, 'error': 'No match found for this tracking number.'})

# Super Admin Dashboard View.
def SuperAdminDashboard(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    all_dept = Departments.objects.all()
    dept_count = all_dept.count()
    all_users = CustomUsers.objects.all()
    user_count = all_users.count()
    all_comp = Complaint.objects.all()
    comp_count = all_comp.count()
    all_task = Tasks.objects.all()
    task_count = all_task.count()
    context = {
        'user': user,
        'dept': dept_count,
        'user': user_count,
        'comp': comp_count,
        'task': task_count,
    }
    view_name = request.resolver_match.view_name
    if view_name == "super_admin" and user_role == 'Super Admin':
        return render(request, 'super_admin_dashboard.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Departments View.
def DepartmentView(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    query = request.GET.get('q', '')
    if query:
        all_department = Departments.objects.filter(name__icontains=query)
    else:
        all_department = Departments.objects.all()
    paginator = Paginator(all_department, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'query': query,
    }
    view_name = request.resolver_match.view_name
    if view_name == "all_departments" and user_role == 'Super Admin':
        return render(request, 'department.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Department Complaint Pie Chart.
def DeptComplaintPieChart(request,id):
    user = request.user
    selected_dept = get_object_or_404(Departments, id=id)
    open_comp = Complaint.objects.filter(department=selected_dept, status='Open').count()
    pro_comp = Complaint.objects.filter(department=selected_dept, status='In Progress').count()
    close_comp = Complaint.objects.filter(department=selected_dept, status='Resolved').count()
    halt_comp = Complaint.objects.filter(department=selected_dept, status='Halt').count()
    if open_comp + pro_comp + close_comp + halt_comp == 0:
        labels = ['No Data']
        sizes = [1]
        colors = ['#d3d3d3']
    else:
        raw_data = [
            ('Open', open_comp, '#eb0707'),
            ('Progress', pro_comp, '#ebd807'),
            ('Resolved', close_comp, '#4feb07'),
            ('Halt', halt_comp, "#2207eb")
            ]
    
        filtered_data = [(label, size, color) for label, size, color in raw_data if size > 0]
        labels, sizes, colors = zip(*filtered_data)

    buffer = io.BytesIO()

    with plot_lock:
        bg_color = (0, 0, 0, 0.4)
        fig, ax = plt.subplots(figsize=(6, 3), facecolor=bg_color) 
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, textprops={'color': 'white'})
        ax.axis('equal')
        # Add the chart title
        ax.set_title("Complaint Pie Chart", color='white', fontsize=10)
        plt.savefig(buffer, format='png', facecolor=fig.get_facecolor())
        plt.close(fig)
    
    buffer.seek(0)
    return HttpResponse(buffer.read(), content_type='image/png')

# Department Task Pie Chart.
def DeptTaskPieChart(request,id):
    user = request.user
    selected_dept = get_object_or_404(Departments, id=id)
    open_comp = Tasks.objects.filter(department=selected_dept, status='Open').count()
    pro_comp = Tasks.objects.filter(department=selected_dept, status='In Progress').count()
    close_comp = Tasks.objects.filter(department=selected_dept, status='Completed').count()
    halt_comp = Tasks.objects.filter(department=selected_dept, status='Halt').count()
    if open_comp + pro_comp + close_comp + halt_comp == 0:
        labels = ['No Data']
        sizes = [1]
        colors = ['#d3d3d3']
    else:
        raw_data = [
            ('Open', open_comp, '#eb0707'),
            ('Progress', pro_comp, '#ebd807'),
            ('Resolved', close_comp, '#4feb07'),
            ('Halt', halt_comp, "#2207eb")
            ]
    
        filtered_data = [(label, size, color) for label, size, color in raw_data if size > 0]
        labels, sizes, colors = zip(*filtered_data)

    buffer = io.BytesIO()

    with plot_lock:
        bg_color = (0, 0, 0, 0.4)
        fig, ax = plt.subplots(figsize=(6, 3), facecolor=bg_color) 
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, textprops={'color': 'white'})
        ax.axis('equal')
        # Add the chart title
        ax.set_title("task Pie Chart", color='white', fontsize=10)
        plt.savefig(buffer, format='png', facecolor=fig.get_facecolor())
        plt.close(fig)
    
    buffer.seek(0)
    return HttpResponse(buffer.read(), content_type='image/png')

# Department Details.
def DepartmentDetails(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    selected_dept = get_object_or_404(Departments, id=id)
    dept_comp = Complaint.objects.filter(department=selected_dept).count()
    dept_task = Tasks.objects.filter(department=selected_dept).count()
    dept_users = CustomUsers.objects.filter(department=selected_dept).count()
    context = {
        'select_dept': selected_dept,
        'comp': dept_comp,
        'task': dept_task,
        'users': dept_users
    }
    view_name = request.resolver_match.view_name
    if view_name == "department_detail" and user_role == 'Super Admin':
        return render(request, 'department_details.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Department Complaints
def DepartmentComplaints(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    selected_dept = get_object_or_404(Departments, id=id)
    dept_comp = Complaint.objects.filter(department=selected_dept).all()
    context = {
        'complaints': dept_comp
    }
    view_name = request.resolver_match.view_name
    if view_name == "department_complaints" and user_role == 'Super Admin':
        return render(request, 'department_complaint.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Department Tasks
def DepartmentTasks(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    selected_dept = get_object_or_404(Departments, id=id)
    dept_task = Tasks.objects.filter(department=selected_dept).all()
    context = {
        'tasks': dept_task
    }
    view_name = request.resolver_match.view_name
    if view_name == "department_tasks" and user_role == 'Super Admin':
        return render(request, 'department_task.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# All Complaint Pie Chart.
def AllComplaintPieChart(request):
    user = request.user
    open_comp = Complaint.objects.filter(status='Open').count()
    pro_comp = Complaint.objects.filter(status='In Progress').count()
    close_comp = Complaint.objects.filter(status='Resolved').count()
    halt_comp = Complaint.objects.filter(status='Halt').count()
    if open_comp + pro_comp + close_comp + halt_comp == 0:
        labels = ['No Data']
        sizes = [1]
        colors = ['#d3d3d3']
    else:
        raw_data = [
            ('Open', open_comp, '#eb0707'),
            ('Progress', pro_comp, '#ebd807'),
            ('Resolved', close_comp, '#4feb07'),
            ('Halt', halt_comp, "#2207eb")
            ]
    
        filtered_data = [(label, size, color) for label, size, color in raw_data if size > 0]
        labels, sizes, colors = zip(*filtered_data)

    buffer = io.BytesIO()

    with plot_lock:
        bg_color = (0, 0, 0, 0.4)
        fig, ax = plt.subplots(figsize=(6, 3), facecolor=bg_color) 
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, textprops={'color': 'white'})
        ax.axis('equal')
        # Add the chart title
        ax.set_title("Complaint Pie Chart", color='white', fontsize=10)
        plt.savefig(buffer, format='png', facecolor=fig.get_facecolor())
        plt.close(fig)
    
    buffer.seek(0)
    return HttpResponse(buffer.read(), content_type='image/png')

# All Task Pie Chart.
def AllTasksPieChart(request):
    user = request.user
    open_comp = Tasks.objects.filter(status='Open').count()
    pro_comp = Tasks.objects.filter(status='In Progress').count()
    close_comp = Tasks.objects.filter(status='Completed').count()
    halt_comp = Tasks.objects.filter(status='Halt').count()
    if open_comp + pro_comp + close_comp + halt_comp == 0:
        labels = ['No Data']
        sizes = [1]
        colors = ['#d3d3d3']
    else:
        raw_data = [
            ('Open', open_comp, '#eb0707'),
            ('Progress', pro_comp, '#ebd807'),
            ('Resolved', close_comp, '#4feb07'),
            ('Halt', halt_comp, "#2207eb")
            ]
    
        filtered_data = [(label, size, color) for label, size, color in raw_data if size > 0]
        labels, sizes, colors = zip(*filtered_data)

    buffer = io.BytesIO()

    with plot_lock:
        bg_color = (0, 0, 0, 0.4)
        fig, ax = plt.subplots(figsize=(6, 3), facecolor=bg_color) 
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, textprops={'color': 'white'})
        ax.axis('equal')
        # Add the chart title
        ax.set_title("Task Pie Chart", color='white', fontsize=10)
        plt.savefig(buffer, format='png', facecolor=fig.get_facecolor())
        plt.close(fig)
    
    buffer.seek(0)
    return HttpResponse(buffer.read(), content_type='image/png')

# Users View.
def UserView(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    
    reg_dept = Departments.objects.all()
    department_id = request.GET.get("department")
    all_status = CustomUsers._meta.get_field("status").choices
    status_value = request.GET.get("status")

    all_users = CustomUsers.objects.all()

    if department_id:
        all_users = all_users.filter(department_id=department_id)

    if status_value:
        all_users = all_users.filter(status=status_value)


    paginator = Paginator(all_users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    context = {
        'page_obj': page_obj,
        'dept': reg_dept,
        'status': all_status,
        'selected_department': department_id,
    }
    view_name = request.resolver_match.view_name
    if view_name == "all_users" and user_role == 'Super Admin':
        return render(request, 'users.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Complaints View.
def ComplaintView(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")

    reg_dept = Departments.objects.all()
    dept_id = request.GET.get("department")
    all_status = Complaint._meta.get_field("status").choices
    status_value = request.GET.get("status")

    all_complaint = Complaint.objects.all()

    if dept_id:
        all_complaint = all_complaint.filter(department_id = dept_id)

    if status_value:
        all_complaint = all_complaint.filter(status = status_value)

    paginator = Paginator(all_complaint, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'dept': reg_dept,
        'status': all_status,
        'selected_dept': dept_id,
    }

    view_name = request.resolver_match.view_name
    if view_name == "all_complaints" and user_role == 'Super Admin':
        return render(request, 'super_admin_complaints.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Complaints Details View.
def ComplaintDetailView(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    selected_comp = get_object_or_404(Complaint, id=id)
    remark = ComplaintRemarks.objects.filter(complaint_id=id)
    context = {
        'complaint': selected_comp,
        'remarks': remark,
    }
    view_name = request.resolver_match.view_name
    if view_name == "complaint_detail" and user_role == 'Super Admin':
        return render(request, 'complaints_details.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Tasks View.
def TaskView(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")

    reg_dept = Departments.objects.all()
    dept_id = request.GET.get("department")
    all_status = Tasks._meta.get_field("status").choices
    status_value = request.GET.get("status")

    all_task = Tasks.objects.all()

    if dept_id:
        all_task = all_task.filter(department_id = dept_id)

    if status_value:
        all_task = all_task.filter(status = status_value)

    paginator = Paginator(all_task, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'dept': reg_dept,
        'status': all_status,
        'selected_dept': dept_id,
    }

    view_name = request.resolver_match.view_name
    if view_name == "all_tasks" and user_role == 'Super Admin':
        return render(request, 'super_admin_tasks.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Tasks Details View.
def TaskDetailView(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    selected_comp = get_object_or_404(Tasks, id=id)
    remark = TasksRemarks.objects.filter(tasks_id=id)
    context = {
        'task': selected_comp,
        'remarks': remark,
    }
    view_name = request.resolver_match.view_name
    if view_name == "task_detail" and user_role == 'Super Admin':
        return render(request, 'task_detail.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Push Notification.
def send_notification(request):
    payload = {
        "head": "New Update!",
        "body": "You've got a new message.",
        "icon": "/static/icons/icon-192x192.png",
    }
    send_user_notification(user=request.user, payload=json.dumps(payload), ttl=1000)
    return JsonResponse({'status': 'success'})

# Add Department View
def AddDepartmentView(request):
    if request.method == 'POST':
        form = AddDepartmentForm(request.POST)
        if form.is_valid():
            register_dept = form.save(commit=False)
            try:
                register_dept.save()
                messages.success(request, f'Department "{register_dept.name}" added successfully!')
            except ValidationError as e:
                messages.error(request, e.message)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddDepartmentForm()

    return render(request, 'add_department.html', {'form': form})

# Add Complaint Type View.
def AddComplaintTypeView(request):
    if request.method == 'POST':
        form = AddComplaintType(request.POST)
        if form.is_valid():
            comp_type = form.save(commit=False)
            
            # use "exists" instead of reusing comp_type
            exists = ComplaintType.objects.filter(
                name__iexact=comp_type.name,
                department=comp_type.department
            ).exists()

            if exists:
                messages.error(request, 'Complaint type already exists!')
            else:
                comp_type.save()
                messages.success(request, 'Complaint type added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddComplaintType()

    return render(request, 'add_complaint_type.html', {'form': form})

# Add Tasks Type View.
def AddTaskTypeView(request):
    if request.method == 'POST':
        form = AddTaskType(request.POST)
        if form.is_valid():
            task_type = form.save(commit=False)
            exists = TasksTypes.objects.filter(name__iexact = task_type.name, department__name__iexact = task_type.department).exists()
            if exists:
                messages.error(request, 'Task type already exist!')
            else:
                task_type.save()
                messages.success(request, 'Task type added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddComplaintType()

    return render(request, 'add_tasks_type.html', {'form': form})
