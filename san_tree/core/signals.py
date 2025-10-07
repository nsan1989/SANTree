from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from san_cms.models import Complaint, ReassignedComplaint, ReassignDepartment
from san_tms.models import Tasks
from san_srm.models import Service

# Complaint gmail handler
@receiver(post_save, sender=Complaint)
def ComplaintGmailHandler(sender, instance, created, **kwargs):

    if not created:
        return
    
    assigned_to = getattr(instance, 'assigned_to', None)
    if not assigned_to or not getattr(assigned_to, "cms_assigned_complaints", None):
        return
    
    staff_name = getattr(assigned_to, "username", "Staff Member")
    staff_email = getattr(assigned_to, "email", None)

    if not staff_email:
        return
   
    subject = "New complaint assigned"
    message = (
        f"Hello! {staff_name}, \n\n"
        f"A new complaint has been assigned to you. \n\n"
        f"Complaint Number: {instance.id} \n"
        "Please check your complaint page for more details."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [staff_email],
        fail_silently=False,
    )

# Reassigned to user gmail handler
@receiver(post_save, sender=ReassignedComplaint)
def ReassignedGmailHandler(sender, instance, created, **kwargs):

    if not created:
        return
    
    assigned_to = getattr(instance, 'reassigned_to', None)
    if not assigned_to or not getattr(assigned_to, "reassign_complaints", None):
        return
    
    staff_name = getattr(assigned_to, "username", "Staff Member")
    staff_email = getattr(assigned_to, "email", None)

    if not staff_email:
        return

    subject = "New complaint assigned"
    message = (
        f"Hello! {staff_name}, \n\n"
        f"A new complaint has been assigned to you. \n\n"
        f"Complaint Number: {instance.id} \n"
        "Please check your complaint page for more details."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [staff_email],
        fail_silently=False,
    )

# Reassigned to department gmail handler
@receiver(post_save, sender=ReassignDepartment)
def ReassignDepartmentGmailHandler(sender, instance, created, **kwargs):

    if not created:
        return
    
    assigned_to = getattr(instance, 'reassign_to', None)
    if not assigned_to or not getattr(assigned_to, "reassign_departments", None):
        return
    
    dept_name = getattr(assigned_to, "name", "Department")
    dept_email = getattr(assigned_to, "email", None)

    if not dept_email:
        return

    subject = "New complaint has been reassigned to your department"
    message = (
        f"Hello! {dept_name}, \n\n"
        f"A new complaint has been assigned to you. \n\n"
        f"Complaint Number: {instance.id} \n"
        "Please check your complaint page for more details."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [dept_email],
        fail_silently=False,
    )

# Task gmail handler
@receiver(post_save, sender=Tasks)
def TaskGmailHandler(sender, instance, created, **kwargs):
    if not created:
        return
    
    assigned_to = getattr(instance, 'assigned_to', None)
    if not assigned_to or not getattr(assigned_to, "tms_assigned_tasks", None):
        return
    
    staff_name = getattr(assigned_to, "username", "Staff Member")
    staff_email = getattr(assigned_to, "email", None)

    if not staff_email:
        return

    subject = "New task assigned"
    message = (
        f"Hello! {staff_name}, \n\n"
        f"A new task has been assigned to you. \n\n"
        f"Task Number: {instance.id} \n"
        "Please check your task request page for more details."
    )
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [staff_email],
        fail_silently=False,
    )

# Service gmail handler
@receiver(post_save, sender=Service)
def ServiceGmailHandler(sender, instance, created, **kwargs):

    if not created:
        return
    
    assigned_to = getattr(instance, 'assigned_to', None)
    if not assigned_to or not getattr(assigned_to, "shift_staffs", None):
        return
    
    staff = assigned_to.shift_staffs
    staff_name = getattr(staff, "username", "Staff Member")
    staff_email = getattr(staff, "email", None)

    if not staff_email:
        return

    subject = "New service assigned"
    message = (
        f"Hello! {staff_name}, \n\n"
        f"A new service has been assigned to you. \n\n"
        f"Service Number: {instance.id} \n"
        "Please check your service request page for more details."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [staff_email],
        fail_silently=False,
    )
