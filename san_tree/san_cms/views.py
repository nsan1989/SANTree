from django.shortcuts import render, redirect, get_object_or_404
from .forms import ComplaintForm, ReassignedForm, RemarksForm, ReassignedDepartmentForm
from accounts.models import CustomUsers
from .models import Complaint, ComplaintHistory, ComplaintType, ComplaintRemarks, ReassignedComplaint
from accounts.models import Departments
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from openpyxl import Workbook
from django.http import HttpResponse
from accounts.models import CustomUsers
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from threading import Lock
plot_lock = Lock()
from django.utils import timezone
from datetime import timedelta
import datetime

# Admin Complaint Dashboard view.
def AdminComplaintDashboard(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    dept_users = CustomUsers.objects.filter(department = user.department).exclude(role='Admin')
    vacant_users = dept_users.filter(status = 'vacant')
    engaged_users = dept_users.filter(status = 'engaged')
    all_user = dept_users.count()
    complaints = Complaint.objects.filter(
        Q(department = user.department) |
        (Q(assigned_to=user)|Q(created_by=user))
        ).all().count()
    context = {
        'current_user': user,
        'all_users': all_user,
        'engage_user': engaged_users,
        'vacant_user': vacant_users,
        'total_complaint': complaints,
    }
    view_name = request.resolver_match.view_name
    if view_name == "cms:admin_dashboard" and user_role == 'Admin':
        return render(request, 'complaint_dashboard.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Admin Complaints Pie Chart.
def complaint_status_pie_chart(request):
    user = request.user
    dept_comp = Complaint.objects.filter(department = user.department).all()
    open_comp = dept_comp.filter(status = 'Open').count()
    pro_comp = dept_comp.filter(status = 'In Progress').count()
    close_comp = dept_comp.filter(status = 'Resolved').count()
    if open_comp + pro_comp + close_comp == 0:
        labels = ['No Data']
        sizes = [1]
        colors = ['#d3d3d3']
    else:
        raw_data = [
            ('Open', open_comp, '#eb0707'),
            ('Progress', pro_comp, '#ebd807'),
            ('Resolved', close_comp, '#4feb07')
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

# Users Pie Chart.
def user_status_pie_chart(request):
    user = request.user
    dept_users = CustomUsers.objects.filter(department=user.department).exclude(role='Admin')
    vac_users = dept_users.filter(status='vacant').count()
    eng_users = dept_users.filter(status='engaged').count()

    if vac_users + eng_users == 0:
        labels = ['No Data']
        sizes = [1]
        colors = ['#d3d3d3']  
    else:
        raw_data = [
            ('Vacant', vac_users, '#4feb07'),
            ('Engaged', eng_users, '#eb0707'),
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

# User Complaint Dashboard View.
def UserComplaintDashboard(request):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found")
    create_comp = Complaint.objects.filter(created_by = user).all()
    assign_comp = Complaint.objects.filter(assigned_to = user).all()
    create_count = create_comp.count()
    assign_count = assign_comp.count()
    context = {
        'current_user': user,
        'raised': create_count,
        'assigned': assign_count,
    }
    view_name = request.resolver_match.view_name
    if view_name == "cms:staff_dashboard" and user_role == 'User':
        return render(request, 'staff_complaints_dashboard.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# user Complaints Pie Chart.
def raise_complaint_pie_chart(request):
    user = request.user
    create_comp = Complaint.objects.filter(created_by = user).all()

    create_open = create_comp.filter(status = 'Open').all().count()
    create_pro = create_comp.filter(status = 'In Progress').all().count()
    create_close = create_comp.filter(status = 'Resolved').all().count()
    create_halt = create_comp.filter(status = 'Halt').all().count()
    if create_open + create_pro + create_close + create_halt == 0:
        labels = ['No Data']
        sizes = [1]
        colors = ['#f2f2f2']
    else:
        raw_data = [
            ('Open', create_open, '#0731eb'),
            ('Progress', create_pro, '#ebd807'),
            ('Resolved', create_close, '#4feb07'),
            ('Halt', create_halt, "#eb0707")
            ]
    
        filtered_data = [(label, size, color) for label, size, color in raw_data if size > 0]

        labels, sizes, colors = zip(*filtered_data)

    buffer = io.BytesIO()

    with plot_lock:
        bg_color = (1.0, 1.0, 1.0, 0.2)
        fig, ax = plt.subplots(figsize=(4, 2), facecolor=bg_color) 
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, textprops={'color': 'black'})
        ax.axis('equal')
        plt.savefig(buffer, format='png', facecolor=fig.get_facecolor())
        plt.close(fig)
    
    buffer.seek(0)
    return HttpResponse(buffer.read(), content_type='image/png')

# User Assign Complaint Chart.
def assign_complaint_pie_chart(request):
    user = request.user
    assign_comp = Complaint.objects.filter(assigned_to = user).all()
    
    assign_open = assign_comp.filter(status = 'Open').all().count()
    assign_pro = assign_comp.filter(status = 'In Progress').all().count()
    assign_close = assign_comp.filter(status = 'Resolved').all().count()
    if assign_open + assign_pro + assign_close == 0:
        labels = ['No Data']
        sizes = [1]
        colors = ['#f2f2f2']
    else:
        raw_data = [
            ('Open', assign_open, '#eb0707'),
            ('Progress', assign_pro, '#ebd807'),
            ('Resolved', assign_close, '#4feb07')
            ]
    
        filtered_data = [(label, size, color) for label, size, color in raw_data if size > 0]
        labels, sizes, colors = zip(*filtered_data)

    buffer = io.BytesIO()

    with plot_lock:
        bg_color = (1.0, 1.0, 1.0, 0.2)
        fig, ax = plt.subplots(figsize=(4, 2), facecolor=bg_color) 
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, textprops={'color': 'black'})
        ax.axis('equal')
        plt.savefig(buffer, format='png', facecolor=fig.get_facecolor())
        plt.close(fig)
    
    buffer.seek(0)
    return HttpResponse(buffer.read(), content_type='image/png')

# views.py
def load_complaint_types(request):
    department_id = request.GET.get('department')
    complaint_types = ComplaintType.objects.filter(department_id=department_id).order_by('name')
    return JsonResponse(list(complaint_types.values('id', 'name')), safe=False)

# Complaints View.
def ComplaintView(request):
    user = request.user
    
    if request.method == 'POST':
        form = ComplaintForm(request.POST or None, request.FILES, user=request.user)

        if form.is_valid():
            new_complaint = form.save(commit=False)
            new_complaint.created_by = request.user
            department = form.cleaned_data.get('department')
            complaint_type = form.cleaned_data.get('complaint_type')
            if not complaint_type:
                types = ComplaintType.objects.filter(department=department)
                non_other_types = types.exclude(name__iexact='Others')
                if non_other_types.count() == 1:
                    form.instance.complaint_type = types.first()
                elif non_other_types.count() > 1:
                    form.add_error('complaint_type', 'Please select a complaint type.')
                    return render(request, 'complaints.html', {'form': form})
                else:
                    form.add_error('complaint_type', 'No valid complaint types found.')
                    return render(request, 'complaints.html', {'form': form})
            
            # check for redundant complaint.
            existing = Complaint.objects.filter(
                created_by=request.user,
                department=department,
                complaint_type=complaint_type,
                location=new_complaint.location,
                priority=new_complaint.priority,
                description__iexact=new_complaint.description.strip()
            )
            if existing.exists():
                form.add_error(None, "A similar complaint already exists.")
                return render(request, 'complaints.html', {'form': form})
            
            if user.role == 'User':
                assigned_user = CustomUsers.objects.filter(department=user.department, role='Admin').first()
                if assigned_user:
                    new_complaint.assigned_to = assigned_user
                    new_complaint.status = 'Waiting'
                    assigned_user.save()
                new_complaint.save()
            
            if  user.role == 'Admin':
                assigned_user = CustomUsers.objects.filter(department=department, role='Admin').first()
                if assigned_user:
                    new_complaint.assigned_to = assigned_user
                    new_complaint.status = 'Open'
                    assigned_user.save()
                new_complaint.save()

            ComplaintHistory.objects.create(
                complaint=new_complaint,
                status_changed_to = new_complaint.status,
                changed_by = new_complaint.created_by,
            )

            if user.role == 'User':
                return redirect('cms:staff_complaints_history')
            elif user.role == 'Admin':
                return redirect('cms:incharge_complaints_history')
    else:
        form = ComplaintForm(user=request.user)

    context = {
        'form': form
    }

    return render(request, 'complaints.html', context)

# All Complaints View
def AllComplaintsView(request):
    user = request.user
    path = request.path
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found.")
    complaints = ComplaintHistory.objects.filter(complaint__created_by = user).order_by('complaint__created_at')
    page_number = request.GET.get('page')
    paginator = Paginator(complaints, 10)  
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    if path.startswith('/cms/staff/raised_complaints/') and user_role == 'User':
        return render(request, 'all_complaints.html', context)
    if path.startswith('/cms/incharge/raised_complaints/') and user_role == 'Admin':
        return render(request, 'all_complaints.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Review Complaints View
def ReviewComplaints(request):
    user = request.user
    path = request.path
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found.")
    complaints = ComplaintHistory.objects.filter(
        Q(complaint__created_by__department=user.department) &
        (Q(complaint__status='Waiting') |
        Q(complaint__status='Rejected') |
        Q(complaint__status='Halt') |
        Q(complaint__status='Open')
        )
        ).order_by('complaint__created_at')
    page_number = request.GET.get('page')
    paginator = Paginator(complaints, 10)  
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    if path.startswith('/cms/incharge/review_complaints/') and user_role == 'Admin':
        return render(request, 'complaint_approval.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Review Complaint Details
def ReviewComplaintDetails(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found.")
    complaint = get_object_or_404(ComplaintHistory, complaint_id=id)
    remark = ComplaintRemarks.objects.filter(complaint_id=id)

    context = {
        'complaint': complaint,
        'remarks': remark
    }
    view_name = request.resolver_match.view_name
    if view_name == 'cms:review_complaint_details' and user_role == 'Admin':
        return render(request, 'review_complaint_details.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Review Complaint Update View
def ReviewComplaintUpdateView(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found.")
    complaint = get_object_or_404(ComplaintHistory, id=id)

    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status == 'Open':
            complaint.changed_by = request.user
            complaint.status_changed_to = new_status
            complaint.save()

            assigned_user = CustomUsers.objects.filter(department=complaint.complaint.department, role='Admin').first()
            complaint.complaint.assigned_to = assigned_user
            complaint.complaint.status = new_status
            complaint.complaint.save()
        elif new_status == "Rejected":
            complaint.changed_by = request.user
            complaint.status_changed_to = new_status
            complaint.save()
            
            complaint.complaint.status = new_status
            complaint.complaint.save()

    view_name = request.resolver_match.view_name
    if view_name == 'cms:review_complaint_update_status' and user_role == 'Admin':
        return redirect('cms:review_complaints')
    raise PermissionDenied("You are not authorized to view this page.")

# Assigned Complaint View.
def AssignedComplaint(request):
    user = request.user
    path = request.path
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found.")
    
    complaints = ComplaintHistory.objects.filter(
        (Q(complaint__assigned_to=user) | 
        Q(complaint__department=user.department)) &
        (Q(complaint__status = 'Open')|
         Q(complaint__status = 'In Progress')|
         Q(complaint__status = 'Resolved')|
         Q(complaint__status = 'Halt') |
         Q(complaint__status = 'Review')
         )
        ).order_by('complaint__created_at')
    
    # Vacant the user if it exceeds the assign duration.
    now = timezone.now()
    reassigned = ReassignedComplaint.objects.all()
    for r in reassigned:
        hours, minutes = map(int, r.duration.split(':'))
        expiry_time = r.timestamp + timedelta(hours=hours, minutes=minutes)

        if now >= expiry_time and r.complaint.status == 'In Progress':
            r.complaint.status = 'Halt'
            r.complaint.save()
            new_user = r.reassigned_to
            if new_user.status != 'vacant':
                new_user.status = 'vacant'
                new_user.save()

    page_number = request.GET.get('page')
    paginator = Paginator(complaints, 10)  
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    if path.startswith('/cms/incharge/assigned_complaint/') and user_role == 'Admin':
        return render(request, 'assigned_complaint.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Assigned Complaint Details View.
def AssignedComplaintDetails(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found.")
    complaint = get_object_or_404(ComplaintHistory, complaint_id=id)
    remark = ComplaintRemarks.objects.filter(complaint_id=id)
    context = {
        'complaint': complaint,
        'remarks': remark
    }
    view_name = request.resolver_match.view_name
    if view_name == 'cms:assigned_complaint_details' and user_role == 'Admin':
        return render(request, 'assigned_complaint_details.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Staff Update Complaint Status View.
def StaffUpdateComplaintStatus(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User Profile not found.")
    complaint = get_object_or_404(ComplaintHistory, id=id)

    if complaint.complaint.assigned_to != request.user:
        return redirect('cms:staff_assigned_tasks')
    
    if complaint.complaint.status in ['Closed', 'Cancelled']:
        messages.warning(request, f"Cannot update status. Complaint is already {complaint.complaint.status}.")
        return redirect('cms:staff_assigned_tasks')
    
    dept_admin = CustomUsers.objects.filter(department=user.department, role='Admin').first()
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status == 'Review':
            complaint.changed_by = request.user
            complaint.complaint.assigned_to = dept_admin
            complaint.status_changed_to = new_status
            complaint.complaint.status = new_status
            complaint.complaint.save()
            complaint.save()

            messages.success(request, "Status updated successfully.")
    view_name = request.resolver_match.view_name
    if view_name == 'cms:staff_update_complaint_status' and user_role == 'User':
        return redirect('cms:staff_assigned_tasks')
    raise PermissionDenied("You are not authorized to view this page.")

# Admin Update Complaint Status View.
def AdminUpdateComplaintStatus(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found.")
    
    complaint = get_object_or_404(ComplaintHistory, id=id)

    if (complaint.complaint.assigned_to != user and complaint.complaint.department != user.department):
        return redirect('cms:assigned_complaint')
    
    if complaint.complaint.status in ['Closed', 'Cancelled']:
        messages.warning(request, f"Cannot update status. Complaint is already {complaint.complaint.status}.")
        return redirect('cms:assigned_complaint')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        print(new_status)
        if new_status == 'Closed' and complaint.status_changed_to == 'Cancelled':
            messages.warning(request, "Cancelled complaint cannot be Closed.")
        else:
            complaint.changed_by = user
            complaint.status_changed_to = new_status
            complaint.complaint.status = new_status
            complaint.complaint.save()
            complaint.save()

            if new_status == 'In Progress':
                complaint.complaint.assigned_to.status = 'engaged'
                complaint.complaint.assigned_to.save()
            elif new_status == 'Resolved':
                complaint.complaint.assigned_to.status = 'vacant'
                complaint.complaint.assigned_to.save()

            complaint.complaint.save()
            complaint.save()

            messages.success(request, "Status updated successfully.")
    view_name = request.resolver_match.view_name
    if view_name == 'cms:admin_update_complaint_status' and user_role == 'Admin':
        return redirect('cms:assigned_complaint')
    raise PermissionDenied("You are not authorized to view this page.")

# Cancel Complaint View.
def CancelComplaint(request, id):
    complaint = get_object_or_404(ComplaintHistory, complaint_id=id)
  
    if request.method == 'POST':
        new_status = request.POST.get('status')

        if complaint.complaint.created_by != request.user:
            if request.user.role == 'User':
                return redirect('cms:staff_complaints_history')
            else:
                return redirect('cms:incharge_complaints_history')
        
        if new_status == 'Cancelled' and complaint.complaint.status == 'Closed':
            messages.warning(request, "Closed complaint cannot be cancelled.")
        else:
            complaint.status_changed_to = new_status
            complaint.save()

            main_complaint = complaint.complaint
            main_complaint.status = new_status
            main_complaint.save()

            messages.success(request, "Status updated successfully.")

    if request.user.role == 'User':
        return redirect('cms:staff_complaints_history')
    else:
        return redirect('cms:incharge_complaints_history')

# Complaint Details View.
def ComplaintDetails(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found.")
    complaint = get_object_or_404(ComplaintHistory, complaint_id=id)
    remark = ComplaintRemarks.objects.filter(complaint_id=id)
    
    context = {
        'complaint': complaint,
        'remarks': remark
    }
    
    view_name = request.resolver_match.view_name
    if view_name == 'cms:staff_complaints_details' and user_role == 'User':
        return render(request, 'complaint_details.html', context)
    if view_name == 'cms:incharge_complaints_details' and user_role == 'Admin':
        return render(request, 'complaint_details.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Complain History View.
def ComplainHistory(request):
    selected_department_id = request.GET.get('department')
    page_number = request.GET.get('page')

    if selected_department_id:
        all_complaints = ComplaintHistory.objects.filter(
            complaint__department_id=selected_department_id
        ).order_by('-complaint__created_at')
    else:
        all_complaints = ComplaintHistory.objects.all().order_by('-complaint__created_at')

    paginator = Paginator(all_complaints, 10)  
    page_obj = paginator.get_page(page_number)

    departments = Departments.objects.all()

    context = {
        'page_obj': page_obj,
        'departments': departments,
        'selected_department': int(selected_department_id) if selected_department_id else None,
    }

    return render(request, 'complaint_history.html', context)

# Reassigned Complaint to User View.
def ReassignedComplaintView(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        form = ReassignedForm(request.POST, request=request)
        if form.is_valid():

            previous_user = complaint.assigned_to
            if previous_user:
                previous_user.status = 'vacant'
                previous_user.save()

            new_user = form.cleaned_data['reassigned_to']
            new_user.status = 'engaged'
            new_user.save()

            reassign_complaint = form.save(commit=False)
            reassign_complaint.complaint = complaint
            reassign_complaint.reassigned_to = new_user
            reassign_complaint.save()

            complaint.assigned_to = new_user
            complaint.save()

            return redirect('cms:assigned_complaint')
    else:
        form = ReassignedForm(request=request)

    context = {
        'form': form,
        'complaint': complaint
    }
    return render(request, 'reassigned_complaint.html', context)

# Reassigned Department View
def ReassignDepartmentView(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        form = ReassignedDepartmentForm(request.POST, user=request.user)
        if form.is_valid():

            department = form.cleaned_data['reassign_to']
            assign_user = CustomUsers.objects.filter(department=department, role='Admin').first()
            if assign_user:
                complaint.assigned_to = assign_user
                complaint.department = department
                complaint.save()
                return redirect('cms:assigned_complaint')
    else:
        form = ReassignedDepartmentForm(user=request.user)

    context = {
        'form': form,
        'complaint': complaint
    }
    return render(request, 'department_assigned.html', context)

# Assigned Tasks View.
def AssignedTasks(request):
    user = request.user
    path = request.path
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found.")
    assign_complaints = ComplaintHistory.objects.filter(
        Q(complaint__assigned_to = user) | 
        Q(Q(complaint__status = 'Review') | Q(complaint__status = 'Resolved'))
        ).order_by('complaint__created_at')

    page_number = request.GET.get('page')
    paginator = Paginator(assign_complaints, 10)  
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    if path.startswith('/cms/staff/assigned_tasks/') and user_role == 'User':
        return render(request, 'assigned_tasks.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Assigned Task Details
def AssignedTaskDetails(request, id):
    user = request.user
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found.")
    complaint = get_object_or_404(ComplaintHistory, complaint_id=id)
    remark = ComplaintRemarks.objects.filter(complaint_id=id)
    
    context = {
        'task': complaint,
        'remarks': remark
    }
    view_name = request.resolver_match.view_name
    if view_name == 'cms:staff_assigned_tasks_details' and user_role == 'User':
        return render(request, 'assigned_task_details.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Complaint Remark View.
def RemarksComplaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        form = RemarksForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            remark = form.save(commit=False)
            remark.complaint = complaint
            remark.remarks = form.cleaned_data.get('remarks')
            remark.created_by = request.user
            remark.save()

            if request.user.designation == 'Staff':
                return redirect('cms:staff_assigned_tasks')
            else:
                return redirect('cms:assigned_complaint')

    else:
        form = RemarksForm(request=request)
    context = {
        'form': form,
        'complaint': complaint
    }
    return render(request, 'remarks.html', context)

# Complaint Profile View.
def ComplaintProfile(request):
    user = request.user
    try:
        user_role = user.role
    except:
        PermissionDenied("User profile not found.")
    context = {
        'profile': user,
    }
    view_name = request.resolver_match.view_name
    if view_name == "cms:staff_profile" and user_role == 'User':
        return render(request, 'complaint_profile.html', context)
    if view_name == "cms:admin_profile" and user_role == 'Admin':
        return render(request, 'complaint_profile.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Excel Export.
def TasksExport(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    tasks = ComplaintHistory.objects.none()
    if start_date_str and end_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d') + datetime.timedelta(days=1)

            tasks = ComplaintHistory.objects.select_related('complaint').filter(
                complaint__created_at__range=(start_date, end_date)
            )
        except ValueError:
            pass 
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="tasks.xlsx"'
    wb = Workbook()
    ws = wb.active
    ws.append(['Complaint Number', 'Complaint', 'Priority', 'Created By', 'Location', 'Concern Department', 'Created At', 'Status', 'Completed At'])
    for task in tasks:
        complaint = task.complaint
        ws.append([
            str(complaint.complaint_number),
            str(complaint.complaint_type), 
            complaint.priority,
            str(complaint.created_by),
            str(complaint.location),
            str(complaint.department), 
            complaint.created_at.strftime('%Y-%m-%d %H:%M'),
            complaint.status, 
            complaint.completed_at.strftime('%Y-%m-%d %H:%M'),
            ])
    wb.save(response)
    return response
