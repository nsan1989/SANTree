from datetime import timedelta

from django.db.models.signals import post_save
from django.test import TestCase
from django.utils import timezone

from accounts.models import ADMIN, USER, CustomUsers, Departments, Location
from san_srm.models import Blocks, Service, ServiceRequestQueue, ServiceTypes, ShiftSchedule
from san_srm.signals import service_notification
from san_srm.views import free_up_staff


class SRMServiceFlowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        post_save.disconnect(service_notification, sender=Service)

    @classmethod
    def tearDownClass(cls):
        post_save.connect(service_notification, sender=Service)
        super().tearDownClass()

    def setUp(self):
        self.gda = Departments.objects.create(name="GDA")
        self.other_dept = Departments.objects.create(name="Facilities")

        self.block = Blocks.objects.create(name="A Block")
        self.from_location = Location.objects.create(name="Ward 1")
        self.to_location = Location.objects.create(name="ICU")
        self.service_type = ServiceTypes.objects.create(
            name="Patient Transfer", department=self.gda
        )

        self.staff = CustomUsers.objects.create_user(
            username="gda_staff",
            password="pass1234",
            role=USER,
            status="engaged",
            department=self.gda,
            employee_id="EMP1001",
            phone_number="9000000001",
        )
        self.requester = CustomUsers.objects.create_user(
            username="requester",
            password="pass1234",
            role=ADMIN,
            status="vacant",
            department=self.other_dept,
            employee_id="EMP1002",
            phone_number="9000000002",
        )

        now = timezone.now()
        self.shift = ShiftSchedule.objects.create(
            shift_type="morning",
            shift_block=self.block,
            shift_staffs=self.staff,
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=3),
            status="ongoing",
            is_active=True,
        )

    def test_service_in_progress_sets_started_at_and_deadline(self):
        service = Service.objects.create(
            service_type=self.service_type,
            request_type="High",
            service_block=self.block,
            from_location=self.from_location,
            to_location=self.to_location,
            status="Open",
            assigned_to=self.shift,
            created_by=self.requester,
        )

        service.status = "In Progress"
        before = timezone.now()
        service.save()
        service.refresh_from_db()

        self.assertIsNotNone(service.started_at)
        self.assertIsNotNone(service.deadline)
        self.assertGreaterEqual(service.started_at, before - timedelta(seconds=2))
        self.assertAlmostEqual(
            (service.deadline - service.started_at).total_seconds(),
            15 * 60,
            delta=2,
        )

    def test_free_up_staff_marks_expired_service_pending_and_staff_vacant(self):
        service = Service.objects.create(
            service_type=self.service_type,
            request_type="High",
            service_block=self.block,
            from_location=self.from_location,
            to_location=self.to_location,
            status="In Progress",
            assigned_to=self.shift,
            created_by=self.requester,
            deadline=timezone.now() - timedelta(minutes=1),
        )

        free_up_staff()

        service.refresh_from_db()
        self.staff.refresh_from_db()

        self.assertEqual(service.status, "Pending")
        self.assertIsNone(service.assigned_to)
        self.assertEqual(service.handled_by_id, self.staff.id)
        self.assertEqual(self.staff.status, "vacant")

    def test_free_up_staff_reassigns_waiting_queue_to_freed_staff(self):
        expired_service = Service.objects.create(
            service_type=self.service_type,
            request_type="Critical",
            service_block=self.block,
            from_location=self.from_location,
            to_location=self.to_location,
            status="In Progress",
            assigned_to=self.shift,
            created_by=self.requester,
            deadline=timezone.now() - timedelta(minutes=1),
        )

        waiting_service = Service.objects.create(
            service_type=self.service_type,
            request_type="Low",
            service_block=self.block,
            from_location=self.from_location,
            to_location=self.to_location,
            status="Waiting",
            created_by=self.requester,
        )
        ServiceRequestQueue.objects.create(service_request=waiting_service)

        free_up_staff()

        expired_service.refresh_from_db()
        waiting_service.refresh_from_db()
        self.staff.refresh_from_db()

        self.assertEqual(expired_service.status, "Pending")
        self.assertEqual(waiting_service.status, "Open")
        self.assertEqual(waiting_service.assigned_to_id, self.shift.id)
        self.assertEqual(self.staff.status, "vacant")
        self.assertFalse(
            ServiceRequestQueue.objects.filter(service_request=waiting_service).exists()
        )
