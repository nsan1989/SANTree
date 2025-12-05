from django.db import models
from accounts.models import CustomUsers, Departments, Location
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os
from datetime import timedelta
from dateutil.relativedelta import relativedelta 
from django.utils.timezone import now

# Tasks Types.
class TasksTypes(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, related_name='tasks_types')

    def __str__(self):
        return f'{self.name} {self.department}'
    
    class Meta:
        verbose_name_plural = 'Tasks Types'

# Tasks Frequency.
TASKS_FREQUENCY = (
    ('Daily', 'Daily'),
    ('Weekly', 'Weekly'),
    ('Monthly', 'Monthly'),
)

# Status Choices.
STATUS_CHOICES = (
    ('Waiting', 'Waiting'),
    ('In Progress', 'In Progress'),
    ('Postponed', 'Postponed'),
    ('Overdue', 'Overdue'),
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled'),
)

def task_image_path(instance, filename):
    filename = os.path.basename(filename)  
    return f'task_images/{filename}'

# Tasks Model.
class Tasks(models.Model):
    tasks_number = models.CharField(max_length=20, unique=True, blank=True)
    tasks_types = models.ForeignKey(TasksTypes, on_delete=models.SET_NULL, null=True, blank=True)
    task_frequency = models.CharField(max_length=20, choices=TASKS_FREQUENCY, default='Daily')
    location = models.ForeignKey(Location, related_name='tasks_locations', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Waiting')
    department = models.ForeignKey(Departments, on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUsers, related_name='tms_created_tasks', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(CustomUsers, related_name='tms_assigned_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    next_date = models.DateTimeField(null=True, blank=True)
    attachment = models.ImageField(upload_to=task_image_path, null=True, blank=True)
    
    def __str__(self):
        return str(self.tasks_types)

#    @property
#    def time_taken(self):
#        if self.completed_at and self.created_at:
#            return self.completed_at - self.created_at
#        return None

    # auto assign completed time
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_frequency = None
        if not is_new:
            old_frequency = Tasks.objects.get(pk=self.pk).task_frequency

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

        # Auto-set next_date based on frequency ONLY for new or if frequency changed
        if (is_new or old_frequency != self.task_frequency) or not self.next_date:
            base_date = self.created_at or now()

            if self.task_frequency == "Daily":
                self.next_date = base_date + timedelta(days=1)
            elif self.task_frequency == "Weekly":
                self.next_date = base_date + timedelta(weeks=1)
            elif self.task_frequency == "Monthly":
                self.next_date = base_date + relativedelta(months=1)

            Tasks.objects.filter(pk=self.pk).update(next_date=self.next_date)

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
