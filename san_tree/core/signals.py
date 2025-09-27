from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from san_cms.models import Complaint
from san_tms.models import Tasks
from san_srm.models import Service

# Complaint gmail handler
@receiver(post_save, sender=Complaint)
def ComplaintGmailHandler(sender, instance, created, **kwargs):
    if created and instance.assigned_to:
        subject = "New complaint assigned"
        message = f"Helle {instance.assigned_to}, \n\nA new complaint has been assigned to you"
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.assigned_to.email],
            fail_silently=False,
        )

# Task gmail handler
@receiver(post_save, sender=Tasks)
def TaskGmailHandler(sender, instance, created, **kwargs):
    if created and instance.assigned_to:
        subject = "New task assigned"
        message = f"Helle {instance.assigned_to}, \n\nA new task has been assigned to you"
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.assigned_to.email],
            fail_silently=False,
        )

# Service gmail handler
@receiver(post_save, sender=Service)
def ServiceGmailHandler(sender, instance, created, **kwargs):
    if created and instance.assigned_to and instance.assigned_to.shift_staffs:
        subject = "New complaint assigned"
        message = f"Hello! {instance.assigned_to.shift_staffs}, \n\nA new complaint has been assigned to you."
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.assigned_to.email],
            fail_silently=False,
        )
