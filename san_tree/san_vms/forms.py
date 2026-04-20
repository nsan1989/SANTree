from django import forms

from .models import *


# Vehicle form.
class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = "__all__"
        widgets = {
            "maintenance_due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        maintenance_due_date = cleaned_data.get("maintenance_due_date")

        if status == "UNDER_REPAIR" and not maintenance_due_date:
            raise forms.ValidationError(
                "Maintenance due date is required when vehicle is under repair."
            )
        return cleaned_data


# Driver form.
class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


# Booking form.
class BookingForm(forms.ModelForm):

    pickup_time = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
    )

    drop_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
    )

    class Meta:
        model = Booking
        fields = [
            "booking_type",
            "priority",
            "pickup_location",
            "drop_location",
            "pickup_time",
            "drop_time",
            "passengers",
            "description",
            "is_recurring",
            "recurrence_pattern",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pickup_time"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["drop_time"].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean(self):
        cleaned_data = super().clean()
        booking_type = cleaned_data.get("booking_type")
        priority = cleaned_data.get("priority")
        pickup = cleaned_data.get("pickup_location")
        drop = cleaned_data.get("drop_location")
        pickup_time = cleaned_data.get("pickup_time")
        drop_time = cleaned_data.get("drop_time")

        if booking_type == BookingTypes.PICKUP and not pickup:
            raise forms.ValidationError("Pickup location is required.")

        if (
            booking_type in [BookingTypes.DROP, BookingTypes.DROP_AND_PICKUP]
            and not drop
        ):
            raise forms.ValidationError("Drop location is required.")

        if pickup_time and drop_time and drop_time < pickup_time:
            raise forms.ValidationError("Drop time cannot be earlier than pickup time.")

        return cleaned_data


# Shift Schedule Form.
class DriverScheduleForm(forms.ModelForm):
    class Meta:
        model = DriverSchedule
        fields = [
            "shift_type",
            "shift_staffs",
            "start_time",
            "end_time",
        ]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(DriverScheduleForm, self).__init__(*args, **kwargs)

        self.fields["shift_type"].required = True

        self.fields["shift_staffs"].required = True

        self.fields["start_time"].required = True

        self.fields["end_time"].required = True

        # Filter based on current user's department
        if user and hasattr(user, "department") and user.department:
            department = user.department

            self.fields["shift_staffs"].queryset = Driver.objects.filter(
                user__department=department, user__role="User"
            )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        if start and end:
            tz = timezone.get_current_timezone()
            print(tz)
            if timezone.is_naive(start):
                start = timezone.make_aware(start, timezone=tz)
                print("Start (aware):", start)
            if timezone.is_naive(end):
                end = timezone.make_aware(end, timezone=tz)
                print("End (aware):", end)
            cleaned_data["start_time"] = start
            cleaned_data["end_time"] = end

            if start and end and start >= end:
                self.add_error("end_time", "End time must be after start time.")


# Shift Edit Form.
class ShiftEditForm(forms.ModelForm):
    class Meta:
        model = DriverSchedule
        fields = [
            "shift_type",
            "shift_staffs",
            "start_time",
            "end_time",
        ]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(ShiftEditForm, self).__init__(*args, **kwargs)

        self.fields["shift_type"].required = True

        self.fields["shift_staffs"].required = True

        self.fields["start_time"].required = True

        self.fields["end_time"].required = True

        # Filter based on current user's department
        if user and hasattr(user, "department") and user.department:
            department = user.department

            self.fields["shift_staffs"].queryset = Driver.objects.filter(
                user__department=department, role="User"
            )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        if start and end and start >= end:
            self.add_error("end_time", "End time must be after start time.")
