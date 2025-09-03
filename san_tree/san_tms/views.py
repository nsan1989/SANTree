from django.shortcuts import render, redirect, get_object_or_404
from .forms import TasksForm, RemarkForm
from .models import TasksTypes, Tasks, TasksRemarks
from accounts.models import CustomUsers
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from datetime import date
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from threading import Lock
plot_lock = Lock()
from django.http import HttpResponse

# Tasks Pie Chart
def TasksPieChart(request):
    open_tasks = Tasks.objects.filter(status = 'Open').count()
    in_progress = Tasks.objects.filter(status = 'In Progress').count()
    waiting = Tasks.objects.filter(status = 'Waiting').count()
    completed = Tasks.objects.filter(status = 'Completed').count()
    if open_tasks + in_progress + waiting + completed == 0:
        labels = ['No Data']
        sizes = [1]
        colors = ['#d3d3d3']
    else:
        raw_data = [
            ('Open', open_tasks, '#eb0707'),
            ('Progress', in_progress, '#ebd807'),
            ('Waiting', waiting, "#07bdeb"),
            ('Completed', completed, '#4feb07')
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

# Task Dashboard view.
def TaskDashboard(request):
    user = request.user
    try:
        user_role = user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")
    total_users = CustomUsers.objects.filter(
        Q(department = user.department) &
        ~Q(id=user.id)
        ).all().count()
    incharge_tasks = Tasks.objects.filter(created_by = user).all().count()
    complete_tasks = Tasks.objects.filter(
        Q(department = user.department) &
        Q(status = 'Completed')
        ).all().count()
    dept_users = CustomUsers.objects.filter(department = user.department).exclude(role='Admin')
    vacant_users = dept_users.filter(status = 'vacant')
    engaged_users = dept_users.filter(status = 'engaged')

    context = {
        'current_user': user,
        'date': date.today(),
        'created_tasks': incharge_tasks,
        'comp_tasks': complete_tasks,
        'tot_users': total_users,
        'engage': engaged_users,
        'vacant': vacant_users,
    }

    view_name = request.resolver_match.view_name
    if view_name == "tms:admin_dashboard" and user_role == 'Admin':
        return render(request, 'tasks_dashboard.html', context)

    raise PermissionDenied("You are not authorized to view this page.")

# Staff Dashboard View.
def StaffDashboard(request):
    user = request.user
    try:
        user_role = user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")
    staff_tasks = Tasks.objects.filter(assigned_to = user).all().count()
    completed = Tasks.objects.filter(status='Completed').all().count()
    in_progress = Tasks.objects.filter(status='In Progress').all().count()
    context = {
        'current_user': user,
        'assigned_tasks': staff_tasks,
        'complete': completed,
        'progress': in_progress
    }
    view_name = request.resolver_match.view_name
    if view_name == "tms:staff_dashboard" and user_role == 'User':
        return render(request, 'staff_dashboard.html', context)

# Task Profile View.
def TaskProfile(request):
    user = request.user
    try:
        user_role = user.role
    except:
        PermissionDenied("User profile not found.")
    context = {
        'profile': user,
    }
    view_name = request.resolver_match.view_name
    if view_name == "tms:staff_profile" and user_role == 'User':
        return render(request, 'tasks_profile.html', context)
    if view_name == "tms:admin_profile" and user_role == 'Admin':
        return render(request, 'tasks_profile.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Load Task Types.
def load_tasks_types(request):
    department_id = request.GET.get('department')
    tasks_types = TasksTypes.objects.filter(department_id=department_id).order_by('name')
    return JsonResponse(list(tasks_types.values('id', 'name')), safe=False)

# Load Task Staff.
def load_tasks_staffs(request):
    department_id = request.GET.get('department')
    staff = CustomUsers.objects.filter(department_id=department_id, role='User').values('id', 'username')
    return JsonResponse(list(staff), safe=False)

# Raised a Task View.
def TasksView(request):
    if request.method == 'POST':
        form = TasksForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.created_by = request.user
            department = form.cleaned_data.get('department')
            task_type = form.cleaned_data.get('tasks_types')
            assigned_user = form.cleaned_data.get('assigned_to')
            if not task_type:
                types = TasksTypes.objects.filter(department=department)
                if types.count() == 1:
                    form.instance.task_type = types.first()
                elif types.count() > 1 and types == 'others':
                    form.add_error('task_type', 'Please select a task type.')
                    return render(request, 'raised_tasks.html', {'form', form})
            if assigned_user:
                if assigned_user.status == 'vacant':
                    new_task.assigned_to = assigned_user
                    assigned_user.status = 'engaged'
                    assigned_user.save()
                else:
                    form.add_error('assigned_to', f"{assigned_user.username} is not vacant.")
                    return render(request, 'raised_tasks.html', {'form': form})
            new_task.save()
            return redirect('tms:tasks')
    else:
        form = TasksForm(user=request.user)
    context = {'form': form}
    return render(request, 'raised_tasks.html', context)

# All Tasks View.
def AllTasks(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    new_tasks = Tasks.objects.filter(
        Q(created_by = user)
    )
    context = {
        'tasks': new_tasks
    }
    view_name = request.resolver_match.view_name
    if view_name == "tms:tasks" and user_role == 'Admin':
        return render(request, 'all_tasks.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# My Tasks View
def MyTasks(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    my_tasks = Tasks.objects.filter(
        Q(department = user.department) & 
        Q(assigned_to = user)
    )

    for tasks in my_tasks:
        if tasks.status == 'Waiting':
            current_time = timezone.now()
            elapsed = current_time - tasks.waiting_time
            if elapsed > timedelta(seconds=180):
                tasks.assigned_to.status = 'vacant'
                tasks.assigned_to.save()

        tasks.save()

    context = {
        'tasks': my_tasks
    }
    view_name = request.resolver_match.view_name
    if view_name == "tms:my_tasks" and user_role == 'User':
        return render(request, 'my_tasks.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Tasks Details.
def TasksDetails(request, id):
    tasks = get_object_or_404(Tasks, id=id)
    user = request.user
    try:
        user_role = user.role
    except:
        PermissionDenied("User profile not found.")
    task_remark = TasksRemarks.objects.filter(tasks_id = id).order_by('-created_at')
    context = {
        'tasks': tasks,
        'remark': task_remark,
    }
    view_name = request.resolver_match.view_name
    if view_name == "tms:staff_tasks_details" and user_role == 'User':
        return render(request, 'tasks_details.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Tasks Details.
def AllTasksDetails(request, id):
    tasks = get_object_or_404(Tasks, id=id)
    user = request.user
    try:
        user_role = user.role
    except:
        PermissionDenied("User profile not found.")
    task_remark = TasksRemarks.objects.filter(tasks_id = id).order_by('-created_at')
    context = {
        'tasks': tasks,
        'remark': task_remark,
    }
    view_name = request.resolver_match.view_name
    if view_name == "tms:admin_tasks_details" and user_role == 'Admin':
        return render(request, 'all_tasks_details.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Update Tasks Status.
def UpdateStatus(request, id):
    user = request.user
    try:
        user_role = user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")

    tasks = get_object_or_404(Tasks, id=id)

    if tasks.status == 'Completed':
        messages.warning(request, f"Cannot update status. Complaint is already {tasks.status}.")
        return redirect('tms:my_tasks')

    if request.method == "POST":
        new_status = request.POST.get('status')

        if tasks.status == 'Completed':
            messages.warning(request, f"Cannot update status. Complaint is already {tasks.status}.")
            return redirect('tms:my_tasks')

        tasks.status = new_status

        if new_status == 'Completed':
            tasks.completed_at = timezone.now()
            tasks.assigned_to.status = 'Vacant'
            tasks.assigned_to.save() 
            tasks.save()
        else:
            tasks.completed_at = None

        if new_status == 'Waiting':
            tasks.waiting_time = timezone.now()
            tasks.save()
            
        tasks.save()
        messages.success(request, "Status updated successfully.")
        if user.role == 'User':
            return redirect('tms:my_tasks')
        else:
            return redirect('tms:tasks')
    
    view_name = request.resolver_match.view_name
    if view_name == 'tms:staff_update_task_status' and user_role == 'User':
        return redirect('tms:my_tasks')
    if view_name == 'tms:admin_update_task_status' and user_role == 'Admin':
        return redirect('tms:tasks')
    raise PermissionDenied("You are not authorized to view this page.")    

# Task Remark View.
def RemarkComplaint(request, task_id):
    task = get_object_or_404(Tasks, id=task_id)
    if request.method == 'POST':
        form = RemarkForm(request.POST, request.FILES)
        if form.is_valid():
            remark = form.save(commit=False)
            remark.tasks = task
            remark.remarks = form.cleaned_data.get('remarks')
            remark.created_by = request.user
            remark.save()

            if request.user.designation == 'Staff':
                return redirect('tms:my_tasks')
            else:
                return redirect('tms:tasks')

    else:
        form = RemarkForm()
    context = {
        'form': form,
        'task': task
    }
    return render(request, 'remark.html', context)
