from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError

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


# Payment status.
class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"
    REFUNDED = "REFUNDED", "Refunded"


# Patient Service Type
class PatientServiceType(models.TextChoices):
    PATIENT_DROP = "PATIENT_DROP", "Patient Drop"
    DECEASED_TRANSPORT = "DECEASED_TRANSPORT", "Deceased Transport"
    OTHER = "OTHER", "Other"


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

    def save(self, *args, **kwargs):
        if (
            Driver.objects.filter(
                user__username__iexact=self.user.username,
                license_number__iexact=self.license_number,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(
                f"A Driver with the name '{self.user.username}' and '{self.license_number}' already exists."
            )
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["user__username"]
        verbose_name_plural = "Users"


# Recurrence pattern.
class PatternChoices(models.TextChoices):
    DAILY = "DAILY", "Daily"
    WEEKLY = "WEEKLY", "Weekly"
    MONTHLY = "MONTHLY", "Monthly"


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
    passengers = models.IntegerField(null=True, blank=True, default=0)
    description = models.TextField(null=True, blank=True)
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
        max_length=20,
        choices=PatternChoices.choices,
        default=PatternChoices.DAILY,
        blank=True,
        null=True,
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
        limit_choices_to=models.Q(
            user__department__name__iexact="Transport",
            user__role="User",
        ),
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


# Patient Booking model.
class PatientBooking(models.Model):
    booking_number = models.CharField(max_length=50, unique=True)
    service_type = models.CharField(
        max_length=50,
        choices=PatientServiceType.choices,
        default=PatientServiceType.PATIENT_DROP,
    )
    patient_name = models.CharField(max_length=255)
    patient_uhid = models.CharField(max_length=50, unique=True, null=True, blank=True)
    patient_phone = models.CharField(max_length=20, null=True, blank=True)
    hospital_location = models.CharField(max_length=255)
    drop_location_text = models.CharField(max_length=255)
    drop_latitude = models.FloatField(null=True, blank=True)
    drop_longitude = models.FloatField(null=True, blank=True)
    distance_km_estimated = models.FloatField(null=True, blank=True)
    distance_km_final = models.FloatField(null=True, blank=True)
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    per_km_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    extra_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    status = models.CharField(
        max_length=20, choices=BookingStatus.choices, default=BookingStatus.WAITING
    )
    remarks = models.TextField(null=True, blank=True)
    booked_by = models.CharField(max_length=255, null=True, blank=True)
    assigned_vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_bookings_vehicle",
    )
    assigned_driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_bookings_driver",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Patient Booking {self.booking_number}"


# Patient Payment model.
class PatientPayment(models.Model):
    booking = models.ForeignKey(
        PatientBooking, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    payment_provider = models.CharField(max_length=50, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    gateway_order_id = models.CharField(
        max_length=255, null=True, blank=True, db_index=True
    )
    gateway_payment_id = models.CharField(
        max_length=255, null=True, blank=True, db_index=True
    )
    gateway_signature = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    initiated_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(null=True, blank=True)
    raw_response = models.JSONField(null=True, blank=True)
    upi_id = models.CharField(max_length=100, null=True, blank=True)
    qr_code_image = models.ImageField(upload_to="payment_qr/", null=True, blank=True)
    upi_transaction_ref = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Payment for Booking {self.booking.booking_number} - {self.status}"
