from san_vms.models import Booking, Vehicle, BookingStatus


def HandleCriticalBooking(critical_booking):

    normal_booking = (
        Booking.objects.select_for_update()
        .filter(
            status=BookingStatus.CONFIRMED,
            priority="NORMAL",
            vehicle=critical_booking.vehicle_id
        )
        .select_related("vehicle", "driver")
        .exclude(id=critical_booking.id)
        .first()
    )

    if normal_booking:
        vehicle = normal_booking.vehicle
        driver = normal_booking.driver

        normal_booking.status = BookingStatus.CANCELLED
        normal_booking.vehicle = None
        normal_booking.driver = None
        normal_booking.save()

        assign_vehicle(critical_booking, vehicle, driver)
        return True
    
    return False


def assign_vehicle(booking, vehicle, driver):

    vehicle = Vehicle.objects.select_for_update().get(id=vehicle.id)

    booking.vehicle = vehicle
    booking.driver = driver
    booking.status = BookingStatus.CONFIRMED
    booking.save()

    if driver:
        driver.user.status = "engaged"
        driver.user.save()

    vehicle.status = "IN_TRANSIT"
    vehicle.is_emergency_active = True
    vehicle.save()
