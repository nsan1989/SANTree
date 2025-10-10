from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from san_cms.models import Complaint, ReassignedComplaint, ReassignDepartment
from san_tms.models import Tasks
from san_srm.models import Service
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from accounts.models import CustomUsers

# Complaint gmail handler
@receiver(post_save, sender=Complaint)
def ComplaintGmailHandler(sender, instance, created, **kwargs):

    if created and instance.status == 'Waiting':
        department = getattr(instance, 'department', None)
        dept_admins = CustomUsers.objects.filter(department=department, role='Admin', is_active=True)

        for admin in dept_admins:
            admin_name = getattr(admin, "username", "Admin")
            admin_email = getattr(admin, "email", None)

            if not admin_email:
                continue

            subject = "New complaint received"
            message = (
                f"Hello! {admin_name}, \n\n"
                f"A new complaint has been received in your department. \n\n"
                f"Complaint Number: {instance.id} \n"
                "Please check your complaint page for more details."
                "Regards,\n"
                "Team MIS"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [admin_email],
                fail_silently=False,
            )
    elif created and instance.status == 'Open':
        assigned_to = getattr(instance, 'assigned_to', None)
        print(assigned_to)
        staff_name = getattr(assigned_to, "username", "Staff Member")
        print(staff_name)
        staff_email = getattr(assigned_to, "email", None)
        print(staff_email)

        if not staff_email:
            return

        subject = "New complaint assigned"
        message = (
            f"Hello! {staff_name}, \n\n"
            f"A new complaint has been assigned to you. \n\n"
            f"Complaint Number: {instance.id} \n"
            "Please check your complaint page for more details."
            "Regards,\n"
            "Team MIS"
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
        "Regards,\n"
        "Team MIS"
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
        "Regards,\n"
        "Team MIS"
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
        "Regards,\n"
        "Team MIS"
    )
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [staff_email],
        fail_silently=False,
    )

@receiver(pre_save, sender=Service)
def store_previous_assigned_to(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_assigned_to = None
    else:
        try:
            old_instance = Service.objects.get(pk=instance.pk)
            instance._old_assigned_to = old_instance.assigned_to
        except Service.DoesNotExist:
            instance._old_assigned_to = None

# Service gmail handler
@receiver(post_save, sender=Service)
def ServiceGmailHandler(sender, instance, created, **kwargs):

    assigned_to = getattr(instance, 'assigned_to', None)
    old_assigned_to = getattr(instance, '_old_assigned_to', None)

    if created and not assigned_to:
        return

    if not assigned_to or assigned_to == old_assigned_to:
        return

    staff = getattr(assigned_to, "shift_staffs", None)
    if not staff:
        return

    staff_name = getattr(staff, "username", "Staff Member")
    staff_email = getattr(staff, "email", None)

    if not staff_email:
        return

    subject = "New service assigned"
    message = (
        f"Hello {staff_name},\n\n"
        f"A new service has been assigned to you.\n\n"
        f"Service Number: {instance.service_number or instance.id}\n"
        "Please check your service request page for more details.\n\n"
        "Regards,\n"
        "Team MIS"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [staff_email],
        fail_silently=False,
    )
