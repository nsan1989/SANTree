from django.db import models
from accounts.models import CustomUsers

# Vehicle status.
class VehicleStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Available"
    BOOKED = "BOOKED", "Booked"
    IN_TRANSIT = "IN_TRANSIT", "In Transit"
    UNDER_REPAIR = "UNDER_REPAIR", "Under Repair"
    INACTIVE = "INACTIVE", "Inactive"

# Driver status.
class DriverStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Available"
    ON_DUTY = "ON_DUTY", "On Duty"
    OFF_DUTY = "OFF_DUTY", "Off Duty"

# Booking status.
class BookingStatus(models.TextChoices):
    WAITING = "WAITING", "Waiting"
    CONFIRMED = "CONFIRMED", "Confirmed"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"

# Booking types.
class BookingTypes(models.TextChoices):
    DROP = "DROP", "Drop"
    PICKUP = "PICKUP", "Pickup"
    DROP_AND_PICKUP = "DROP_AND_PICKUP", "Drop and Pickup"

# Vehicle model.
class Vehicle(models.Model):
    vehicle_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=50)  
    capacity_weight = models.FloatField(null=True, blank=True)  
    capacity_volume = models.FloatField(null=True, blank=True)  
    fuel_type = models.CharField(max_length=20, choices=[('DIESEL', 'Diesel'), ('PETROL', 'Petrol'), ('ELECTRIC', 'Electric')])
    status = models.CharField(max_length=20, choices=VehicleStatus.choices, default=VehicleStatus.AVAILABLE)
    current_location = models.CharField(max_length=255, blank=True)
    maintenance_due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.vehicle_number

# Driver model.
class Driver(models.Model):
    user = models.OneToOneField(CustomUsers, on_delete=models.CASCADE, related_name="driver_profile")
    license_type = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)

    status = models.CharField(
        max_length=20,
        choices=DriverStatus.choices,
        default=DriverStatus.AVAILABLE
    )

    shift_start = models.TimeField()
    shift_end = models.TimeField()

    def __str__(self):
        return self.user.username

# Cargo model.
class Cargo(models.Model):
    cargo_type = models.CharField(max_length=100)
    weight = models.FloatField()  
    volume = models.FloatField()  
    fragile = models.BooleanField(default=False)
    refrigeration_required = models.BooleanField(default=False)

    def __str__(self):
        return self.cargo_type

# Booking model.
class Booking(models.Model):
    booking_type = models.CharField(max_length=20, choices=BookingTypes.choices)
    pickup_location = models.CharField(max_length=255)
    drop_location = models.CharField(max_length=255, blank=True)
    pickup_time = models.DateTimeField(null=True, blank=True)
    drop_time = models.DateTimeField(null=True, blank=True)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings_driver")
    booked_by = models.ForeignKey(CustomUsers, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings_user")
    assigned_to = models.ForeignKey(CustomUsers, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings_assigned")
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.WAITING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id}"

# Driver schedule.
class DriverSchedule(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)

    def __str__(self):
        return self.driver.user.username

# Vehicle maintenance.
class VehicleMaintenance(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle.vehicle_number} Maintenance"
