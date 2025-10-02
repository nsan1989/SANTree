from django import forms
from accounts.models import Departments, Location
from san_cms.models import ComplaintType
from san_tms.models import TasksTypes
from san_srm.models import ServiceTypes, Blocks
from .models import *

# Add Department Form.
class AddDepartmentForm(forms.ModelForm):
    class Meta:
        model = Departments
        fields = ['name']

# Add Complaint Type.
class AddComplaintType(forms.ModelForm):
    class Meta:
        model = ComplaintType
        fields = ['name', 'department']
        
# Add Tasks Type.
class AddTaskType(forms.ModelForm):
    class Meta:
        model = TasksTypes
        fields = ['name', 'department']

# Add Location Form.
class AddLocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name']

# Add Service Type Form.
class AddServiceTypeForm(forms.ModelForm):
    class Meta:
        model = ServiceTypes
        fields = ['name', 'department']

# Add Block Form.
class AddBlockForm(forms.ModelForm):
    class Meta:
        model = Blocks
        fields = ['name']
