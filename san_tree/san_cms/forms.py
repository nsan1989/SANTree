from django import forms
from .models import Complaint, ComplaintType, ReassignedComplaint, ComplaintRemarks, ReassignDepartment
from accounts.models import CustomUsers, Departments
from django.db.models import Count, Q

# Complaint Form.
class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['department', 'complaint_type', 'location', 'priority', 'attachment', 'description']
        labels = {
            'department': 'Concern Department'
        }

        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3, 
                'cols': 20  
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ComplaintForm, self).__init__(*args, **kwargs)

        self.fields['complaint_type'].required = True

        self.fields['location'].required = True

        self.fields['description'].required = False

        self.fields['attachment'].required = False

        user_department = getattr(user, 'department', None) if user else None

        department_qs = Departments.objects.annotate(
            valid_complaint_type_count=Count(
                'complaint_types',
                filter=~Q(complaint_types__name__iexact='Others')
            )
        ).filter(valid_complaint_type_count__gt=0)

        if user_department:
            department_qs = department_qs.exclude(id=user_department.id)
        
        self.fields['department'].queryset = department_qs


        self.fields['complaint_type'].queryset = ComplaintType.objects.none()

        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['complaint_type'].queryset = ComplaintType.objects.filter(department_id=department_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.department:
            self.fields['complaint_type'].queryset = ComplaintType.objects.filter(department=self.instance.department)

# Reassigned Form
class ReassignedForm(forms.ModelForm):

    class Meta:
        model = ReassignedComplaint
        fields = ['reassigned_to', 'duration']
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.request:
            user_department = getattr(self.request.user, 'department', None)

            if user_department:
                self.fields['reassigned_to'].queryset = CustomUsers.objects.filter(
                    Q(department=user_department) &
                    Q(status='vacant')
                    ).exclude(id=self.request.user.id)
            else:
                self.fields['reassigned_to'].queryset = CustomUsers.objects.none()

# Reassigned Department Form
class ReassignedDepartmentForm(forms.ModelForm):
    class Meta:
        model = ReassignDepartment
        fields = ['reassign_to']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ReassignedDepartmentForm, self).__init__(*args, **kwargs)

        user_department = getattr(user, 'department', None) if user else None

        department_qs = Departments.objects.all()

        if user_department:
            department_qs = department_qs.exclude(id=user_department.id)

        self.fields['reassign_to'].queryset = department_qs

# Remark Form.
class RemarksForm(forms.ModelForm):
    class Meta:
        model = ComplaintRemarks
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
