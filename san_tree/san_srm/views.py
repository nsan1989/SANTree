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
import structlog
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from threading import Lock
plot_lock = Lock()
from django.http import HttpResponse
from django.db.models import OuterRef, Subquery
from core.models import AnonymousServiceGenerate
from datetime import datetime

log = structlog.get_logger()
now = timezone.now()
today = timezone.localdate()

# Tasks Pie Chart
def ServicePieChart(request):
    open_serv = Service.objects.filter(status = 'Open', created_by = request.user).count()
    prog_serv = Service.objects.filter(status = 'In Progress', created_by = request.user).count()
    wait_serv = Service.objects.filter(status = 'Waiting', created_by = request.user).count()
    pen_serv = Service.objects.filter(status = 'Pending', created_by = request.user).count()
    hold_serv = Service.objects.filter(status = 'On Hold', created_by = request.user).count()
    comp_serv = Service.objects.filter(status = 'Completed', created_by = request.user).count()
    if open_serv + prog_serv + wait_serv + pen_serv + hold_serv + comp_serv == 0:
        labels = ['No Data']
        sizes = [1]
        colors = ['#d3d3d3']
    else:
        raw_data = [
            ('Open', open_serv, '#cccccc'),
            ('In Progress', prog_serv, '#ff6600'),
            ('Waiting', wait_serv, "#ff9900"),
            ('Pending', pen_serv, "#990000"),
            ('On Hold', hold_serv, "#993300"),
            ('Completed', comp_serv, '#003300')
            ]
    
        filtered_data = [(label, size, color) for label, size, color in raw_data if size > 0]
        labels, sizes, colors = zip(*filtered_data)

    buffer = io.BytesIO()

    with plot_lock:
        bg_color = (0, 0, 0, 0.4)
        fig, ax = plt.subplots(figsize=(4, 2), facecolor=bg_color) 
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, textprops={'color': 'white'})
        ax.axis('equal')
        plt.savefig(buffer, format='png', facecolor=fig.get_facecolor())
        plt.close(fig)
    
    buffer.seek(0)
    return HttpResponse(buffer.read(), content_type='image/png')

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
    services = Service.objects.filter(assigned_to__shift_staffs__department__name= user.department)
    total_serv = services.count()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            services = services.filter(created_at__range=(start, end))
        except ValueError:
            pass
    context = {
        'sevices': services.order_by('-created_at'),
        'current_user': user,
        'all_users': user_count,
        'engage_user': engaged_users,
        'engaged': engage,
        'vacant_user': vacant_users,
        'vacants': vacant,
        'total_service': total_serv,
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
    service_created = Service.objects.filter(created_by = user)
    created_services = service_created.count()
    open_created_service = Service.objects.filter(created_by = user, status = 'Open').count()
    progress_created_service = Service.objects.filter(created_by = user, status = 'In Progress').count()
    completed_created_service = Service.objects.filter(created_by = user, status = 'Completed').count()
    assign_service = Service.objects.filter(assigned_to__shift_staffs = user).all().count()
    progress_assign_service = Service.objects.filter(assigned_to__shift_staffs = user, status = 'In Progress').count()
    completed_assign_service = Service.objects.filter(assigned_to__shift_staffs = user, status = 'Completed').count()
    service_generated_by = GenerateService.objects.filter(generate_by__shift_staffs = user).count()
    my_shift = ShiftSchedule.objects.filter(
        shift_staffs = user, 
        start_time__gte=today, 
        end_time__lt=tomorrow
        ).all()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            service_created = service_created.filter(created_at__range=(start, end))
        except ValueError:
            pass
    if request.method == 'POST':
        form = ServiceGenerateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            new_service = form.save(commit=False)
            shift_schedule = ShiftSchedule.objects.filter(shift_staffs=request.user).first()

            if shift_schedule:
                new_service.generate_by = shift_schedule
                new_service.save()

                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({
                        "success": True,
                        "id": new_service.id,
                        "generate_number": new_service.generate_number,
                        "service_type": str(new_service.service_type),
                        "from_location": str(new_service.from_location),
                        "to_location": str(new_service.to_location),
                        "status": new_service.status,
                        "generate_at": new_service.generate_at.strftime("%Y-%m-%d %H:%M"),
                    })

                messages.success(request, "Service generated successfully!")
                return redirect('srm:staff_dashboard')
            else:
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({"success": False, "error": "Shift schedule not found"}, status=400)
                messages.error(request, "Shift schedule not found")
                return redirect('srm:staff_dashboard')
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
            messages.error(request, "Invalid form")
    else:
        form = ServiceGenerateForm(user=request.user)
    context = {
        'services': service_created.order_by('-created_at'),
        'current_user': user,
        'total_created_service': created_services,
        'open_created_serv': open_created_service,
        'prog_created_serv': progress_created_service,
        'comp_created_serv': completed_created_service,
        'total_assign_service': assign_service,
        'prog_assign_serv': progress_assign_service,
        'comp_assign_serv': completed_assign_service,
        'shifts': my_shift,
        'generate': service_generated_by,
        "show_action_buttons": user.status == "engaged",
        "form": form
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
                        shift_block=new_service.service_block,
                        shift_staffs__id=staff.id,
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
                        new_service.status = 'Open'
                        new_service.save()
                        break

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
        ano_service = AnonymousServiceGenerate.objects.filter(status='In Progress').all()
        if prog_service.exists():
            for service in prog_service:
                if service.created_at <= timezone.now() - timedelta(minutes=30):
                    staff = service.assigned_to.shift_staffs
                    if staff and staff.status == 'engaged':
                        staff.status = 'vacant'
                        staff.save()
                        
                        service.status = 'Pending'
                        service.save()
                    assign_service_from_queue(staff)
        elif ano_service.exists():
            for service in ano_service:
                if service.generate_at <= timezone.now() - timedelta(minutes=30):
                    staff = service.assigned_to.shift_staffs
                    if staff and staff.status == 'engaged':
                        staff.status = 'vacant'
                        staff.save()

                        service.status = 'Pending'
                        service.save()
                        
    except Exception as e:
        log.error("Error freeing up staff", error=str(e))

# Free up the staff when service is completed.
def free_up_completed_staff(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User Profile not found.")
    service = None
    ano_service = None
    try:
        service = Service.objects.get(id=id)
    except Service.DoesNotExist:
        try:
            ano_service = AnonymousServiceGenerate.objects.get(id=id)
        except AnonymousServiceGenerate.DoesNotExist:
            raise PermissionDenied("Service not found.")

    if request.method == 'POST':
        obj = service or ano_service
        assigned_staff = getattr(getattr(obj, "assigned_to", None), "shift_staffs", None)
        if user_role == 'User' and assigned_staff == user:
            new_status = request.POST.get('status')
            if not assigned_staff:
                raise PermissionDenied("No staff assigned to this service.")
            if new_status == 'Completed':
                obj.status = new_status
                assigned_staff.status = 'vacant'
                assigned_staff.save()
                obj.save()
                messages.success(request, "Service status updated successfully.")
                assign_service_from_queue(assigned_staff)
                return redirect('srm:staff_service')
            elif new_status == 'On Hold':
                obj.status = new_status
                assigned_staff.status = 'engaged'
                assigned_staff.save()
                obj.save()
                messages.success(request, "Service status updated successfully.")
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
            service.assigned_to = ShiftSchedule.objects.filter(shift_block = service.service_block, shift_staffs=vacant_staff).first()
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
            user = CustomUsers.objects.filter(username = request.user)

            if user:
                new_service.generate_by = user
                new_service.save()

                user.status = 'engaged'
                user.save()

                messages.success(request, "Service generated successfully!")
                return redirect('srm:staff_dashboard')
            else:
                messages.error(request, "There was an error with the form submission.")
                return redirect('srm:staff_dashboard')
        else:
            messages.error(request, "There was an error with the form submission.")
    else:
        form = ServiceGenerateForm(user=request.user)
    context = {'form': form}
    return render(request, 'service_generate.html', context)

# All Generated Service
def AllGeneratedService(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    generate_serv = GenerateService.objects.filter(generate_by__shift_staffs = user).order_by('generate_at')
    context = {
        'generate': generate_serv
    }
    view_name = request.resolver_match.view_name
    if view_name == "srm:all_generate_service" and user_role == 'User':
        return render(request, 'all_generate_service.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# All Service View.
def RequestServiceView(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    request_service = Service.objects.filter(created_by = user).order_by('-created_at')
    assign_service = Service.objects.filter(assigned_to__shift_staffs = user).order_by('-created_at')
    anonymous_service = AnonymousServiceGenerate.objects.filter(assigned_to__shift_staffs = user)
    latest_remark_subquery = ServiceRemarks.objects.filter(service=OuterRef('pk')).order_by('-created_at')
    request_service = request_service.annotate(
        latest_remark_text=Subquery(latest_remark_subquery.values('remarks')[:1])
    )
    assign_service = assign_service.annotate(
        latest_remark_text=Subquery(latest_remark_subquery.values('remarks')[:1])
    )
    selected_option = request.GET.get('serviceType', 'default')
    if selected_option == 'request':
        services = request_service
    elif selected_option == 'generate':
        services = assign_service
    elif selected_option == 'anonymous':
        services = anonymous_service
    else:
        if user.department.name in ['GDA', 'General Duty Assistant']:
            services = assign_service
        else:
            services = request_service
    page_number = request.GET.get('page')
    paginator = Paginator(services, 10)
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'selected_option': selected_option,
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
    start_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
    end_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))
    schedules = ShiftSchedule.objects.filter(
    Q(shift_staffs__department__name__in=['GDA', 'General Duty Assistant']),
    start_time__gte=start_of_day,
    end_time__lte=end_of_day
    ).order_by("-id")
    page_number = request.GET.get('page')
    paginator = Paginator(schedules, 10) 
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    view_name = request.resolver_match.view_name
    if view_name == "srm:schedule" and user_role == 'Admin':
        return render(request, 'shift_schedule.html', context)
    if view_name == "srm:schedule" and user_role == 'User':
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

# Free up the staff if service status is 'On Hold' and exceeds timestamp.
def free_up_onhold_staff():
    try:
        onhold_service = Service.objects.filter(status='On Hold').all()
        onhold_ano_service = AnonymousServiceGenerate.objects.filter(status='On Hold').all()
        if onhold_service.exists():
            for service in onhold_service:
                if service.created_at <= timezone.now() - timedelta(minutes=25):
                    staff = service.assigned_to.shift_staffs
                    if staff and staff.status == 'engaged':
                        staff.status = 'vacant'
                        staff.save()
                        
                        service.status = 'Pending'
                        service.save()
                    assign_service_from_queue(staff)
        elif onhold_ano_service.exists():
            for service in onhold_ano_service:
                if service.generate_at <= timezone.now() - timedelta(minutes=25):
                    staff = service.assigned_to.shift_staffs
                    if staff and staff.status == 'engaged':
                        staff.status = 'vacant'
                        staff.save()
                    assign_service_from_queue(staff)

    except Exception as e:
        log.error("Error freeing up staff", error=str(e))

# free up the staff when the service status is 'pending'.
def free_up_pending_staff(request):
    try:
        pen_service = Service.objects.filter(status='Pending').all()
        pen_ano_service = AnonymousServiceGenerate.objects.filter(status='Pending').all()
        if pen_service.exists():
            for service in pen_service:
                staff = pen_service.assigned_to.shift_staffs
                if staff and staff.status == 'engaged':
                    staff.status = 'vacant'
                    staff.save()
                    assign_service_from_queue(staff)
        elif pen_ano_service.exists():
            for service in pen_ano_service:
                staff = pen_ano_service.assigned_to.shift_staffs
                if staff and staff.status == 'engaged':
                    staff.status = 'vacant'
                    staff.save()
                    assign_service_from_queue(staff)
    except Exception as e:
        log.error("Error freeing up staff", error=str(e))

# Service Remark View.
def ServiceRemark(request, id):
    service = get_object_or_404(Service, id=id)
    if request.method == 'POST':
        form = ServiceRemarkForm(request.POST, request.FILES)
        if form.is_valid():
            remark = form.save(commit=False)
            remark.service = service
            remark.remarks = form.cleaned_data.get('remarks')
            remark.created_by = request.user
            remark.save()

            if request.user.role == 'User':
                return redirect('srm:staff_service')
            else:
                return redirect('srm:all_services')

    else:
        form = ServiceRemarkForm()
    context = {
        'form': form,
        'service': service,
    }
    return render(request, 'srm_remarks.html', context)

# Updating user status.
def UpdateUserStatus(request):
    user = request.user
    if request.method == "POST":
        status = request.POST.get("status")
        user.status = status 
        user.save()
        return JsonResponse({"success": True, "status": user.status})
    return JsonResponse({"success": False})

# Shift Edit Form View.
def ShiftEditView(request, id):
    edit_schedule = get_object_or_404(ShiftSchedule, id=id)
    if request.method == 'POST':
        form = ShiftEditForm(request.POST, instance=edit_schedule, user=request.user)
        if form.is_valid():
            edit_schedule = form.save(commit=False)
            edit_schedule.created_by = request.user
            edit_schedule.save()
            messages.success(request, "Shift schedule edited successfully.")
            return redirect('srm:schedule')
    else:
        form = ShiftEditForm(instance=edit_schedule ,user=request.user)
    context = {
        'form': form,
        'edit_schedule': edit_schedule
    }
    return render(request, 'shift_edit.html', context)
