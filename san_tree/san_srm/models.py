import os
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from PIL import Image
from datetime import timedelta

from accounts.models import CustomUsers, Departments, Location


# Service Model.
class ServiceTypes(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(
        Departments, on_delete=models.CASCADE, related_name="service_types"
    )

    def __str__(self):
        return f"{self.name} {self.department}"

    class Meta:
        verbose_name_plural = "Service Types"


# Block Model.
class Blocks(models.Model):
    name = models.CharField(max_length=100)

    # Method to define string representation of an object.
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Check for duplicate block names (case-insensitive)
        if Blocks.objects.filter(name__iexact=self.name).exclude(pk=self.pk).exists():
            raise ValidationError(
                f"A block with the name '{self.name}' already exists."
            )
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Blocks"


# Shift Types.
SHIFT_CHOICES = (
    ("morning", "Morning"),
    ("evening", "Evening"),
    ("day", "Day"),
    ("night", "Night"),
)


# Shift Manager
class ShiftManager(models.Manager):
    def active_now(self):
        now = timezone.now()
        return self.filter(status="ongoing", start_time__lte=now, end_time__gte=now)


# Shift Model.
class ShiftSchedule(models.Model):
    SHIFT_STATUS = [
        ("scheduled", "Scheduled"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    shift_type = models.CharField(
        max_length=20, choices=SHIFT_CHOICES, default="Morning"
    )
    shift_block = models.ForeignKey(
        Blocks, related_name="shift_blocks", on_delete=models.CASCADE, default=None
    )
    shift_staffs = models.ForeignKey(
        CustomUsers,
        related_name="shift_staff",
        on_delete=models.CASCADE,
        limit_choices_to=(
            models.Q(department__name="GDA")
            | models.Q(department__name="General Duty Assistant")
        )
        & models.Q(role="User"),
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=SHIFT_STATUS, default="scheduled")

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
        return f"{self.shift_staffs} - {self.shift_type} ({self.status})"


# Status Choices.
STATUS_CHOICES = (
    ("Open", "Open"),
    ("In Progress", "In Progress"),
    ("Waiting", "Waiting"),
    ("Pending", "Pending"),
    ("On Hold", "On Hold"),
    ("Completed", "Completed"),
)


# Request Service Model.
class Service(models.Model):
    service_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    service_type = models.ForeignKey(
        ServiceTypes, on_delete=models.SET_NULL, null=True, blank=True
    )
    service_block = models.ForeignKey(
        Blocks,
        related_name="service_blocks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    UHID = models.CharField(max_length=20, null=True, blank=True)
    from_location = models.ForeignKey(
        Location,
        related_name="service_from",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    to_location = models.ForeignKey(
        Location,
        related_name="service_to",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    description = models.TextField(
        default="enter description here", max_length=100, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Open")
    assigned_to = models.ForeignKey(
        ShiftSchedule,
        related_name="srm_service_staff",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    handled_by = models.ForeignKey(
        CustomUsers,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="handled_services",
    )
    created_by = models.ForeignKey(
        CustomUsers, related_name="srm_created_service", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    hold_used = models.DateTimeField(default=False)

    def __str__(self):
        return str(self.service_type)

    @property
    def start_time(self):
        if self.started_at and self.created_at:
            return self.started_at - self.created_at
        return None

    @property
    def time_taken(self):
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None

    @property
    def is_overdue(self):
        if self.deadline and self.status in ["In Progress", "On Hold"]:
            return timezone.now() > self.deadline
        return False

    @property
    def remaining_time(self):
        if self.deadline and self.status in ["In Progress", "On Hold"]:
            remaining = self.deadline - timezone.now()
            return remaining if remaining.total_seconds() > 0 else None
        return None

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        now = timezone.now()

        if not is_new:
            before = Service.objects.get(pk=self.pk)
            old_status = before.status
            new_status = self.status

            # Started
            if new_status == "In Progress" and not self.started_at:
                self.started_at = now
                self.deadline = now + timedelta(minutes=15)

            elif new_status == "On Hold":
                if self.hold_used:
                    raise ValueError("Extension already used once.")

                if old_status != "In Progress":
                    raise ValueError("Service must be In Progress before Hold.")

                self.deadline = now + timedelta(minutes=20)
                self.hold_used = True

        super().save(*args, **kwargs)

        # Assign service number only once when new
        if is_new and not self.service_number:
            self.service_number = f"SRM{self.id}"
            Service.objects.filter(pk=self.pk).update(
                service_number=self.service_number
            )


# Service Request Queue Model.
class ServiceRequestQueue(models.Model):
    service_request = models.ForeignKey(
        Service, related_name="service_queue", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.service_request.id)

    class Meta:
        ordering = ["created_at"]


# Service Remarks Image Path.
def generate_service_image_path(instance, filename):
    filename = os.path.basename(filename)
    return f"service_remark_images/{filename}"


# Generate Service Model.
class GenerateService(models.Model):
    generate_number = models.CharField(max_length=20, unique=True, blank=True)
    service_type = models.ForeignKey(
        ServiceTypes, on_delete=models.SET_NULL, null=True, blank=True
    )
    from_location = models.ForeignKey(
        Location,
        related_name="generate_from",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    to_location = models.ForeignKey(
        Location,
        related_name="generate_to",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    generate_by = models.ForeignKey(
        ShiftSchedule, related_name="srm_generate_service", on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="Completed"
    )
    generate_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    attachment = models.ImageField(
        upload_to=generate_service_image_path, null=True, blank=True
    )

    def __str__(self):
        return str(self.service_type)

    @property
    def time_taken(self):
        if self.completed_at and self.generate_at:
            return self.completed_at - self.generate_at
        return None

    # Compress image before saving
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        image_changed = False
        super().save(*args, **kwargs)

        # Assign service number only once when new
        if is_new and not self.generate_number:
            temp_id = GenerateService.objects.count() + 1
            self.generate_number = f"GSN{temp_id}"

        if (
            is_new
            and self.generate_number.startswith("GSN")
            and self.generate_number == f"GSN{GenerateService.objects.count()}"
        ):
            self.generate_number = f"GSN{self.id}"
            GenerateService.objects.filter(pk=self.pk).update(
                generate_number=self.generate_number
            )

        # Compress image before saving
        if self.attachment and image_changed:
            try:
                img = Image.open(self.attachment)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                output = BytesIO()
                img.save(output, format="JPEG", quality=70)
                output.seek(0)

                # Keep original file name
                self.attachment = ContentFile(output.read(), name=self.attachment.name)

            except Exception as e:
                print("Image compression error:", e)

        # Save instance
        super().save(*args, **kwargs)


# Service Remarks Image Path.
def service_remark_image_path(instance, filename):
    filename = os.path.basename(filename)
    return f"service_remark_images/{filename}"


# Service Remarks.
class ServiceRemarks(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    remarks = models.TextField()
    created_by = models.ForeignKey(
        CustomUsers,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="srm_created_remark",
    )
    created_at = models.DateTimeField(auto_now=True)
    attachment = models.ImageField(
        upload_to=service_remark_image_path, null=True, blank=True
    )

    def __str__(self):
        return f"{self.service} {self.remarks}"

    # Compress image before saving
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        image_changed = False

        # Check if attachment has changed (only for existing object)
        if self.pk:
            old_attachment = Service.objects.get(pk=self.pk).attachment
            if self.attachment and self.attachment != old_attachment:
                image_changed = True
        else:
            image_changed = bool(self.attachment)

        # Compress image before saving
        if self.attachment and image_changed:
            try:
                img = Image.open(self.attachment)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                output = BytesIO()
                img.save(output, format="JPEG", quality=70)
                output.seek(0)

                # Keep original file name
                self.attachment = ContentFile(output.read(), name=self.attachment.name)

            except Exception as e:
                print("Image compression error:", e)

        # Save instance
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Service Remarks"
