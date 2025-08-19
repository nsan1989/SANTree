from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

SUPER_ADMIN = 'Super Admin'
ADMIN = 'Admin'
USER = 'User'

INCHARGE = 'In Charge'
STAFF = 'Staff'

ENGAGED = 'Engaged'
VACANT = 'Vacant'

# Role Choices.
ROLE_CHOICES = (
    (SUPER_ADMIN, 'super admin'),
    (ADMIN, 'admin'),
    (USER, 'user'),
)

# Designation Choices.
DESIGNATION_CHOICES = [
    (INCHARGE, 'incharge'),
    (STAFF, 'staff'),
]

# Status Choices.
STATUS_CHOICES = (
    (ENGAGED, 'engaged'),
    (VACANT, 'vacant'),
)

# Department Model.
class Departments(models.Model):
    name = models.CharField(max_length=100)

    # Method to define string representation of an object.
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Check for duplicate department names (case-insensitive)
        if Departments.objects.filter(name__iexact=self.name).exclude(pk=self.pk).exists():
            raise ValidationError(f"A department with the name '{self.name}' already exists.")
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
    
# Location Model.
class Location(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

# User Model.
class CustomUsers(AbstractUser):
    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default='user')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='vacant', null=True, blank=True)
    department = models.ForeignKey(Departments, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.CharField(max_length=25, choices=DESIGNATION_CHOICES, default='staff')
    employee_id = models.CharField(max_length=20, unique=True, default='EMP_ID')

    def __str__(self):
        # f string is a way to embed expressions inside string literals using curly braces
        return f'{self.username} {self.department}'  
    
    class Meta:
        ordering = ['username']
