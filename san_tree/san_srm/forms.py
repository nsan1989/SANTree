from django import forms
from .models import Service, ServiceRemarks, ServiceTypes
from accounts.models import CustomUsers

# Service Form.
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            'service_type',
            'location',
        ]
        labels = {
            'service_type': 'Service'
        }

# Service Remarks.
class ServiceRemark(forms.ModelForm):
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
