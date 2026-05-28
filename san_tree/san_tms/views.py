from datetime import date, timedelta

import matplotlib
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import CustomUsers

from .forms import *
from .models import (
    TaskHandover,
    Tasks,
    TasksRemarks,
    TasksTypes,
    TaskChecklist,
    TaskChecklistStatus,
)

matplotlib.use("Agg")
import io
from threading import Lock

import matplotlib.pyplot as plt

plot_lock = Lock()
import calendar
import json
from datetime import datetime

from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils.safestring import mark_safe
from django.utils.timezone import now


# Tasks Pie Chart
def TasksPieChart(request):
    user = request.user
    # --- date filter ---
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    tasks = Tasks.objects.filter(assigned_to=user, start_date__lte=timezone.localdate())

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            tasks = tasks.filter(start_date__range=[start.date(), end.date()])
        except ValueError:
            pass

    # --- counts by status ---
    open_count = tasks.filter(status="Open").count()
    progress_count = tasks.filter(status="In Progress").count()
    waiting_count = tasks.filter(status="Waiting").count()
    review_count = tasks.filter(status="Review").count()
    completed_count = tasks.filter(status="Completed").count()

    if (
        open_count + progress_count + waiting_count + review_count + completed_count
        == 0
    ):
        labels = ["No Data"]
        sizes = [1]
        colors = ["#d3d3d3"]
    else:
        raw_data = [
            ("Open", open_count, "#eb0707"),
            ("In Progress", progress_count, "#ebd807"),
            ("Waiting", waiting_count, "#07bdeb"),
            ("Review", review_count, "#ff9900"),
            ("Completed", completed_count, "#4feb07"),
        ]
        filtered = [(l, s, c) for l, s, c in raw_data if s > 0]
        labels, sizes, colors = zip(*filtered)

    # --- draw pie chart ---
    buffer = io.BytesIO()
    fig, ax = plt.subplots(figsize=(4, 2), facecolor=(0, 0, 0, 0.4))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
        textprops={"color": "white"},
    )
    ax.axis("equal")

    plt.savefig(buffer, format="png", facecolor=fig.get_facecolor(), transparent=True)
    plt.close(fig)
    buffer.seek(0)

    return HttpResponse(buffer.read(), content_type="image/png")


# Admin Dashboard view.
def TaskDashboard(request):
    user = request.user
    try:
        user_role = user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")

    events = []
    if request.method == "POST":
        form = TasksForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.created_by = request.user
            department = form.cleaned_data.get("department")
            task_type = form.cleaned_data.get("tasks_types")
            assigned_user = form.cleaned_data.get("assigned_to")
            if not task_type:
                types = TasksTypes.objects.filter(department=department)
                if types.count() == 1:
                    form.instance.task_type = types.first()
                elif types.count() > 1 and types == "others":
                    form.add_error("task_type", "Please select a task type.")
            if assigned_user:
                if assigned_user.status.strip().lower() == "vacant":
                    new_task.assigned_to = assigned_user
                    assigned_user.save()
                else:
                    form.add_error(
                        "assigned_to", f"{assigned_user.username} is not vacant."
                    )

            if not form.errors:
                new_task.save()

            messages.success(request, "Task created successfully.")
            return redirect("tms:tasks")
    else:
        form = TasksForm(user=request.user)

    total_users = (
        CustomUsers.objects.filter(Q(department=user.department) & ~Q(id=user.id))
        .all()
        .count()
    )

    incharge_tasks = Tasks.objects.filter(created_by=user).all()
    for tasks in incharge_tasks:
        events.append(
            {
                "title": f"{tasks.tasks_types} ({tasks.task_frequency})",
                "start": tasks.start_date.strftime("%Y-%m-%d"),
                "url": reverse("tms:admin_tasks_details", args=[tasks.id]),
                "color": "#6c757d",
            }
        )
        if tasks.next_date:
            events.append(
                {
                    "title": f"{tasks.tasks_types} - Next ({tasks.task_frequency})",
                    "start": tasks.next_date.strftime("%Y-%m-%d"),
                    "url": reverse("tms:admin_tasks_details", args=[tasks.id]),
                    "color": "#f39c12",
                }
            )
    total_tasks = incharge_tasks.count()
    complete_tasks = (
        Tasks.objects.filter(Q(department=user.department) & Q(status="Completed"))
        .all()
        .count()
    )

    context = {
        "current_user": user,
        "date": date.today(),
        "all_tasks": incharge_tasks,
        "calendar_events": json.dumps(events, cls=DjangoJSONEncoder),
        "created_tasks": total_tasks,
        "comp_tasks": complete_tasks,
        "tot_users": total_users,
        "form": form,
    }

    view_name = request.resolver_match.view_name
    if view_name == "tms:tms_admin_dashboard" and user_role == "Admin":
        return render(request, "tasks_dashboard.html", context)
    raise PermissionDenied("You are not authorized to view this page.")


