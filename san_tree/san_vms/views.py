from django.shortcuts import render, redirect, get_object_or_404
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

# All bookings view for admin.
def AdminCabRequestsView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        all_requests = Booking.objects.filter(assigned_to=current_user).order_by('-created_at')
    except Exception as e:
        context['error'] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_admin_cab_requests" and current_user_role == 'Admin':
        context['all_requests'] = all_requests
        return render(request, 'vms_admin_requests.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# All trips view for admin.
def AdminTripsView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        all_trips = Booking.objects.filter(status=BookingStatus.COMPLETED).order_by('-created_at')
    except Exception as e:
        context['error'] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_admin_trips" and current_user_role == 'Admin':
        context['all_trips'] = all_trips
        return render(request, 'vms_admin_trips.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# Admin update booking status view.
def AdminUpdateBookingStatusView(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = request.POST.get("status")
        booking.save()
    return redirect('vms:vms_admin_cab_requests')

# Staff Dashboard.
def StaffDashboardView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        all_bookings = Booking.objects.filter(booked_by=current_user)
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

    if current_user_role != 'User':
        raise PermissionDenied("Unauthorized access")

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)

            dept_admin = CustomUsers.objects.filter(
                role='Admin',
                department__name__iexact='Transport'
            )

            booking.booked_by = current_user
            booking.assigned_to = dept_admin.first() if dept_admin.exists() else None
            booking.save()

            return redirect('vms:vms_cab_request')  
    else:
        form = BookingForm()

    return render(request, 'vms_booking_request.html', {'form': form})

# All trips view.
def AllTripsView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        all_requests = Booking.objects.filter(booked_by=current_user, status=BookingStatus.COMPLETED).order_by('-created_at')
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
