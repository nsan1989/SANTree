from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
import json
from django.http import JsonResponse
from datetime import timedelta
from django.urls import reverse

from .forms import *
from .models import *
from .services.dispatch import HandleCriticalBooking


# Admin Dashboard.
def AdminDashboardView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        all_bookings = Booking.objects.filter(assigned_to=current_user).order_by(
            "-created_at"
        )
        page_number = request.GET.get("page")
        paginator = Paginator(all_bookings, 10)
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
    except Exception as e:
        context["error"] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_admin_dashboard" and current_user_role == "Admin":
        return render(request, "vms_admin_dashboard.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


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
        all_requests = Booking.objects.filter(assigned_to=current_user).order_by(
            "-created_at"
        )
        page_number = request.GET.get("page")
        paginator = Paginator(all_requests, 10)
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
        context["vehicles"] = vehicles
        context["drivers"] = driver
    except Exception as e:
        context["error"] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_admin_cab_requests" and current_user_role == "Admin":
        return render(request, "vms_admin_requests.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# All trips view for admin.
def AdminTripsView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        all_trips = Booking.objects.exclude(status=BookingStatus.WAITING).order_by(
            "-created_at"
        )
    except Exception as e:
        context["error"] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_admin_trips" and current_user_role == "Admin":
        context["all_trips"] = all_trips
        return render(request, "vms_admin_trips.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


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
            booking.assigned_to = new_driver.user
            new_driver.user.status = "engaged"
            new_driver.user.save()
        else:
            booking.driver = None
            booking.assigned_to = None

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

    return redirect("vms:vms_admin_cab_requests")


# Staff Dashboard.
def StaffDashboardView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        if (
            current_user.department
            and "transport" in current_user.department.name.lower()
        ):
            all_bookings = Booking.objects.filter(assigned_to=current_user).order_by(
                "-created_at"
            )
        else:
            all_bookings = Booking.objects.filter(created_by=current_user).order_by(
                "-created_at"
            )
        context["bookings"] = all_bookings
    except Exception as e:
        context["error"] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_staff_dashboard" and current_user_role == "User":
        return render(request, "vms_staff_dashboard.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# Cap request view.
def CabRequestView(request):
    current_user = request.user

    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")

    if current_user_role not in ["User", "Admin"]:
        raise PermissionDenied("Unauthorized access")

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                booking = form.save(commit=False)

                dept_admin = CustomUsers.objects.filter(
                    role="Admin", department__name__iexact="Transport"
                )

                booking.booked_by = current_user
                booking.assigned_to = (
                    dept_admin.first() if dept_admin.exists() else None
                )
                booking.save()

            #                if booking.priority == BookingPriority.CRITICAL:
            #                    HandleCriticalBooking(booking)

            return redirect("vms:booking_success")
    else:
        form = BookingForm()

    context = {"form": form}

    return render(request, "vms_booking_request.html", context)


# All trips view.
def AllTripsView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        if (
            current_user.department
            and "transport" in current_user.department.name.lower()
        ):
            all_requests = Booking.objects.filter(
                assigned_to=current_user,
                status__in=["ACKNOWLEDGE", "COMPLETED", "IN_PROGRESS", "CANCELLED"],
            ).order_by("-created_at")
        else:
            all_requests = Booking.objects.filter(
                booked_by=current_user,
                status__in=["COMPLETED", "IN_PROGRESS", "CANCELLED"],
            ).order_by("-created_at")
        page_number = request.GET.get("page")
        paginator = Paginator(all_requests, 10)
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
    except Exception as e:
        context["error"] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_all_trips" and current_user_role == "User":
        return render(request, "vms_all_trips.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# Assigned trips view.
def AssignedTripsView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    assigned_trip = Booking.objects.filter(
        assigned_to=current_user, status="CONFIRMED"
    ).order_by("-created_at")
    context = {"assigned": assigned_trip}
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_assigned_trips" and current_user_role == "User":
        return render(request, "vms_assigned_trips.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# Admin upcoming trips.
def AdminUpcomingTripsView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    upcoming = Booking.objects.filter(
        booked_by=current_user,
        status="CONFIRMED",
    ).order_by("-created_at")
    context = {"upcomings": upcoming}
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_admin_upcoming_trips" and current_user_role == "Admin":
        return render(request, "vms_admin_upcoming_trips.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# upcoming trips view.
def UpcomingTripsView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        if (
            current_user.department
            and "transport" in current_user.department.name.lower()
        ):
            upcoming = Booking.objects.filter(
                status__in=[
                    "CONFIRMED",
                ]
            ).order_by("-created_at")
        else:
            upcoming = Booking.objects.filter(
                booked_by=current_user, status__in=["CONFIRMED", "ACKNOWLEDGE"]
            ).order_by("-created_at")
        page_number = request.GET.get("page")
        paginator = Paginator(upcoming, 10)
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
    except Exception as e:
        context["error"] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_upcoming_trips" and current_user_role == "User":
        return render(request, "vms_upcoming_trips.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# Staff update booking status view.
def StaffUpdateBookingStatusView(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = request.POST.get("status")
        booking.save()
    return redirect("vms:vms_staff_dashboard")


# All Vehicles View.
def VehiclesView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        vehicles = Vehicle.objects.all()
        page_number = request.GET.get("page")
        paginator = Paginator(vehicles, 10)
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
    except Exception as e:
        context["error"] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_all_vehicles" and current_user_role == "Admin":
        return render(request, "vms_vehicles.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# Add Staff View.
def AddStaffView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        if request.method == "POST":
            form = DriverForm(request.POST, user=request.user)
            if form.is_valid():
                new_driver = form.save(commit=False)
                new_driver.save()
    except Exception as e:
        context["error"] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_add_staff" and current_user_role == "Admin":
        return render(request, "vms_add_staff.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# All Staff View.
def StaffView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        staff = Driver.objects.all()
        page_number = request.GET.get("page")
        paginator = Paginator(staff, 10)
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
    except Exception as e:
        context["error"] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:vms_all_staffs" and current_user_role == "Admin":
        return render(request, "vms_staff.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# Driver Schedule Form View.
def ScheduleForm(request):
    shift_choices = [
        ("morning", "Morning"),
        ("evening", "Evening"),
        ("day", "Day"),
        ("night", "Night"),
    ]
    shift_staffs = Driver.objects.filter(
        (Q(user__department__name__iexact="Transport")) & Q(user__role="User")
    )
    if request.method == "POST":
        form = DriverScheduleForm(request.POST, user=request.user)
        if form.is_valid():
            new_schedule = form.save(commit=False)
            new_schedule.created_by = request.user
            new_schedule.save()
            messages.success(request, "Shift schedule created successfully.")
            return redirect("vms:driver_schedule")
    else:
        form = DriverScheduleForm(user=request.user)
    context = {
        "form": form,
        "choices": shift_choices,
        "staffs": shift_staffs,
    }
    return render(request, "vms_schedule_form.html", context)


# Driver Schedule View.
def DriverScheduleView(request):
    DriverSchedule.update_shift_statuses()
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        schedule = DriverSchedule.objects.filter(shift_type="ongoing")
        page_number = request.GET.get("page")
        paginator = Paginator(schedule, 10)
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
    except Exception as e:
        context["error"] = str(e)
    view_name = request.resolver_match.view_name
    if view_name == "vms:driver_schedule" and current_user_role == "Admin":
        return render(request, "vms_schedule.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# Shift Edit Form View.
def ShiftEditView(request, id):
    edit_schedule = get_object_or_404(DriverSchedule, id=id)
    if request.method == "POST":
        form = ShiftEditForm(request.POST, instance=edit_schedule, user=request.user)
        if form.is_valid():
            edit_schedule = form.save(commit=False)
            edit_schedule.created_by = request.user
            edit_schedule.save()
            messages.success(request, "Shift schedule edited successfully.")
            return redirect("srm:schedule")
    else:
        form = ShiftEditForm(instance=edit_schedule, user=request.user)
    context = {"form": form, "edit_schedule": edit_schedule}
    return render(request, "shift_edit.html", context)


def ToggleSchedule(request, pk):
    if request.method == "POST":
        data = json.loads(request.body)
        schedule = DriverSchedule.objects.get(id=pk)
        schedule.is_active = data["is_active"]
        schedule.save()
        return JsonResponse({"status": "success"})


# Recurrence booking view.
def recurring_bookings():
    today = timezone.now().date()

    bookings = Booking.objects.filter(
        is_recurring=True,
        pickup_time__date=today,
        status__in=["WAITING", "CONFIRMED", "COMPLETED"],
    )

    for booking in bookings:
        if booking.recurrence_pattern == "DAILY":
            delta = timedelta(days=1)

        elif booking.recurrence_pattern == "WEEKLY":
            delta = timedelta(days=7)

        elif booking.recurrence_pattern == "MONTHLY":
            delta = timedelta(months=1)

        else:
            continue

        if booking.pickup_time:
            booking.pickup_time += delta
        if booking.drop_time:
            booking.drop_time += delta

        booking.status = "WAITING"
        booking.vehicle = None
        booking.driver = None

        booking.save()


# Success view.
def BookingSuccessView(request):
    if request.user.role == "Admin":
        redirect_url = reverse("vms:vms_admin_dashboard")
    else:
        redirect_url = reverse("cms:vms:vms_staff_dashboard")

    return render(request, "vms_booking_success.html", {"redirect_url": redirect_url})
