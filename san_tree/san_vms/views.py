from django.shortcuts import render, redirect, get_object_or_404
from .services.dispatch import HandleCriticalBooking
from .models import *
from .forms import *
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction

# Admin Dashboard.
def AdminDashboardView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        all_bookings = Booking.objects.filter(assigned_to=current_user).order_by('-created_at')
        page_number = request.GET.get('page')
        paginator = Paginator(all_bookings, 10)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
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
    vehicles = Vehicle.objects.all()
    driver = Driver.objects.all()
    try:
        all_requests = Booking.objects.filter(assigned_to=current_user).order_by('-created_at')
        page_number = request.GET.get('page')
        paginator = Paginator(all_requests, 10)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['vehicles'] = vehicles
        context['drivers'] = driver
    except Exception as e:
        context['error'] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_admin_cab_requests" and current_user_role == 'Admin':
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
@transaction.atomic
def AdminUpdateBookingStatusView(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)
        old_driver = booking.driver
        old_vehicle = booking.vehicle

        status = request.POST.get("status")
        if status:
            booking.status = status

        vehicle_id = request.POST.get("vehicle")
        if vehicle_id:
            new_vehicle = Vehicle.objects.get(id=vehicle_id)
            booking.vehicle = new_vehicle
            new_vehicle.status = "BOOKED"
            new_vehicle.save()
        else:
            booking.vehicle = None

        driver_id = request.POST.get("driver")
        if driver_id:
            new_driver = Driver.objects.get(id=driver_id)
            booking.driver = new_driver
            new_driver.user.status = "engaged"
            new_driver.user.save()
        else:
            booking.driver = None

        if booking.priority == "CRITICAL" and booking.vehicle:
            HandleCriticalBooking(booking)
            
        booking.save()

        if old_driver and old_driver != booking.driver:
            old_driver.user.status = "vacant"
            old_driver.user.save()

        if old_vehicle and old_vehicle != booking.vehicle:
            old_vehicle.status = "AVAILABLE"
            old_vehicle.save()

        if booking.status == "CANCELLED":
            if booking.driver:
                booking.driver.user.status = "vacant"
                booking.driver.user.save()
            if booking.vehicle:
                booking.vehicle.status = "AVAILABLE"
                booking.vehicle.save()

            booking.driver = None
            booking.vehicle = None
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
    
    cargos = Cargo.objects.all()

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                booking = form.save(commit=False)

                dept_admin = CustomUsers.objects.filter(
                    role='Admin',
                    department__name__iexact='Transport'
                )

                booking.booked_by = current_user
                booking.assigned_to = dept_admin.first() if dept_admin.exists() else None
                booking.save()

#                if booking.priority == BookingPriority.CRITICAL:
#                    HandleCriticalBooking(booking)

            return redirect('vms:vms_cab_request')  
    else:
        form = BookingForm()

    context = {'form': form, 'cargos': cargos}

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
        all_requests = Booking.objects.filter(booked_by=current_user, status=BookingStatus.COMPLETED).order_by('-created_at')
        page_number = request.GET.get('page')
        paginator = Paginator(all_requests, 10)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
    except Exception as e:
        context['error'] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_all_trips" and current_user_role == 'User':
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
        page_number = request.GET.get('page')
        paginator = Paginator(upcoming, 10)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
    except Exception as e:
        context['error'] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_upcoming_trips" and current_user_role == 'User':
        return render(request, 'vms_upcoming_trips.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# Staff update booking status view.
def StaffUpdateBookingStatusView(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = request.POST.get("status")
        booking.save()
    return redirect('vms:vms_staff_dashboard')

