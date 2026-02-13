from san_vms.models import Booking, Vehicle, BookingStatus


def HandleCriticalBooking(critical_booking):

    # find available vehicle.
    available_vehicle = Vehicle.objects.filter(
        status="AVAILABLE",
        is_emergency_active=False
    ).first()

    # assign available vehicle to critical booking.
    if available_vehicle:
        assign_vehicle(critical_booking, available_vehicle)
        return

    # find normal booking that can be cancelled.
    normal_booking = Booking.objects.select_for_update().filter(
        status=BookingStatus.CONFIRMED,
        priority="NORMAL",
        vehicle__isnull=False
    ).select_related("vehicle", "driver").first()

    if normal_booking:

        vehicle = normal_booking.vehicle
        driver = normal_booking.driver
        normal_booking.status = BookingStatus.CANCELLED
        normal_booking.vehicle = None

        if driver:
            driver.user.status = "vacant"
            driver.user.save()
            normal_booking.driver = None

        normal_booking.save()
        assign_vehicle(critical_booking, vehicle)
        return True
    
    critical_booking.status = BookingStatus.WAITING
    critical_booking.save()
    return False


def assign_vehicle(booking, vehicle):

    vehicle = Vehicle.objects.select_for_update().get(id=vehicle.id)

    booking.vehicle = vehicle
    booking.status = BookingStatus.CONFIRMED
    booking.save()

    vehicle.status = "IN_TRANSIT"
    vehicle.is_emergency_active = True
    vehicle.save()
