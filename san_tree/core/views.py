from django.shortcuts import render, get_object_or_404, redirect
from accounts.models import Departments, CustomUsers
from san_cms.models import Complaint, ComplaintRemarks, ComplaintType
from san_tms.models import Tasks, TasksRemarks, TasksTypes
from san_srm.models import Service, ServiceRemarks, ServiceTypes
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.http import HttpResponse
import matplotlib
from django.conf import settings
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from threading import Lock
plot_lock = Lock()
from django.core.paginator import Paginator
import json
from .forms import *
from django.contrib import messages
from django.core.exceptions import ValidationError
from webpush.models import SubscriptionInfo, PushInformation
import json
from django.utils import timezone
import structlog
from django.db.models import Q
import qrcode
import base64
from datetime import timedelta

log = structlog.get_logger()
now = timezone.now()

# Home View.
def Home(request):
    return render(request, 'home.html')

# Main Dashboard View
def MainDashboard(request):
    context = {
        'vapid_key': settings.WEBPUSH_SETTINGS['VAPID_PUBLIC_KEY']
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
    all_service = Service.objects.all()
    serv_count = all_service.count()
    all_comp = Complaint.objects.all()
    comp_count = all_comp.count()
    all_task = Tasks.objects.all()
    task_count = all_task.count()
    context = {
        'user': user,
        'dept': dept_count,
        'serv': serv_count,
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

# All Service Pie Chart.
def AllServicePieChart(request):
    user = request.user
    open_comp = Service.objects.filter(status='Open').count()
    pro_comp = Service.objects.filter(status='In Progress').count()
    close_comp = Service.objects.filter(status='Completed').count()
    pen_comp = Service.objects.filter(status='Pending').count()
    if open_comp + pro_comp + close_comp + pen_comp == 0:
        labels = ['No Data']
        sizes = [1]
        colors = ['#d3d3d3']
    else:
        raw_data = [
            ('Open', open_comp, '#eb0707'),
            ('Progress', pro_comp, '#ebd807'),
            ('Resolved', close_comp, '#4feb07'),
            ('Halt', pen_comp, "#2207eb")
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
        ax.set_title("Service Pie Chart", color='white', fontsize=10)
        plt.savefig(buffer, format='png', facecolor=fig.get_facecolor())
        plt.close(fig)
    
    buffer.seek(0)
    return HttpResponse(buffer.read(), content_type='image/png')

# Services View.
def ServiceView(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")

    reg_dept = Departments.objects.all()
    dept_id = request.GET.get("department")
    all_status = Service._meta.get_field("status").choices
    status_value = request.GET.get("status")

    all_service = Service.objects.all()

    if dept_id:
        all_service = all_service.filter(department_id = dept_id)

    if status_value:
        all_service = all_service.filter(status = status_value)

    paginator = Paginator(all_service, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'dept': reg_dept,
        'status': all_status,
        'selected_dept': dept_id,
    }

    view_name = request.resolver_match.view_name
    if view_name == "all_services" and user_role == 'Super Admin':
        return render(request, 'super_admin_services.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Services Details View.
def ServiceDetailView(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    selected_serv = get_object_or_404(Service, id=id)
    remark = ServiceRemarks.objects.filter(service_id=id)
    context = {
        'service': selected_serv,
        'remarks': remark,
    }
    view_name = request.resolver_match.view_name
    if view_name == "service_detail" and user_role == 'Super Admin':
        return render(request, 'services_details.html', context)
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

# Add Location View.
def AddLocationView(request):
    if request.method == 'POST':
        form = AddLocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            exists = Location.objects.filter(name__iexact=location.name).exists()
            if exists:
                messages.error(request, 'Location already exist!')
            else:
                location.save()
                messages.success(request, 'Location added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddLocationForm()

    return render(request, 'add_location.html', {'form': form})

# Add Service Type View.
def AddServiceTypeView(request):
    if request.method == 'POST':
        form = AddServiceTypeForm(request.POST)
        if form.is_valid():
            service_type = form.save(commit=False)
            exists = ServiceTypes.objects.filter(name__iexact=service_type.name).exists()
            if exists:
                messages.error(request, 'Service type already exist!')
            else:
                service_type.save()
                messages.success(request, 'Service type added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddServiceTypeForm()

    return render(request, 'add_service.html', {'form': form})

# Add Block View.
def AddBlockView(request):
    if request.method == 'POST':
        form = AddBlockForm(request.POST)
        if form.is_valid():
            block = form.save(commit=False)
            exists = Blocks.objects.filter(name__iexact=block.name).exists()
            if exists:
                messages.error(request, 'Block already exist!')
            else:
                block.save()
                messages.success(request, 'Block added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddBlockForm()

    return render(request, 'add_block.html', {'form': form})

# Profile View.
def ProfileView(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'profile.html', context)

# Save User Subscription Info
def save_information(request):
    if request.method != "POST" or not request.user.is_authenticated:
        return JsonResponse({"status": "error"}, status=403)

    data = json.loads(request.body)

    browser = request.META.get('HTTP_USER_AGENT', '')[:100]
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

    sub_info, created = SubscriptionInfo.objects.update_or_create(
        endpoint=data["endpoint"],
        defaults={
            "p256dh": data["keys"]["p256dh"],
            "auth": data["keys"]["auth"],
            "browser": browser,
            "user_agent": user_agent
        }
    )

    PushInformation.objects.get_or_create(
        user=request.user,
        group=None,
        subscription=sub_info,
    )

    return JsonResponse({"status": "success"})

# Anonymous Service Generate View.
def AnonymousServiceView(request):
    provider_staff = CustomUsers.objects.filter(role='User').filter(
        Q(department__name='GDA') |
        Q(department__name='General Duty Assistant')
    )
    if request.method == "POST":
        form = AnonymousServiceGenerateForm(request.POST)
        if form.is_valid():
            request_service = form.save(commit=False)
            request_service.status = 'Open'
            request_service.save()
            
            for staff in provider_staff:
                if staff.status == 'vacant' or staff.status == 'Vacant':
                    schedule = ShiftSchedule.objects.filter(
                        shift_staffs=staff,
                        start_time__lte=now,
                        end_time__gte=now
                        ).first()
                    if schedule:
                        request_service.assigned_to = schedule
                        request_service.status = 'In Progress'
                        request_service.save()
                        staff.status = 'engaged'
                        staff.save()
                        break
                    else:
                        messages.error(request, f"No shift schedule found for staff {staff}")
            
            return redirect('success_page')
    else:
        form = AnonymousServiceGenerateForm()
    context = {
        'form': form,
    }
    return render(request, "anonymous_service_page.html", context)

# Service Request Success Page
def ServiceSuccessView(request):
    context = {}
    return render(request, "service_request_success_page.html", context)

# QR Generate View.
def GenerateQRCode(request):
    url = "http://10.10.13.246:8000/anonymous_service_generate/"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'qr_code.html', {'qr_code': img_base64})
