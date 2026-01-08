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
from datetime import datetime, time

log = structlog.get_logger()

# Tasks Pie Chart
def ServicePieChart(request):

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    services = Service.objects.filter(created_by = request.user)

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            services = services.filter(created_at__range=(start, end))
        except ValueError:
            pass

    open_serv = services.filter(status = 'Open').count()
    prog_serv = services.filter(status = 'In Progress').count()
    wait_serv = services.filter(status = 'Waiting').count()
    pen_serv = services.filter(status = 'Pending').count()
    hold_serv = services.filter(status = 'On Hold').count()
    comp_serv = services.filter(status = 'Completed').count()
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
    user_services = Service.objects.filter(
        Q(assigned_to__shift_staffs=user) | Q(created_by=user),
        Q(status__in=['Open', 'In Progress', 'On Hold', 'Completed'])
    ).order_by('-created_at')[:10]
    assign_service = Service.objects.filter(assigned_to__shift_staffs = user).all().count()
    open_assign_service = Service.objects.filter(assigned_to__shift_staffs = user, status = 'Open').count()
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
        'user_services': user_services,
        'total_assign_service': assign_service,
        'open_assign_service': open_assign_service,
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

    priorities = [
        ('high', 'High'),
        ('mid', 'Mid'),
        ('low', 'Low'),
    ]

    service_types = ServiceTypes.objects.all()
    blocks = Blocks.objects.all()
    locations = Location.objects.all()

    # filter GDA or General Duty Staff.
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

            # to get local time time
            now_local = timezone.localtime(timezone.now())

            # to store active staff with status vacant
            eligible_shift_schedules = []

            for staff in provider_staff:
                staff_status = (staff.status or '').strip().lower()
                if staff_status != 'vacant':
                    continue

                is_engaged = Service.objects.filter(
                    assigned_to__shift_staffs_id = staff.id,
                    status = "Open"
                ).exists()

                schedule_qs = ShiftSchedule.objects.filter(
                    shift_block=new_service.service_block,
                    shift_staffs_id=staff.id,
                )               

                if is_engaged:
                    continue

                for s in schedule_qs:
                    s_start = timezone.localtime(s.start_time)
                    s_end = timezone.localtime(s.end_time)
                    active = s_start <= now_local <= s_end
                    if active:
                        eligible_shift_schedules.append(s)

            if not eligible_shift_schedules:
                new_service.status = 'Waiting'
                new_service.save()
                ServiceRequestQueue.objects.create(service_request=new_service)
            else:
                staff_loads = [
                    (s, Service.objects.filter(assigned_to=s).count())
                    for s in eligible_shift_schedules
                ]
                selected_shift = sorted(staff_loads, key=lambda x: x[1])[0][0]

                new_service.assigned_to = selected_shift
                new_service.status = 'Open'
                new_service.save()
            
            if request.user.role == 'Admin':
                return redirect('srm:admin_dashboard')
            else:
                return redirect('srm:staff_dashboard')
    else:
        form = ServiceForm(user=request.user)
    context = {
        'form': form, 
        'service_types': service_types, 
        'priorities': priorities,
        'blocks': blocks,
        'locations': locations
    }
    return render(request, 'service_request.html', context)

# Free up the staff when exceeds timestamp.
def free_up_staff():
    try:
        prog_service = Service.objects.filter(status='In Progress')
        if prog_service.exists():
            for service in prog_service:
                if service.started_at <= timezone.now() - timedelta(minutes=15):
                    staff = service.assigned_to
                    if staff and staff.status == 'engaged':
                        staff.status = 'vacant'
                        staff.save()
                        service.status = 'Pending'
                        service.assigned_to = None
                        service.save()
                    assign_service_from_queue(staff)
                        
    except Exception as e:
        log.error("Error freeing up staff", error=str(e))

# Put on hold if the service exceeds creation date
def hold_service():
    try:
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        start_of_yesterday = timezone.make_aware(
            datetime.combine(yesterday, datetime.min.time())
        )
        end_of_yesterday = timezone.make_aware(
            datetime.combine(yesterday, datetime.max.time())
        )
        
        services = Service.objects.filter(
            created_at__lte=end_of_yesterday,
            status__in=['Open', 'In Progress']
        )

        for serv in services:
            staff = getattr(serv.assigned_to, "shift_staffs", None)

            # Free staff if assigned
            if staff and staff.status == 'engaged':
                staff.status = 'vacant'
                staff.save()

            # Put service on hold
            serv.status = 'On Hold'
            serv.assigned_to = None
            serv.save()

            assign_service_from_queue(staff)

    except Exception as e:
        log.error("Error freeing up staff", error=str(e))

