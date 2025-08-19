from django import forms
from .models import Tasks, TasksRemarks, Departments, TasksTypes
from accounts.models import CustomUsers

# Tasks Form.
class TasksForm(forms.ModelForm):
    class Meta:
        model = Tasks
        fields = ['department', 'tasks_types', 'location', 'assigned_to', 'attachment']
        labels = {
            'tasks_types': 'Tasks',
            'assigned_to': 'Assigned To'
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super(TasksForm, self).__init__(*args, **kwargs)

        if user and hasattr(user, 'department') and user.department:
            department = user.department
            self.fields['department'].initial = department
            self.fields['department'].queryset = Departments.objects.filter(id=department.id)
            self.fields['department'].disabled = True 
            self.fields['attachment'].required = False

            # Filter related fields based on user's department
            self.fields['tasks_types'].queryset = TasksTypes.objects.filter(
                department=department
            ).exclude(name__iexact='Others').order_by('name')

            self.fields['assigned_to'].queryset = CustomUsers.objects.filter(
                department=department,
                role='User'
            )

# Tasks Remark Form.
class RemarkForm(forms.ModelForm):
    class Meta:
        model = TasksRemarks
        fields = ['remarks', 'attachment']

        widgets = {
            'remarks': forms.Textarea(attrs={
                'rows': 3,
                'cols': 20
            }),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        self.fields['attachment'].required = False

        if self.request:
            user_department = getattr(self.request.user, 'department', None)

            if user_department:
                self.fields['tasks'].queryset = Tasks.objects.filter(department=user_department)
            else:
                self.fields['tasks'].queryset = Tasks.objects.none()
