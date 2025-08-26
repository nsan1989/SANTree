from django import forms
from accounts.models import Departments
from san_cms.models import ComplaintType
from san_tms.models import TasksTypes

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
        