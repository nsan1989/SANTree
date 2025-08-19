from django.db import models
from accounts.models import CustomUsers, Departments, Location
from django.utils import timezone
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from django.core.files.base import ContentFile
import os

# Predefine Complaint Types.
class ComplaintType(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, related_name='complaint_types')

    def __str__(self):
        return self.name

# Status Choices.
STATUS_CHOICES = (
    ('review', 'Review'),
    ('rejected', 'Rejected'),
    ('open', 'Open'),
    ('cancelled', 'Cancelled'),
    ('in_progress', 'In Progress'),
    ('resolved', 'Resolved'),
    ('halt', 'Halt'),
    ('waiting', 'Waiting')
)

# Prority Choices.
PRIORITY_CHOICES = (
    ('high', 'High'),
    ('mid', 'Mid'),
    ('low', 'Low')
)

def complaint_image_path(instance, filename):
    filename = os.path.basename(filename)  
    return f'complaint_images/{filename}'

# Complaint Model.
class Complaint(models.Model):
    complaint_number = models.CharField(max_length=20, unique=True, blank=True)
    complaint_type = models.ForeignKey(ComplaintType, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    assigned_to = models.ForeignKey(CustomUsers, related_name='cms_assigned_complaints', on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Location, related_name='complaint_locations', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Low')
    department = models.ForeignKey(Departments, on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUsers, related_name='cms_created_complaints', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    attachment = models.ImageField(upload_to=complaint_image_path, null=True, blank=True)

    # Method to define string representation of an object.
    def __str__(self):
        return str(self.complaint_type)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        image_changed = False

        # Check if attachment has changed (only for existing object)
        if self.pk:
            old_attachment = Complaint.objects.get(pk=self.pk).attachment
            if self.attachment and self.attachment != old_attachment:
                image_changed = True
        else:
            image_changed = bool(self.attachment)

        # Handle completed_at timestamp based on status
        if self.status == 'Resolved' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'Resolved':
            self.completed_at = None

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

        # Assign complaint number only once when new
        if is_new and not self.complaint_number:
            self.complaint_number = f"CMS{self.id}"
            Complaint.objects.filter(pk=self.pk).update(complaint_number=self.complaint_number)
    
    @property
    def time_taken(self):
        if self.completed_at and self.created_at:
            return self.completed_at - self.created_at
        return None

    def _str_(self):
        return str(self.complaint_type)

# Complaint History Model.
class ComplaintHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    status_changed_to = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    changed_by = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, null=True, blank=True, related_name='changed_complaints')
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.complaint.complaint_type)

# Time Choices
TIME_DURATION_CHOICES = [
    ('00:03', '3 min'),
    ('00:30', '30 min'),
    ('01:00', '1 hr'),
    ('01:30', '1 hr 30 min'),
    ('02:00', '2 hr'),
    ('02:30', '2 hr 30 min'),
    ('03:00', '3 hr'),
    ('03:30', '3 hr 30 min'),
]

# Reassigned Complaint Model
class ReassignedComplaint(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    reassigned_to = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, null=True, blank=True, related_name='reassign_complaints')
    duration = models.CharField(max_length=5, choices=TIME_DURATION_CHOICES, default='00:00', verbose_name="Duration")
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.reassigned_to)
    
# Reassigned Department Model
class ReassignDepartment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    reassign_to = models.ForeignKey(Departments, on_delete=models.CASCADE, null=True, blank=True, related_name='reassign_departments')
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.reassign_to)
    
def complaint_remark_image_path(instance, filename):
    filename = os.path.basename(filename)  
    return f'remark_images/{filename}'
    
# Remark Model
class ComplaintRemarks(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    remarks = models.TextField()
    created_by = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, null=True, blank=True, related_name='cms_created_remark')
    created_at = models.DateTimeField(auto_now=True)
    attachment = models.ImageField(upload_to=complaint_remark_image_path, null=True, blank=True)

    def __str__(self):
        return self.remarks
    
    # Compress image before saving
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        image_changed = False

        # Check if attachment has changed (only for existing object)
        if self.pk:
            old_attachment = Complaint.objects.get(pk=self.pk).attachment
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
        