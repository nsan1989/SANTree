from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from .models import *
from .forms import *
from accounts.models import CustomUsers
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import datetime
import structlog

log = structlog.get_logger()
now = timezone.now()

# Admin Dashboard view.
def AdminDashboard(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    dept_users = CustomUsers.objects.filter(
        Q(department__name='GDA') | Q(department__name='General Duty Assistant')
        ).exclude(role='Admin')
    user_count = dept_users.count()
    vacant_users = dept_users.filter(status = 'vacant')
    vacant = vacant_users.count()
    engaged_users = dept_users.filter(status = 'engaged')
    engage = engaged_users.count()
    services = Service.objects.filter(assigned_to__shift_staffs__department__name= user.department).all().count()
    context = {
        'current_user': user,
        'all_users': user_count,
        'engage_user': engaged_users,
        'engaged': engage,
        'vacant_user': vacant_users,
        'vacants': vacant,
        'total_service': services,
    }
    view_name = request.resolver_match.view_name
    if view_name == "srm:admin_dashboard" and user_role == 'Admin':
        return render(request, 'srm_admin_dashboard.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Staff Dashboard View.
def StaffDashboard(request):
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    created_services = Service.objects.filter(created_by = user).all().count()
    open_created_service = Service.objects.filter(created_by = user, status = 'Open').count()
    progress_created_service = Service.objects.filter(created_by = user, status = 'In Progress').count()
    completed_created_service = Service.objects.filter(created_by = user, status = 'Completed').count()
    assign_service = Service.objects.filter(assigned_to__shift_staffs = user).all().count()
    open_assign_service = Service.objects.filter(assigned_to__shift_staffs = user, status = 'Open').count()
    progress_assign_service = Service.objects.filter(assigned_to__shift_staffs = user, status = 'In Progress').count()
    completed_assign_service = Service.objects.filter(assigned_to__shift_staffs = user, status = 'Completed').count()
    my_shift = ShiftSchedule.objects.filter(
        shift_staffs = user, 
        start_time__gte=today, 
        end_time__lt=tomorrow
        ).all()
    context = {
        'current_user': user,
        'total_created_service': created_services,
        'open_created_serv': open_created_service,
        'prog_created_serv': progress_created_service,
        'comp_created_serv': completed_created_service,
        'total_assign_service': assign_service,
        'open_assign_serv': open_assign_service,
        'prog_assign_serv': progress_assign_service,
        'comp_assign_serv': completed_assign_service,
        'shifts': my_shift,
    }
    view_name = request.resolver_match.view_name
    if view_name == "srm:staff_dashboard" and user_role == 'User':
        return render(request, 'srm_staff_dashboard.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Load Service Types.
def load_service_types(request):
    department_id = request.GET.get('department')
    tasks_types = ServiceTypes.objects.filter(department_id=department_id).order_by('name')
    return JsonResponse(list(tasks_types.values('id', 'name')), safe=False)

# Service Request View.
def ServiceView(request):
    provider_staff = CustomUsers.objects.filter(role='User').filter(
        Q(department__name='GDA') |
        Q(department__name='General Duty Assistant')
    )
    if request.method == 'POST':
        form = ServiceForm(request.POST, user=request.user)
        if form.is_valid():
            new_service = form.save(commit=False)
            new_service.created_by = request.user
            new_service.status = 'Open'
            new_service.save()

            if new_service.pk is None:
                raise ValueError("Service not saved properly; missing required fields!")

            assigned = False
            for staff in provider_staff:
                if staff.status == 'vacant' or staff.status == 'Vacant':
                    schedule = ShiftSchedule.objects.filter(
                        shift_staffs=staff,
                        start_time__lte=now,
                        end_time__gte=now
                        ).first()
                    if schedule:
                        new_service.assigned_to = schedule
                        new_service.status = 'In Progress'
                        new_service.save()
                        staff.status = 'engaged'
                        staff.save()
                        assigned = True
                        break
                    else:
                        messages.error(request, f"No shift schedule found for staff {staff}")

            if not assigned:
                new_service.status = 'Waiting'
                new_service.save()
                ServiceRequestQueue.objects.create(service_request=new_service)
            
            if request.user.role == 'Admin':
                return redirect('srm:admin_dashboard')
            else:
                return redirect('srm:staff_dashboard')
    else:
        form = ServiceForm(user=request.user)
    context = {'form': form}
    return render(request, 'service_request.html', context)

# Free up the staff when exceeds timestamp.
def free_up_staff():
    try:
        prog_service = Service.objects.filter(status='In Progress').all()
        if prog_service.exists():
            for service in prog_service:
                if service.created_at <= timezone.now() - timedelta(minutes=3):
                    staff = service.assigned_to.shift_staffs
                    if staff and staff.status == 'engaged':
                        staff.status = 'vacant'
                        staff.save()
                        
                        service.status = 'Pending'
                        service.save()
                    assign_service_from_queue(staff)
        pass
    except Exception as e:
        log.error("Error freeing up staff", error=str(e))

# Free up the staff when service is completed.
def free_up_completed_staff(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User Profile not found.")
    service = get_object_or_404(Service, id=id)
    if request.method == 'POST':
        if user_role == 'User' and service.assigned_to.shift_staffs == user:
            new_status = request.POST.get('status')
            if new_status == 'Completed':
                service.status = new_status
                service.assigned_to.shift_staffs.status = 'vacant'
                service.assigned_to.shift_staffs.save()
                service.save()

                messages.success(request, "Service status updated successfully.")
                assign_service_from_queue(service.assigned_to.shift_staffs)
                return redirect('srm:staff_service')
    view_name = request.resolver_match.view_name
    if view_name == "srm:staff_update_service_status" and user_role == 'User':
        return redirect('srm:staff_service')
    raise PermissionDenied("You are not authorized to perform this action.")

# Assigned Service to the vacant staff from the queue.
def assign_service_from_queue(vacant_staff):
    try:
        next_service_request = ServiceRequestQueue.objects.first()
        if next_service_request:
            service = next_service_request.service_request
            service.assigned_to = ShiftSchedule.objects.filter(shift_staffs=vacant_staff).first()
            service.status = 'In Progress'
            service.save()
            vacant_staff.status = 'engaged'
            vacant_staff.save()
            next_service_request.delete()
        pass
    except Exception as e:
        log.error("Error freeing up staff", error=str(e))

# Service Genearte View.
def GenerateServiceView(request):
    if request.method == 'POST':
        form = ServiceGenerateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            new_service = form.save(commit=False)
            new_service.created_by = request.user
            new_service.save()
            return redirect()
    else:
        form = ServiceGenerateForm(user=request.user)
    context = {'form': form}
    return render(request, 'service_generate.html', context)

# All Service View.
def RequestServiceView(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    request_service = Service.objects.filter(created_by = user).order_by('-created_at')
    assign_service = Service.objects.filter(assigned_to__shift_staffs = user).order_by('-created_at')
    page_number = request.GET.get('page')
    if user.department.name in ['GDA', 'General Duty Assistant']:
        paginator = Paginator(assign_service, 10) 
        page_obj = paginator.get_page(page_number)
    else:
        paginator = Paginator(request_service, 10) 
        page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    view_name = request.resolver_match.view_name
    if view_name == "srm:admin_service" and user_role == 'Admin':
        return render(request, 'srm_admin_service.html', context)
    if view_name == "srm:staff_service" and user_role == 'User':
        return render(request, 'srm_staff_service.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Shift Schedule View.
def ShiftSchedules(request): 
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    schedules = ShiftSchedule.objects.filter(
        Q(shift_staffs__department__name='GDA') | Q(shift_staffs__department__name='General Duty Assistant')
        )
    page_number = request.GET.get('page')
    paginator = Paginator(schedules, 10) 
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    view_name = request.resolver_match.view_name
    if view_name == "srm:schedule" and user_role == 'Admin':
        return render(request, 'shift_schedule.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Shift Schedule Form View.
def ShiftScheduleView(request):
    if request.method == 'POST':
        form = ShiftScheduleForm(request.POST, user=request.user)
        if form.is_valid():
            new_schedule = form.save(commit=False)
            new_schedule.created_by = request.user
            new_schedule.save()
            messages.success(request, "Shift schedule created successfully.")
            return redirect('srm:schedule')
    else:
        form = ShiftScheduleForm(user=request.user)
    context = {
        'form': form,
    }
    return render(request, 'schedule.html', context)