# Staff Dashboard View.
def StaffDashboard(request):
    user = request.user
    try:
        user_role = user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")
    staff_tasks = Tasks.objects.filter(assigned_to=user).order_by("start_date")[:5]
    events = []
    for tasks in staff_tasks:
        # Determine event color based on status
        if tasks.status == "Completed":
            color = "#006600"
        elif tasks.status == "Overdue":
            color = "#800000"
        elif tasks.status == "Pending":
            color = "#ff6600"
        else:
            color = "gray"
        events.append(
            {
                "title": str(tasks.tasks_types),
                "start": tasks.start_date.strftime("%Y-%m-%d"),
                "url": reverse("tms:staff_tasks_details", args=[tasks.id]),
                "color": color,
            }
        )
        if tasks.next_date:
            events.append(
                {
                    "title": f"{tasks.tasks_types} - Next ({tasks.task_frequency})",
                    "start": tasks.next_date.strftime("%Y-%m-%d"),
                    "url": reverse("tms:staff_tasks_details", args=[tasks.id]),
                    "color": color,
                }
            )
    context = {
        "current_user": user,
        "date": date.today(),
        "all_tasks": staff_tasks,
        "calendar_events": json.dumps(events, cls=DjangoJSONEncoder),
    }
    view_name = request.resolver_match.view_name
    if view_name == "tms:tms_staff_dashboard" and user_role == "User":
        return render(request, "staff_dashboard.html", context)
    raise PermissionDenied("You are not authorized to view this page.")


# Load Task Types.
def load_tasks_types(request):
    department_id = request.GET.get("department")
    tasks_types = TasksTypes.objects.filter(department_id=department_id).order_by(
        "name"
    )
    return JsonResponse(list(tasks_types.values("id", "name")), safe=False)


# Load Task Staff.
def load_tasks_staffs(request):
    department_id = request.GET.get("department")
    staff = CustomUsers.objects.filter(department_id=department_id, role="User").values(
        "id", "username"
    )
    return JsonResponse(list(staff), safe=False)


# All Tasks View.
def AllTasks(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    new_tasks = Tasks.objects.filter(Q(created_by=user))
    page_number = request.GET.get("page")
    paginator = Paginator(new_tasks, 10)
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj, "today": timezone.localdate()}
    view_name = request.resolver_match.view_name
    if view_name == "tms:tasks" and user_role == "Admin":
        return render(request, "all_tasks.html", context)
    raise PermissionDenied("You are not authorized to view this page.")


# My Tasks View
def MyTasks(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    my_tasks = Tasks.objects.filter(assigned_to=user).order_by("start_date")

    page_number = request.GET.get("page")
    paginator = Paginator(my_tasks, 10)
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}
    view_name = request.resolver_match.view_name
    if view_name == "tms:my_tasks" and user_role == "User":
        return render(request, "my_tasks.html", context)
    raise PermissionDenied("You are not authorized to view this page.")


# Tasks Details.
def TasksDetails(request, id):
    tasks = get_object_or_404(Tasks, id=id)
    user = request.user
    try:
        user_role = user.role
    except:
        PermissionDenied("User profile not found.")
    task_remark = TasksRemarks.objects.filter(tasks_id=id).order_by("-created_at")
    handover_history = TaskHandover.objects.filter(tasks_id=id).order_by("-created_at")
    handover_form = TaskHandoverForm(task=tasks)
    context = {
        "tasks": tasks,
        "remark": task_remark,
        "handover_history": handover_history,
        "handover_form": handover_form,
    }
    view_name = request.resolver_match.view_name
    if view_name == "tms:staff_tasks_details" and user_role == "User":
        return render(request, "tasks_details.html", context)
    raise PermissionDenied("You are not authorized to view this page.")


# Tasks Details.
def AllTasksDetails(request, id):
    tasks = get_object_or_404(Tasks, id=id)
    user = request.user
    try:
        user_role = user.role
    except:
        PermissionDenied("User profile not found.")
    task_remark = TasksRemarks.objects.filter(tasks_id=id).order_by("-created_at")
    handover_history = TaskHandover.objects.filter(tasks_id=id).order_by("-created_at")
    context = {
        "tasks": tasks,
        "remark": task_remark,
        "handover_history": handover_history,
    }
    view_name = request.resolver_match.view_name
    if view_name == "tms:admin_tasks_details" and user_role == "Admin":
        return render(request, "all_tasks_details.html", context)
    raise PermissionDenied("You are not authorized to view this page.")


