from datetime import datetime, time, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomUsers, Departments

from .models import Booking, BookingStatus, BookingTypes, Driver, PatternChoices, Vehicle
from .views import recurring_bookings


class BookingFlowTests(TestCase):
    def setUp(self):
        self.transport_department = Departments.objects.create(name="Transport")
        self.requester_department = Departments.objects.create(name="Radiology")

        self.transport_admin = CustomUsers.objects.create(
            username="transport-admin",
            role="Admin",
            department=self.transport_department,
            designation="Staff",
            employee_id="EMP100",
            phone_number="9000000001",
        )
        self.requester = CustomUsers.objects.create(
            username="requester",
            role="User",
            department=self.requester_department,
            designation="Staff",
            employee_id="EMP101",
            phone_number="9000000002",
        )
        self.driver_user = CustomUsers.objects.create(
            username="driver-user",
            role="User",
            department=self.transport_department,
            designation="Staff",
            employee_id="EMP102",
            phone_number="9000000003",
        )
        self.driver = Driver.objects.create(
            user=self.driver_user,
            license_number="DL-1001",
        )
        self.vehicle = Vehicle.objects.create(
            vehicle_number="AS-01-AB-1234",
            vehicle_type="Van",
            fuel_type="DIESEL",
        )

    def current_local_noon(self):
        return timezone.make_aware(
            datetime.combine(timezone.localdate(), time(hour=12, minute=0))
        )

    def test_normal_booking_request_creates_waiting_booking(self):
        self.client.force_login(self.requester)

        pickup_time = timezone.localtime(timezone.now()) + timedelta(hours=2)
        response = self.client.post(
            reverse("vms:vms_cab_request"),
            data={
                "booking_type": BookingTypes.PICKUP,
                "priority": "NORMAL",
                "pickup_location": "Ward A",
                "drop_location": "",
                "pickup_time": pickup_time.strftime("%Y-%m-%dT%H:%M"),
                "drop_time": "",
                "passengers": 2,
                "description": "Patient transfer",
                "is_recurring": "",
                "recurrence_pattern": PatternChoices.DAILY,
            },
        )

        self.assertRedirects(response, reverse("vms:booking_success"))
        booking = Booking.objects.get()

        self.assertEqual(booking.booked_by, self.requester)
        self.assertEqual(booking.assigned_to, self.transport_admin)
        self.assertEqual(booking.status, BookingStatus.WAITING)
        self.assertFalse(booking.is_recurring)
        self.assertEqual(booking.pickup_location, "Ward A")

    def test_recurring_booking_request_persists_recurrence_fields(self):
        self.client.force_login(self.requester)

        pickup_time = timezone.localtime(timezone.now()) + timedelta(hours=4)
        drop_time = pickup_time + timedelta(hours=1)
        response = self.client.post(
            reverse("vms:vms_cab_request"),
            data={
                "booking_type": BookingTypes.DROP_AND_PICKUP,
                "priority": "HIGH",
                "pickup_location": "OPD",
                "drop_location": "Lab",
                "pickup_time": pickup_time.strftime("%Y-%m-%dT%H:%M"),
                "drop_time": drop_time.strftime("%Y-%m-%dT%H:%M"),
                "passengers": 1,
                "description": "Recurring sample transport",
                "is_recurring": "on",
                "recurrence_pattern": PatternChoices.DAILY,
            },
        )

        self.assertRedirects(response, reverse("vms:booking_success"))
        booking = Booking.objects.get(description="Recurring sample transport")

        self.assertTrue(booking.is_recurring)
        self.assertEqual(booking.recurrence_pattern, PatternChoices.DAILY)
        self.assertEqual(booking.assigned_to, self.transport_admin)
        self.assertEqual(booking.status, BookingStatus.WAITING)

    def test_recurring_bookings_task_rolls_booking_forward_and_clears_assignment(self):
        pickup_time = self.current_local_noon()
        drop_time = pickup_time + timedelta(hours=1)
        booking = Booking.objects.create(
            booking_type=BookingTypes.DROP_AND_PICKUP,
            priority="CRITICAL",
            pickup_location="ICU",
            drop_location="OT",
            pickup_time=pickup_time,
            drop_time=drop_time,
            passengers=1,
            description="Daily recurring emergency support",
            vehicle=self.vehicle,
            driver=self.driver,
            booked_by=self.requester,
            assigned_to=self.driver_user,
            is_recurring=True,
            recurrence_pattern=PatternChoices.DAILY,
            status=BookingStatus.CONFIRMED,
        )

        recurring_bookings()
        booking.refresh_from_db()

        self.assertEqual(booking.pickup_time, pickup_time + timedelta(days=1))
        self.assertEqual(booking.drop_time, drop_time + timedelta(days=1))
        self.assertEqual(booking.status, BookingStatus.WAITING)
        self.assertIsNone(booking.vehicle)
        self.assertIsNone(booking.driver)

    def test_recurring_bookings_task_ignores_non_recurring_bookings(self):
        pickup_time = self.current_local_noon()
        booking = Booking.objects.create(
            booking_type=BookingTypes.PICKUP,
            priority="NORMAL",
            pickup_location="Reception",
            drop_location="",
            pickup_time=pickup_time,
            passengers=1,
            description="One-off visitor pickup",
            booked_by=self.requester,
            assigned_to=self.transport_admin,
            is_recurring=False,
            status=BookingStatus.WAITING,
        )

        recurring_bookings()
        booking.refresh_from_db()

        self.assertEqual(booking.pickup_time, pickup_time)
        self.assertEqual(booking.status, BookingStatus.WAITING)