# Free up the staff when service is completed.
def free_up_completed_staff(request, id):
    user = request.user
    if not hasattr(user, 'role'):
        raise PermissionDenied("User Profile not found.")
    service = None
    try:
        service = Service.objects.get(id=id)
    except Service.DoesNotExist:
        raise PermissionDenied("Service not found.")

    if request.method == 'POST':
        obj = service # or ano_service
        assigned_staff = obj.assigned_to

        if not assigned_staff:
            raise PermissionDenied("No shift assigned.")

        staff = assigned_staff.shift_staffs
        
        if user.role != 'User' or staff != user:
            raise PermissionDenied("You are not authorized.")
        
        new_status = request.POST.get('status')
        
        if new_status == 'In Progress':
            obj.status = new_status
            assigned_staff.status = 'engaged'
            assigned_staff.save()
            obj.save()
            return redirect('srm:staff_service')
        elif new_status == 'Completed':
            obj.status = new_status
            shift_schedule = obj.assigned_to
            staff = shift_schedule.shift_staffs
            staff.status = 'vacant'
            staff.save()
            obj.save()
            messages.success(request, "Service status updated successfully.")
            assign_service_from_queue(staff)
            return redirect('srm:staff_service')
        elif new_status == 'On Hold':
            obj.status = new_status
            assigned_staff.status = 'vacant'
            assigned_staff.save()
            obj.save()
            messages.success(request, "Service status updated successfully.")
            return redirect('srm:staff_service')
            
    view_name = request.resolver_match.view_name
    if view_name == "srm:staff_update_service_status" and user.role == 'User':
        return redirect('srm:staff_service')
    raise PermissionDenied("You are not authorized to perform this action.")

# Assigned Service to the vacant staff from the queue.
def assign_service_from_queue(vacant_staff):
    now_local = timezone.localtime(timezone.now())
    try:
        if not vacant_staff or vacant_staff.status != 'vacant':
            return
        
        queue_service = ServiceRequestQueue.objects.order_by('created_at').first()
        if not queue_service:
            return
        
        service_obj = queue_service.service_request
        
        eligible_staff = ShiftSchedule.objects.filter(
            shift_block=service_obj.service_block,
            shift_staffs=vacant_staff,
            start_time__lte=now_local,
            end_time__gte=now_local
        ).first()
        
        service_obj.assigned_to = eligible_staff
        service_obj.status = 'Open'
        service_obj.save()

        vacant_staff.status = 'engaged'
        vacant_staff.save()

        queue_service.delete()

    except Exception as e:
        log.error("Error assigning service from queue", error=str(e))

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
    if user.role == 'Admin':
        assign_service = Service.objects.filter(assigned_to__shift_staffs__department__name = user.department).order_by('-created_at')
    else:
        assign_service = Service.objects.filter(assigned_to__shift_staffs = user).order_by('-created_at')
    latest_remark_subquery = ServiceRemarks.objects.filter(service=OuterRef('pk')).order_by('-created_at')
    request_service = request_service.annotate(
        latest_remark_text=Subquery(latest_remark_subquery.values('remarks')[:1])
    )
    assign_service = assign_service.annotate(
        latest_remark_text=Subquery(latest_remark_subquery.values('remarks')[:1])
    )
    selected_option = request.GET.get('status')
    if selected_option == 'request':
        services = services.filter(status=selected_option)
    else:
        if user.department.name in ['GDA', 'General Duty Assistant']:
            services = assign_service
        else:
            services = request_service
    selected_option = request.GET.get('status')
    if selected_option:
        services = services.filter(status=selected_option)
    paginator = Paginator(services, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    service_status = Service._meta.get_field('status').choices
    context = {
        'page_obj': page_obj,
        'selected_option': selected_option,
        'status': service_status,
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
    today = timezone.localdate()
    start_of_day = timezone.make_aware(timezone.datetime.combine(today, time(0, 0, 0)))
    end_of_day = timezone.make_aware(timezone.datetime.combine(today, time(23, 59, 59)))
    schedules = ShiftSchedule.objects.filter(
    Q(shift_staffs__department__name__in=['GDA', 'General Duty Assistant']),
    start_time__gte=start_of_day,
    end_time__lte=end_of_day
    ).order_by("-id")
    page_number = request.GET.get('page')
    paginator = Paginator(schedules, 10) 
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    view_name = request.resolver_match.view_name
    if view_name == "srm:schedule" and user_role == 'Admin':
        return render(request, 'shift_schedule.html', context)
    if view_name == "srm:schedule" and user_role == 'User':
        return render(request, 'shift_schedule.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Shift Schedule Form View.
def ShiftScheduleView(request):
    shift_choices = [
        ('morning', 'Morning'),
        ('evening', 'Evening'),
        ('day', 'Day'),
        ('night', 'Night'),
    ]
    shift_blocks = Blocks.objects.all()
    shift_staffs = CustomUsers.objects.filter(
        (Q(department__name='GDA') | Q(department__name='General Duty Assistant')) & Q(role='User')
    )
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
        'choices': shift_choices,
        'blocks': shift_blocks,
        'staffs': shift_staffs,
    }
    return render(request, 'schedule.html', context)

# Free up the staff if service status is 'On Hold' and exceeds timestamp.
def free_up_onhold_staff():
    try:
        onhold_service = Service.objects.filter(status='On Hold').all()
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
