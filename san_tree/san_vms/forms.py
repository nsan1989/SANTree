from .models import *
from django import forms

# Vehicle form.
class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'
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
        fields = '__all__'
        widgets = {
            "shift_start": forms.TimeInput(attrs={"type": "time"}),
            "shift_end": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        shift_start = cleaned_data.get("shift_start")
        shift_end = cleaned_data.get("shift_end")

        if shift_start and shift_end and shift_start >= shift_end:
            raise forms.ValidationError(
                "Shift start time must be before shift end time."
            )
        return cleaned_data
    
# Booking form.
class BookingForm(forms.ModelForm):

    pickup_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
    )

    drop_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
    )

    class Meta:
        model = Booking
        fields = [
            'booking_type',
            'priority',
            'pickup_location',
            'drop_location',
            'pickup_time',
            'drop_time',
            'cargo'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pickup_time'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['drop_time'].input_formats = ['%Y-%m-%dT%H:%M']

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

        if booking_type in [
            BookingTypes.DROP,
            BookingTypes.DROP_AND_PICKUP
        ] and not drop:
            raise forms.ValidationError("Drop location is required.")

        # Optional but recommended
        if pickup_time and drop_time and drop_time < pickup_time:
            raise forms.ValidationError(
                "Drop time cannot be earlier than pickup time."
            )

        return cleaned_data

