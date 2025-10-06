from django.db import models
from accounts.models import CustomUsers, Departments, Location
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os

# Predefined Tasks Model.
class TasksTypes(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, related_name='tasks_types')

    def __str__(self):
        return f'{self.name} {self.department}'
    
    class Meta:
        verbose_name_plural = 'Tasks Types'

# Status Choices.
STATUS_CHOICES = (
    ('open', 'Open'),
    ('in_progress', 'In Progress'),
    ('waiting', 'Waiting'),
    ('review', 'Review'),
    ('rejected', 'Rejected'),
    ('completed', 'Completed'),
    ('halt', 'Halt'),
)

# Prority Choices.
PRIORITY_CHOICES = (
    ('high', 'High'),
    ('mid', 'Mid'),
    ('low', 'Low')
)

def task_image_path(instance, filename):
    filename = os.path.basename(filename)  
    return f'task_images/{filename}'

# Tasks Model.
class Tasks(models.Model):
    tasks_number = models.CharField(max_length=20, unique=True, blank=True)
    tasks_types = models.ForeignKey(TasksTypes, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Location, related_name='tasks_locations', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Low')
    department = models.ForeignKey(Departments, on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUsers, related_name='tms_created_tasks', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(CustomUsers, related_name='tms_assigned_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    waiting_time = models.DateTimeField(auto_now=True)
    attachment = models.ImageField(upload_to=task_image_path, null=True, blank=True)
    
    def __str__(self):
        return str(self.tasks_types)

    @property
    def time_taken(self):
        if self.completed_at and self.created_at:
            return self.completed_at - self.created_at
        return None

    # auto assign completed time
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        image_changed = False

        # Check if attachment has changed (only for existing object)
        if self.pk:
            old_attachment = Tasks.objects.get(pk=self.pk).attachment
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

        # Assign tasks number only once when new
        if is_new and not self.tasks_number:
            self.tasks_number = f"TMS{self.id}"
            Tasks.objects.filter(pk=self.pk).update(tasks_number=self.tasks_number)

    class Meta:
        verbose_name_plural = 'Tasks'
    
def task_remark_image_path(instance, filename):
    filename = os.path.basename(filename)  
    return f'task_remark_images/{filename}'

# Tasks Remarks.
class TasksRemarks(models.Model):
    tasks = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    remarks = models.TextField()
    created_by = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, null=True, blank=True, related_name='tms_created_remark')
    created_at = models.DateTimeField(auto_now=True)
    attachment = models.ImageField(upload_to=task_remark_image_path, null=True, blank=True)

    def __str__(self):
        return f'{self.tasks} {self.remarks}'
    
    # Compress image before saving
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        image_changed = False

        # Check if attachment has changed (only for existing object)
        if self.pk:
            old_attachment = Tasks.objects.get(pk=self.pk).attachment
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
        verbose_name_plural = 'Tasks Remarks'