# Task Handover.
def TaskHandoverUpdate(request, id):
    user = request.user
    try:
        user_role = user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")

    if user_role != "User":
        raise PermissionDenied("You are not authorized to handover tasks.")

    tasks = get_object_or_404(Tasks, id=id)
    if tasks.assigned_to != user:
        raise PermissionDenied("You can only handover tasks assigned to you.")

    if request.method == "POST":
        form = TaskHandoverForm(request.POST, task=tasks)
        if form.is_valid():
            new_user = form.cleaned_data["to_user"]
            reason = form.cleaned_data["reason"]
            old_user = tasks.assigned_to

            tasks.assigned_to = new_user
            tasks.save(update_fields=["assigned_to"])

            if old_user:
                has_active_tasks = (
                    Tasks.objects.filter(assigned_to=old_user)
                    .exclude(status__in=["Completed", "Cancelled"])
                    .exists()
                )
                old_user.status = "Engaged" if has_active_tasks else "Vacant"
                old_user.save(update_fields=["status"])

            new_user.status = "Engaged"
            new_user.save(update_fields=["status"])

            TaskHandover.objects.create(
                tasks=tasks,
                from_user=old_user,
                to_user=new_user,
                reason=reason,
                created_by=user,
            )

            messages.success(request, "Task handed over successfully.")
        else:
            messages.warning(request, "Handover failed. Please check the details.")
    else:
        form = TaskHandoverForm()

    context = {"form": form, "task": tasks}
    return render(request, "task_handover.html", context)


