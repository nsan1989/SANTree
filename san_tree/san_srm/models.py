from django.db import models
from accounts.models import CustomUsers, Departments, Location
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os

# Service Model.
class ServiceTypes(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, related_name='service_types')

    def __str__(self):
        return f'{self.name} {self.department}'

# Status Choices.
STATUS_CHOICES = (
    ('open', 'Open'),
    ('in_progress', 'In Progress'),
    ('waiting', 'Waiting'),
    ('completed', 'Completed'),
)

# Prority Choices.
PRIORITY_CHOICES = (
    ('high', 'High'),
    ('mid', 'Mid'),
    ('low', 'Low')
)

# Service Model.
class Service(models.Model):
    service_number = models.CharField(max_length=20, unique=True, blank=True)
    service_type = models.ForeignKey(ServiceTypes, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Location, related_name='service_locations', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_by = models.ForeignKey(CustomUsers, related_name='srm_created_service', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(CustomUsers, related_name='srm_assigned_service', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    @property
    def time_taken(self):
        if self.completed_at and self.created_at:
            return self.completed_at - self.created_at
        return None
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        # Assign tasks number only once when new
        if is_new and not self.service_number:
            self.service_number = f"SRM{self.id}"
            Service.objects.filter(pk=self.pk).update(service_number=self.service_number)

    def __str__(self):
        return str(self.service_type)

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
