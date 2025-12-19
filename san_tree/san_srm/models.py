from django.db import models
from accounts.models import CustomUsers, Departments
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import Location

# Service Model.
class ServiceTypes(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, related_name='service_types')

    def __str__(self):
        return f'{self.name} {self.department}'
    
    class Meta:
        verbose_name_plural = 'Service Types'
    
# Block Model.
class Blocks(models.Model):
    name = models.CharField(max_length=100)

    # Method to define string representation of an object.
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Check for duplicate block names (case-insensitive)
        if Blocks.objects.filter(name__iexact=self.name).exclude(pk=self.pk).exists():
            raise ValidationError(f"A block with the name '{self.name}' already exists.")
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Blocks'

# Shift Types.
SHIFT_CHOICES = (
    ('morning', 'Morning'),
    ('evening', 'Evening'),
    ('day', 'Day'),
    ('night', 'Night'),
)

# Shift Model.
class ShiftSchedule(models.Model):
    shift_type = models.CharField(max_length=20, choices=SHIFT_CHOICES, default='Morning')
    shift_block = models.ForeignKey(Blocks, related_name='shift_blocks', on_delete=models.CASCADE, default=None)
    shift_staffs = models.ForeignKey(
        CustomUsers, 
        related_name='shift_staff', 
        on_delete=models.CASCADE,
        limit_choices_to=(models.Q(department__name="GDA") | models.Q(department__name="General Duty Assistant")) & models.Q(role='User'),
        )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.shift_staffs} - {self.shift_type}"
    
    def save(self, *args, **kwargs):
        if self.start_time and timezone.is_naive(self.start_time):
            self.start_time = timezone.make_aware(self.start_time, timezone.get_current_timezone())
        if self.end_time and timezone.is_naive(self.end_time):
            self.end_time = timezone.make_aware(self.end_time, timezone.get_current_timezone())
        super().save(*args, **kwargs)

    
# Status Choices.
STATUS_CHOICES = (
    ('Open', 'Open'),
    ('In Progress', 'In Progress'),
    ('Waiting', 'Waiting'),
    ('Pending', 'Pending'),
    ('On Hold', 'On Hold'),
    ('Completed', 'Completed'),
)

# Request Service Model.
class Service(models.Model):
    service_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    service_type = models.ForeignKey(ServiceTypes, on_delete=models.SET_NULL, null=True, blank=True)
    service_block = models.ForeignKey(Blocks, related_name='service_blocks', on_delete=models.SET_NULL, null=True, blank=True)
    UHID = models.CharField(max_length=20, unique=True, null=True, blank=True)
    from_location = models.ForeignKey(Location, related_name='service_from', on_delete=models.SET_NULL, null=True, blank=True)
    to_location = models.ForeignKey(Location, related_name='service_to', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(default='enter description here', max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    started_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(ShiftSchedule, related_name='srm_service_staff', on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(CustomUsers, related_name='srm_created_service', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return str(self.service_type)

    @property
    def time_taken(self):
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def start_time(self):
        if self.started_at and self.created_at:
            return self.started_at - self.created_at
        return None
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super().save(*args, **kwargs)

        # Assign service number only once when new
        if is_new and not self.service_number:
            self.service_number = f"SRM{self.id}"
            Service.objects.filter(pk=self.pk).update(service_number=self.service_number)

        if not is_new:
            before = Service.objects.get(pk=self.pk)
            old_status = before.status
            new_status = self.status

            if old_status == 'Open' and new_status == 'In Progress':
                if not self.started_at:
                    self.started_at = timezone.now()
            
            if old_status == 'In Progress' and new_status == 'Completed':
                if not self.completed_at:
                    self.completed_at = timezone.now()

        super().save(update_fields=['started_at', 'completed_at'])

# Service Request Queue Model.
class ServiceRequestQueue(models.Model):
    service_request = models.ForeignKey(Service, related_name='service_queue' ,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.service_request.id)
    
    class Meta:
        ordering = ['created_at']
    
# Service Remarks Image Path. 
def generate_service_image_path(instance, filename):
    filename = os.path.basename(filename)  
    return f'service_remark_images/{filename}'
    
# Generate Service Model.
class GenerateService(models.Model):
    generate_number = models.CharField(max_length=20, unique=True, blank=True)
    service_type = models.ForeignKey(ServiceTypes, on_delete=models.SET_NULL, null=True, blank=True)
    from_location = models.ForeignKey(Location, related_name='generate_from', on_delete=models.SET_NULL, null=True, blank=True)
    to_location = models.ForeignKey(Location, related_name='generate_to', on_delete=models.SET_NULL, null=True, blank=True)
    generate_by = models.ForeignKey(ShiftSchedule, related_name='srm_generate_service', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Completed')
    generate_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    attachment = models.ImageField(upload_to=generate_service_image_path, null=True, blank=True)

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

        if is_new and self.generate_number.startswith("GSN") and self.generate_number == f"GSN{GenerateService.objects.count()}":
            self.generate_number = f"GSN{self.id}"
            GenerateService.objects.filter(pk=self.pk).update(generate_number=self.generate_number)

        # Compress image before saving
        if self.attachment and image_changed:
            try:
                img = Image.open(self.attachment)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                output = BytesIO()
                img.save(output, format='JPEG', quality=70)
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
    return f'service_remark_images/{filename}'

# Service Remarks.
class ServiceRemarks(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    remarks = models.TextField()
    created_by = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, null=True, blank=True, related_name='srm_created_remark')
    created_at = models.DateTimeField(auto_now=True)
    attachment = models.ImageField(upload_to=service_remark_image_path, null=True, blank=True)

    def __str__(self):
        return f'{self.service} {self.remarks}'
    
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
                img.save(output, format='JPEG', quality=70)
                output.seek(0)

                # Keep original file name
                self.attachment = ContentFile(output.read(), name=self.attachment.name)

            except Exception as e:
                print("Image compression error:", e)

        # Save instance
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Service Remarks'
