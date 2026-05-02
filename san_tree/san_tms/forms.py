from django import forms

from accounts.models import CustomUsers, Departments

from .models import (
    Departments,
    TaskHandover,
    Tasks,
    TasksRemarks,
    TasksTypes,
    TaskChecklist,
)


# Tasks Form.
class TasksForm(forms.ModelForm):
    class Meta:
        model = Tasks
        fields = [
            "department",
            "tasks_types",
            "task_frequency",
            "start_date",
            "location",
            "assigned_to",
            "attachment",
        ]
        labels = {
            "tasks_types": "Tasks",
            "task_frequency": "Frequency",
            "start_date": "Start Date",
            "assigned_to": "Assigned To",
        }
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super(TasksForm, self).__init__(*args, **kwargs)

        if user and hasattr(user, "department") and user.department:
            department = user.department
            self.fields["department"].initial = department
            self.fields["department"].queryset = Departments.objects.filter(
                id=department.id
            )
            self.fields["department"].disabled = True
            self.fields["location"].required = False
            self.fields["attachment"].required = False

            # Filter related fields based on user's department
            self.fields["tasks_types"].queryset = (
                TasksTypes.objects.filter(department=department)
                .exclude(name__iexact="Others")
                .order_by("name")
            )

            self.fields["assigned_to"].queryset = CustomUsers.objects.filter(
                department=department, role="User"
            )


# Tasks Remark Form.
class RemarkForm(forms.ModelForm):
    class Meta:
        model = TasksRemarks
        fields = ["remarks", "attachment"]

        widgets = {
            "remarks": forms.Textarea(attrs={"rows": 3, "cols": 20}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        self.fields["attachment"].required = False

        if self.request:
            user_department = getattr(self.request.user, "department", None)

            if user_department:
                self.fields["tasks"].queryset = Tasks.objects.filter(
                    department=user_department
                )
            else:
                self.fields["tasks"].queryset = Tasks.objects.none()


# Task Handover Form.
class TaskHandoverForm(forms.ModelForm):
    class Meta:
        model = TaskHandover
        fields = ["to_user", "reason"]
        widgets = {
            "reason": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Handover reason"}
            ),
        }

    def __init__(self, *args, task=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["to_user"].queryset = CustomUsers.objects.none()

        if task and task.department_id:
            queryset = CustomUsers.objects.filter(
                department_id=task.department_id, role="User", is_active=True
            )
            if task.assigned_to_id:
                queryset = queryset.exclude(id=task.assigned_to_id)
            self.fields["to_user"].queryset = queryset


# Task Type Form.
class AddTaskType(forms.ModelForm):
    class Meta:
        model = TasksTypes
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)

        if not self.user or not self.user.department:
            raise ValueError("User does not have a department assigned")

        instance.department = self.user.department

        if commit:
            instance.save()

        return instance


# Task Checklist Form.
class AddTaskChecklistForm(forms.ModelForm):
    class Meta:
        model = TaskChecklist
        fields = ["task_type", "name"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)

        if not self.user or not self.user.department:
            raise ValueError("User does not have a department assigned")

        instance.department = self.user.department

        if commit:
            instance.save()

        return instance
