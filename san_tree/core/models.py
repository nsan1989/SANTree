from django.db import models
from san_srm.models import *


# Anonymous Service Generate Model.
class AnonymousServiceGenerate(models.Model):
    service_number = models.CharField(max_length=20, unique=True, blank=True)
    service_type = models.ForeignKey(ServiceTypes, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(ShiftSchedule, related_name='anonymous_service_staff', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='In Progress')
    block = models.ForeignKey(Blocks, related_name='anonymous_blocks', on_delete=models.SET_NULL, null=True, blank=True)
    from_location = models.ForeignKey(Location, related_name='anonymous_service_from', on_delete=models.SET_NULL, null=True, blank=True)
    to_location = models.ForeignKey(Location, related_name='anonymous_service_to', on_delete=models.SET_NULL, null=True, blank=True)
    generate_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.service_type)
    
    @property
    def time_taken(self):
        if self.completed_at and self.generate_at:
            return self.completed_at - self.generate_at
        return None
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.service_number:
            temp_id = AnonymousServiceGenerate.objects.count() + 1
            self.service_number = f"ASG{temp_id}"

        if is_new and self.service_number.startswith("ASG") and self.service_number == f"GSN{AnonymousServiceGenerate.objects.count()}":
            self.service_number = f"ASG{self.id}"
            AnonymousServiceGenerate.objects.filter(pk=self.pk).update(service_number=self.service_number)

        super().save(*args, **kwargs)
