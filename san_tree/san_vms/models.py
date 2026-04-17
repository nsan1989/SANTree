from django.db import models
from django.db.models import Q
from django.utils import timezone

from accounts.models import CustomUsers


# Vehicle status.
class VehicleStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Available"
    BOOKED = "BOOKED", "Booked"
    IN_TRANSIT = "IN_TRANSIT", "In Transit"
    UNDER_REPAIR = "UNDER_REPAIR", "Under Repair"
    INACTIVE = "INACTIVE", "Inactive"


# Booking status.
class BookingStatus(models.TextChoices):
    WAITING = "WAITING", "Waiting"
    CONFIRMED = "CONFIRMED", "Confirmed"
    ACKNOWLEDGE = "ACKNOWLEDGE", "Acknowledge"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


# Booking types.
class BookingTypes(models.TextChoices):
    DROP = "DROP", "Drop"
    PICKUP = "PICKUP", "Pickup"
    DROP_AND_PICKUP = "DROP_AND_PICKUP", "Drop and Pickup"


# Booking priorities.
class BookingPriority(models.TextChoices):
    NORMAL = "NORMAL", "Normal"
    HIGH = "HIGH", "High"
    CRITICAL = "CRITICAL", "Critical"


# Vehicle model.
class Vehicle(models.Model):
    vehicle_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.CharField(max_length=50)
    capacity_weight = models.FloatField(null=True, blank=True)
    capacity_volume = models.FloatField(null=True, blank=True)
    fuel_type = models.CharField(
        max_length=20,
        choices=[("DIESEL", "Diesel"), ("PETROL", "Petrol"), ("ELECTRIC", "Electric")],
    )
    status = models.CharField(
        max_length=20, choices=VehicleStatus.choices, default=VehicleStatus.AVAILABLE
    )
    maintenance_due_date = models.DateField(null=True, blank=True)
    is_emergency_active = models.BooleanField(default=False)

    def __str__(self):
        return self.vehicle_number

    @property
    def current_location(self):
        active_booking = (
            self.bookings.filter(status__in=["CONFIRMED", "IN_PROGRESS"])
            .order_by("-created_at")
            .first()
        )

        if active_booking:
            if active_booking.status == "CONFIRMED":
                return active_booking.pickup_location
            if active_booking.status == "IN_PROGRESS":
                return f"En route to {active_booking.drop_location}"

        last_completed = (
            self.bookings.filter(status="COMPLETED").order_by("-created_at").first()
        )

        if last_completed:
            return last_completed.drop_location

        return "Depot"


# Driver model.
class Driver(models.Model):
    user = models.OneToOneField(
        CustomUsers, on_delete=models.CASCADE, related_name="driver_profile"
    )
    license_number = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username


# Cargo model.
class Cargo(models.Model):
    cargo_type = models.CharField(max_length=100)
    weight = models.FloatField()
    fragile = models.BooleanField(default=False)
    refrigeration_required = models.BooleanField(default=False)

    def __str__(self):
        return self.cargo_type


# Booking model.
class Booking(models.Model):
    booking_type = models.CharField(max_length=20, choices=BookingTypes.choices)
    priority = models.CharField(
        max_length=20, choices=BookingPriority.choices, default=BookingPriority.NORMAL
    )
    department_priority = models.IntegerField(
        default=0, help_text="Higher value = higher priority department"
    )
    pickup_location = models.CharField(max_length=255)
    drop_location = models.CharField(max_length=255, blank=True)
    pickup_time = models.DateTimeField(null=True, blank=True)
    drop_time = models.DateTimeField(null=True, blank=True)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, null=True, blank=True)
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings_driver",
    )
    booked_by = models.ForeignKey(
        CustomUsers,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings_user",
    )
    assigned_to = models.ForeignKey(
        CustomUsers,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings_assigned",
    )
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(
        max_length=50, blank=True, help_text="Example: DAILY, WEEKLY_MON, WEEKLY_FRI"
    )
    status = models.CharField(
        max_length=20, choices=BookingStatus.choices, default=BookingStatus.WAITING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle"],
                condition=Q(status__in=["CONFIRMED", "IN_PROGRESS"]),
                name="unique_active_booking_per_vehicle",
            )
        ]


# Shift Manager
class ShiftManager(models.Manager):
    def active_now(self):
        now = timezone.now()
        return self.filter(status="ongoing", start_time__lte=now, end_time__gte=now)


# Driver schedule.
class DriverSchedule(models.Model):
    SHIFT_CHOICES = [
        ("morning", "Morning"),
        ("evening", "Evening"),
        ("day", "Day"),
        ("night", "Night"),
    ]
    SHIFT_STATUS = [
        ("scheduled", "Scheduled"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    shift_staffs = models.ForeignKey(
        Driver,
        related_name="shift_staff",
        on_delete=models.CASCADE,
        limit_choices_to=(models.Q(user__department__name__iexact="Transport"))
        & models.Q(user__role="User"),
    )
    shift_type = models.CharField(
        max_length=20, choices=SHIFT_CHOICES, default="Morning"
    )
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=SHIFT_STATUS, default="scheduled")
    is_active = models.BooleanField(default=True)

    objects = ShiftManager()

    @classmethod
    def update_shift_statuses(cls):
        now = timezone.now()

        cls.objects.filter(start_time__gt=now).update(status="scheduled")

        cls.objects.filter(start_time__lte=now, end_time__gte=now).update(
            status="ongoing"
        )

        cls.objects.filter(end_time__lt=now).update(status="completed")

    def __str__(self):
        return self.shift_staffs.user.username


# Vehicle maintenance.
class VehicleMaintenance(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle.vehicle_number} Maintenance"
