from django import forms
from django.db.models import Count, Q

from accounts.models import CustomUsers, Departments

from .models import (
    Facility,
    Block,
    Location,
    Complaint,
    ComplaintRemarks,
    ComplaintType,
    ReassignDepartment,
    ReassignedComplaint,
)


# Complaint Form.
class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            "department",
            "complaint_type",
            "facility",
            "block",
            "location",
            "priority",
            "attachment",
            "description",
        ]
        labels = {"department": "Concern Department"}

        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "cols": 20}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["complaint_type"].required = True

        self.fields["facility"].required = True

        self.fields["block"].required = True

        self.fields["location"].required = True

        self.fields["description"].required = False

        self.fields["attachment"].required = False

        user_department = getattr(user, "department", None) if user else None

        department_qs = Departments.objects.filter(
            complaint_types__isnull=False
        ).distinct()

        if user_department:
            department_qs = department_qs.exclude(id=user_department.id)

        self.fields["department"].queryset = department_qs
        self.fields["facility"].queryset = Facility.objects.filter(
            is_active=True
        ).order_by("name")

        self.fields["complaint_type"].queryset = ComplaintType.objects.none()
        self.fields["block"].queryset = Block.objects.none()
        self.fields["location"].queryset = Location.objects.none()

        department_id = self.data.get("department")

        if not department_id and self.instance.pk:
            department_id = self.instance.department_id

        if department_id:
            self.fields["complaint_type"].queryset = ComplaintType.objects.filter(
                department_id=department_id
            ).order_by("name")

        facility_id = self.data.get("facility")

        if not facility_id and self.instance.pk:
            facility_id = self.instance.facility_id

        if facility_id:
            self.fields["block"].queryset = Block.objects.filter(
                facility_id=facility_id
            ).order_by("name")

        block_id = self.data.get("block")

        if not block_id and self.instance.pk:
            block_id = self.instance.block_id

        if block_id:
            self.fields["location"].queryset = Location.objects.filter(
                block_id=block_id
            ).order_by("name")


# Reassigned Form
class ReassignedForm(forms.ModelForm):

    class Meta:
        model = ReassignedComplaint
        fields = ["reassigned_to", "duration", "message"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        if self.request:
            user_department = getattr(self.request.user, "department", None)

            if user_department:
                self.fields["reassigned_to"].queryset = CustomUsers.objects.filter(
                    Q(department=user_department) & Q(status="vacant")
                ).exclude(id=self.request.user.id)
            else:
                self.fields["reassigned_to"].queryset = CustomUsers.objects.none()


# Reassigned Department Form
class ReassignedDepartmentForm(forms.ModelForm):
    class Meta:
        model = ReassignDepartment
        fields = ["reassign_to", "reason"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(ReassignedDepartmentForm, self).__init__(*args, **kwargs)

        user_department = getattr(user, "department", None) if user else None

        department_qs = Departments.objects.all()

        if user_department:
            department_qs = department_qs.exclude(id=user_department.id)

        self.fields["reassign_to"].queryset = department_qs


# Remark Form.
class RemarksForm(forms.ModelForm):
    class Meta:
        model = ComplaintRemarks
        fields = ["remarks", "attachment"]

        widgets = {
            "remarks": forms.Textarea(attrs={"rows": 3, "cols": 20}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        self.fields["attachment"].required = False
