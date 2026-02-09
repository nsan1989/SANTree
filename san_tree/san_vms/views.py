from django.shortcuts import render
from .models import *
from .forms import *
from django.core.exceptions import PermissionDenied

# Admin Dashboard.
def AdminDashboardView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        pass
    except Exception as e:
        context['error'] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_admin_dashboard" and current_user_role == 'Admin':
        return render(request, 'vms_admin_dashboard.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")


# Staff Dashboard.
def StaffDashboardView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        all_bookings = Booking.objects.filter(booked_by=current_user).order_by('-created_at')
    except Exception as e:
        context['error'] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_staff_dashboard" and current_user_role == 'User':
        context['bookings'] = all_bookings
        return render(request, 'vms_staff_dashboard.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# Cap request view.
def CabRequestView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        if request.method == 'POST':
            form = BookingForm(request.POST)
            if form.is_valid():
                booking = form.save(commit=False)
                booking.booked_by = current_user
                booking.save()
                context['success'] = "Cab request submitted successfully!"
        else:
            form = BookingForm()
    except Exception as e:
        context['error'] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_cab_request" and current_user_role == 'User':
        context['form'] = form
        return render(request, 'vms_booking_request.html', context)

# All trips view.
def AllTripsView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        all_requests = Booking.objects.filter(booked_by=current_user).order_by('-created_at')
    except Exception as e:
        context['error'] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_all_trips" and current_user_role == 'User':
        context['all_requests'] = all_requests
        return render(request, 'vms_all_trips.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# upcoming trips view.
def UpcomingTripsView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        upcoming = Booking.objects.filter(booked_by=current_user, status=BookingStatus.CONFIRMED).order_by('-created_at')
        context['upcoming'] = upcoming
    except Exception as e:
        context['error'] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_upcoming_trips" and current_user_role == 'User':
        return render(request, 'vms_upcoming_trips.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")
