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
from django.utils.dateparse import parse_date
from datetime import datetime
from django.core.paginator import Paginator

# Tasks Pie Chart
def TasksPieChart(request):
    # --- date filter ---
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    tasks = Tasks.objects.all()

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            tasks = tasks.filter(created_at__range=[start, end])
        except ValueError:
            pass

    # --- counts by status ---
    open_count = tasks.filter(status='Open').count()
    progress_count = tasks.filter(status='In Progress').count()
    waiting_count = tasks.filter(status='Waiting').count()
    review_count = tasks.filter(status='Review').count()
    completed_count = tasks.filter(status='Completed').count()

    if open_count + progress_count + waiting_count + review_count + completed_count == 0:
        labels = ['No Data']
        sizes = [1]
        colors = ['#d3d3d3']
    else:
        raw_data = [
            ('Open', open_count, '#eb0707'),
            ('In Progress', progress_count, '#ebd807'),
            ('Waiting', waiting_count, "#07bdeb"),
            ('Review', review_count, "#ff9900"),
            ('Completed', completed_count, '#4feb07'),
        ]
        filtered = [(l, s, c) for l, s, c in raw_data if s > 0]
        labels, sizes, colors = zip(*filtered)

    # --- draw pie chart ---
    buffer = io.BytesIO()
    fig, ax = plt.subplots(figsize=(4, 2), facecolor=(0, 0, 0, 0.4))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%', colors=colors,
        startangle=90, textprops={'color': 'white'}
    )
    ax.axis('equal')

    plt.savefig(buffer, format='png', facecolor=fig.get_facecolor(), transparent=True)
    plt.close(fig)
    buffer.seek(0)

    return HttpResponse(buffer.read(), content_type='image/png')

# Admin Dashboard view.
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
    tasks = Tasks.objects.filter(assigned_to = user)
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            tasks = tasks.filter(created_at__range=(start, end))
        except ValueError:
            pass

    staff_tasks = tasks.count()
    open = tasks.filter(status='Open')
    open_count = open.count()
    completed = tasks.filter(status='Completed')
    complete_count = completed.count()
    in_progress = tasks.filter(status='In Progress')
    progress_count = in_progress.count()
    context = {
        'tasks': tasks.order_by('-created_at'),
        'current_user': user,
        'assigned_tasks': staff_tasks,
        'open': open,
        'open_count': open_count,
        'complete': completed,
        'comp_count': complete_count,
        'progress': in_progress,
        'pro_count': progress_count,
    }
    view_name = request.resolver_match.view_name
    if view_name == "tms:staff_dashboard" and user_role == 'User':
        return render(request, 'staff_dashboard.html', context)

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
                if assigned_user.status.strip().lower() == 'vacant':
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
    page_number = request.GET.get('page')
    paginator = Paginator(new_tasks, 10)
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
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

    page_number = request.GET.get('page')
    paginator = Paginator(my_tasks, 10)
    page_obj = paginator.get_page(page_number)

    for tasks in my_tasks:
        if tasks.status == 'Waiting':
            current_time = timezone.now()
            elapsed = current_time - tasks.waiting_time
            if elapsed > timedelta(seconds=180):
                tasks.assigned_to.status = 'vacant'
                tasks.assigned_to.save()

        tasks.save()

    context = {
        'page_obj': page_obj
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
