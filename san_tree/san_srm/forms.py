from django import forms
from .models import *
from accounts.models import CustomUsers

# Requested Service Form.
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'service_type',
            'service_block',
            'from_location',
            'to_location',
            'priority'
        ]
        labels = {
            'service_type': 'Service'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ServiceForm, self).__init__(*args, **kwargs)

        self.fields['service_type'].required = True

        self.fields['service_block'].required = True

        self.fields['from_location'].required = True

        self.fields['to_location'].required = True

# Generated Service Form.
class ServiceGenerateForm(forms.ModelForm):
    class Meta:
        model = GenerateService
        fields = [
            'service_type',
            'from_location',
            'to_location',
            'attachment'
        ]
        labels = {
            'service_type': 'Service'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ServiceGenerateForm, self).__init__(*args, **kwargs)

        self.fields['service_type'].required = True

        self.fields['from_location'].required = True

        self.fields['to_location'].required = True

        self.fields['attachment'].required = True

# Service Remarks.
class ServiceRemarkForm(forms.ModelForm):
    class Meta:
        model = ServiceRemarks
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
                self.fields['service'].queryset = Service.objects.filter(department=user_department)
            else:
                self.fields['service'].queryset = Service.objects.none()

# Shift Schedule Form.
class ShiftScheduleForm(forms.ModelForm):
    class Meta:
        model = ShiftSchedule
        fields = [
            'shift_type',
            'shift_block',
            'shift_staffs',
            'start_time',
            'end_time',
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ShiftScheduleForm, self).__init__(*args, **kwargs)

        self.fields['shift_type'].required = True

        self.fields['shift_block'].required = True

        self.fields['shift_staffs'].required = True

        self.fields['start_time'].required = True

        self.fields['end_time'].required = True

        # Filter based on current user's department
        if user and hasattr(user, 'department') and user.department:
            department = user.department

            self.fields['shift_staffs'].queryset = CustomUsers.objects.filter(
                department=department,
                role='User'
            )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')

        if start and end:
            tz = timezone.get_current_timezone()
            print(tz)
            if timezone.is_naive(start):
                start = timezone.make_aware(start, timezone=tz)
                print("Start (aware):", start)
            if timezone.is_naive(end):
                end = timezone.make_aware(end, timezone=tz)
                print("End (aware):", end)
            cleaned_data['start_time'] = start
            cleaned_data['end_time'] = end
        
            if start and end and start >= end:
                self.add_error('end_time', 'End time must be after start time.')

# Shift Edit Form.
class ShiftEditForm(forms.ModelForm):
    class Meta:
        model = ShiftSchedule
        fields = [
            'shift_type',
            'shift_block',
            'shift_staffs',
            'start_time',
            'end_time',
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ShiftEditForm, self).__init__(*args, **kwargs)

        self.fields['shift_type'].required = True

        self.fields['shift_block'].required = True

        self.fields['shift_staffs'].required = True

        self.fields['start_time'].required = True

        self.fields['end_time'].required = True

        # Filter based on current user's department
        if user and hasattr(user, 'department') and user.department:
            department = user.department

            self.fields['shift_staffs'].queryset = CustomUsers.objects.filter(
                department=department,
                role='User'
            )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        
        if start and end and start >= end:
            self.add_error('end_time', 'End time must be after start time.')
            