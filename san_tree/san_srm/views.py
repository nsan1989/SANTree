from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from .models import *
from .forms import *
from accounts.models import CustomUsers
from django.http import JsonResponse

# Admin Dashboard view.
def AdminDashboard(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    dept_users = CustomUsers.objects.filter(department = user.department).exclude(role='Admin')
    user_count = dept_users.count()
    vacant_users = dept_users.filter(status = 'vacant')
    vacant = vacant_users.count()
    engaged_users = dept_users.filter(status = 'engaged')
    engage = engaged_users.count()
    services = Service.objects.filter(assigned_to__department = user.department).all().count()
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
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    services = Service.objects.filter(assigned_to = user).all().count()
    open_service = Service.objects.filter(assigned_to = user, status = 'Completed').count()
    progress_service = Service.objects.filter(assigned_to = user, status = 'In Progress').count()
    completed_service = Service.objects.filter(assigned_to = user, status = 'Completed').count()
    context = {
        'current_user': user,
        'total_service': services,
        'open_serv': open_service,
        'prog_serv': progress_service,
        'comp_serv': completed_service
    }
    view_name = request.resolver_match.view_name
    if view_name == "srm:staff_dashboard" and user_role == 'User':
        return render(request, 'srm_staff_dashboard.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Profile View.
def ProfileView(request):
    user = request.user
    try:
        user_role = user.role
    except:
        PermissionDenied("User profile not found.")
    context = {
        'profile': user,
    }
    view_name = request.resolver_match.view_name
    if view_name == "srm:staff_profile" and user_role == 'User':
        return render(request, 'profile.html', context)
    if view_name == "srm:admin_profile" and user_role == 'Admin':
        return render(request, 'profile.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Load Service Types.
def load_service_types(request):
    department_id = request.GET.get('department')
    tasks_types = ServiceTypes.objects.filter(department_id=department_id).order_by('name')
    return JsonResponse(list(tasks_types.values('id', 'name')), safe=False)

# Service Request View.
def ServiceView(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            new_service = form.save(commit=False)
            new_service.created_by = request.user
            service_type = form.cleaned_data.get('service_type')
            location = form.cleaned_data.get('location')
            new_service.save()
            return redirect()
    else:
        form = ServiceForm(user=request.user)
    context = {'form': form}
    return render(request, 'service_request.html', context)

# All Service View.
def AllServiceView(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    new_service = Service.objects.filter(created_by = user)
    context = {
        'services': new_service
    }
    view_name = request.resolver_match.view_name
    if view_name == "srm:admin_service" and user_role == 'Admin':
        return render(request, 'srm_admin_service.html', context)
    if view_name == "srm:staff_service" and user_role == 'User':
        return render(request, 'srm_staff_service.html', context)
    raise PermissionDenied("You are not authorized to view this page.")
    