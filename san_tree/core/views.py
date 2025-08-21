from django.shortcuts import render, get_object_or_404
from accounts.models import Departments, CustomUsers
from san_cms.models import Complaint, ComplaintRemarks
from san_tms.models import Tasks
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
    all_department = Departments.objects.all()
    paginator = Paginator(all_department, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {
        'page_obj': page_obj
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
    all_users = CustomUsers.objects.all()
    paginator = Paginator(all_users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {
        'page_obj': page_obj
    }
    view_name = request.resolver_match.view_name
    if view_name == "all_users" and user_role == 'Super Admin':
        return render(request, 'users.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Complaints View.
def ComplaintView(request):
    user = request.user
    all_complaint = Complaint.objects.all()
    paginator = Paginator(all_complaint, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {
        'page_obj': page_obj
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

# Push Notification.
def send_notification(request):
    payload = {
        "head": "New Update!",
        "body": "You've got a new message.",
        "icon": "/static/icons/icon-192x192.png",
    }
    send_user_notification(user=request.user, payload=json.dumps(payload), ttl=1000)
    return JsonResponse({'status': 'success'})