# Update Tasks Status.
def UpdateStatus(request, id):

    user = request.user
    try:
        user_role = user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")

    tasks = get_object_or_404(Tasks, id=id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        remarks = request.POST.get("remarks", "").strip()

        if tasks.status == "Completed":
            messages.warning(
                request, f"Cannot update status. Complaint is already {tasks.status}."
            )
            return redirect("tms:my_tasks")

        allowed_transitions = {
            "Waiting": {"Acknowledged", "Cancelled"},
            "Acknowledged": {"In Progress", "Postponed"},
            "In Progress": {"Completed", "Postponed"},
            "Postponed": {"In Progress", "Cancelled"},
        }

        valid_next_status = allowed_transitions.get(tasks.status, set())
        if new_status not in valid_next_status:
            messages.warning(
                request,
                f"Invalid status transition from {tasks.status} to {new_status}.",
            )
            if user.role == "User":
                return redirect("tms:my_tasks")
            return redirect("tms:tasks")

        if new_status == "In Progress":
            user.status = "Engaged"
            user.save(update_fields=["status"])

        if new_status == "Postponed" and not remarks:
            messages.warning(request, "Postponed status requires a reason.")
            if user.role == "User":
                return redirect("tms:my_tasks")
            return redirect("tms:tasks")

        if new_status == "Postponed":
            TasksRemarks.objects.create(
                tasks=tasks,
                remarks=remarks,
                created_by=request.user,
            )
            user.status = "Vacant"

        # Ensure checklist exists for this task (initialize if missing)
        checklist_templates = TaskChecklist.objects.filter(task_type=tasks.tasks_types)

        existing_ids = set(
            TaskChecklistStatus.objects.filter(task=tasks).values_list(
                "checklist_id", flat=True
            )
        )

        to_create = [
            TaskChecklistStatus(task=tasks, checklist=tpl)
            for tpl in checklist_templates
            if tpl.id not in existing_ids
        ]

        if to_create:
            TaskChecklistStatus.objects.bulk_create(to_create)

        checklist_qs = TaskChecklistStatus.objects.filter(task=tasks)

        if new_status == "Completed":
            if not checklist_qs.exists():
                messages.error(request, "⚠️ Checklist not initialized for this task.")
                return redirect("tms:my_tasks")

            if checklist_qs.filter(is_completed=False).exists():
                messages.error(
                    request,
                    "⚠️ Please complete all checklist items before marking this task as Completed.",
                )
                return redirect("tms:my_tasks")

            tasks.completed_at = timezone.now()
            anchor_date = tasks.completed_at.date()

            next_start_date = None
            if tasks.task_frequency in {"Daily", "Weekly", "Monthly"}:

                if tasks.task_frequency == "Daily":
                    next_start_date = anchor_date + timedelta(days=1)

                elif tasks.task_frequency == "Weekly":
                    next_start_date = anchor_date + timedelta(days=7)

                elif tasks.task_frequency == "Monthly":
                    next_start_date = anchor_date + timedelta(days=30)

            # For recurring tasks, auto-create the next cycle and keep assignment.
            if next_start_date:
                exist_next = Tasks.objects.filter(
                    tasks_types=tasks.tasks_types,
                    start_date=next_start_date,
                    assigned_to=tasks.assigned_to,
                ).exists()
                if not exist_next:
                    Tasks.objects.create(
                        tasks_types=tasks.tasks_types,
                        task_frequency=tasks.task_frequency,
                        location=tasks.location,
                        status="Waiting",
                        department=tasks.department,
                        created_by=tasks.created_by,
                        assigned_to=tasks.assigned_to,
                        start_date=next_start_date,
                        attachment=tasks.attachment,
                    )

            tasks.status = "Completed"
            tasks.save(
                update_fields=[
                    "status",
                ]
            )

            current_assignee = tasks.assigned_to
            current_assignee.status = "vacant"
            current_assignee.save(update_fields=["status"])

            messages.success(request, "Task completed successfully.")
            return redirect("tms:my_tasks")

        tasks.status = new_status
        tasks.completed_at = None

        if new_status == "Waiting":
            tasks.waiting_time = timezone.now()

        tasks.save(
            update_fields=[
                "status",
            ]
        )

        if user.role == "User":
            return redirect("tms:my_tasks")
        else:
            return redirect("tms:tasks")

    view_name = request.resolver_match.view_name
    if view_name == "tms:staff_update_task_status" and user_role == "User":
        return redirect("tms:my_tasks")
    if view_name == "tms:admin_update_task_status" and user_role == "Admin":
        return redirect("tms:tasks")
    raise PermissionDenied("You are not authorized to view this page.")


# Task Remark View.
def TaskRemark(request, task_id):
    task = get_object_or_404(Tasks, id=task_id)
    if request.method == "POST":
        form = RemarkForm(request.POST, request.FILES)
        if form.is_valid():
            remark = form.save(commit=False)
            remark.tasks = task
            remark.remarks = form.cleaned_data.get("remarks")
            remark.created_by = request.user
            remark.save()

            if request.user.designation == "Staff":
                return redirect("tms:my_tasks")
            else:
                return redirect("tms:tasks")

    else:
        form = RemarkForm()
    context = {"form": form, "task": task}
    return render(request, "remark.html", context)


# calender
def GenerateCalendar(year, month, week, day):
    cal = calendar.HTMLCalendar(calendar.MONDAY)
    return mark_safe(cal.formatmonth(year, month, week, day))


# checklist view
def TaskChecklists(request, task_id):
    user = request.user
    try:
        user_role = user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")
    task = get_object_or_404(Tasks, id=task_id)
    related_checklist = TaskChecklist.objects.filter(task_type=task.tasks_types)

    for items in related_checklist:
        TaskChecklistStatus.objects.get_or_create(task=task, checklist=items)

    if request.method == "POST":
        selected = request.POST.getlist("checklist")

        checklist_status = TaskChecklistStatus.objects.filter(task=task)

        for item in checklist_status:
            if str(item.id) in selected:
                item.is_completed = True
                item.completed_by = request.user
                item.completed_date = timezone.now()
            else:
                item.is_completed = False
                item.completed_by = None
                item.completed_date = None

            item.save()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True})

        return redirect("tms:task_checklist", task_id=task.id)

    checklist_status = TaskChecklistStatus.objects.filter(task=task)

    context = {"task": task, "checklist_status": checklist_status}

    view_name = request.resolver_match.view_name
    if view_name == "tms:task_checklist" and user_role == "User":
        return render(request, "tasks_checklist.html", context)
    raise PermissionDenied("You are not authorized to view this page.")


# add task types
def AddTaskTypes(request):
    user = request.user
    if request.method == "POST":
        form = AddTaskType(request.POST, user=request.user)
        if form.is_valid():
            task_type = form.save(commit=False)
            exists = TasksTypes.objects.filter(
                name__iexact=task_type.name,
                department__name__iexact=user.department,
            ).exists()
            if exists:
                messages.error(request, "Task type already exist!")
            else:
                task_type.save()
                messages.success(request, "Task type added successfully!")
                return redirect("tms:tms_admin_dashboard")
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = AddTaskType(user=request.user)

    context = {"form": form}
    return render(request, "settings/add_task_types.html", context)


# add task checklist
def AddTaskChecklist(request):
    user = request.user
    if request.method == "POST":
        form = AddTaskChecklistForm(request.POST, user=request.user)
        if form.is_valid():
            checklist = form.save(commit=False)
            exists = TaskChecklist.objects.filter(
                name__iexact=checklist.name,
                task_type__name__iexact=checklist.task_type.name,
            ).exists()
            if exists:
                messages.error(request, "Task type already exist!")
            else:
                checklist.save()
                messages.success(request, "Task type added successfully!")
                return redirect("tms:tms_admin_dashboard")
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = AddTaskChecklistForm(user=request.user)

    context = {"form": form}
    return render(request, "settings/add_task_checklist.html", context)
