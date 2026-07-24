import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.test import TransactionTestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.db import transaction, connection

from accounts.models import ADMIN, USER, CustomUsers, Departments, Location
from san_srm.models import (
    Blocks,
    Service,
    ServiceRequestQueue,
    ServiceTypes,
    ShiftSchedule,
)
from san_srm.views import assign_service_from_queue


class ServiceViewConcurrencyTests(TransactionTestCase):
    """
    Tests for race conditions in the ServiceView.
    """

    allow_database_queries = True

    def setUp(self):
        self.gda_dept = Departments.objects.create(name="GDA")
        self.requester_dept = Departments.objects.create(name="Nursing")
        self.block = Blocks.objects.create(name="Concurrency Test Block")
        self.from_location = Location.objects.create(name="ER")
        self.to_location = Location.objects.create(name="Ward 5")
        self.service_type = ServiceTypes.objects.create(
            name="Concurrent Patient Transport", department=self.gda_dept
        )

        self.requester = CustomUsers.objects.create_user(
            username="concurrency_requester",
            password="password",
            role=ADMIN,
            department=self.requester_dept,
            employee_id="EMP-C-REQ",
        )

        # Set up a single vacant staff member
        self.staff_user = CustomUsers.objects.create_user(
            username="concurrent_staff_1",
            password="password",
            role=USER,
            department=self.gda_dept,
            status="vacant",
            employee_id="EMP-C-1",
        )

        now = timezone.now()
        self.shift = ShiftSchedule.objects.create(
            shift_type="day",
            shift_block=self.block,
            shift_staffs=self.staff_user,
            start_time=now - timedelta(hours=4),
            end_time=now + timedelta(hours=4),
            status="ongoing",
            is_active=True,
        )

    def _make_request(self, request_num):
        """Helper function to make a POST request to ServiceView."""
        client = Client()
        client.login(username="concurrency_requester", password="password")
        service_data = {
            "service_type": self.service_type.id,
            "request_type": "Normal",
            "service_block": self.block.id,
            "from_location": self.from_location.id,
            "to_location": self.to_location.id,
            "UHID": f"C-UHID-{request_num}",
            "description": f"Concurrent test service {request_num}",
        }
        response = client.post(reverse("srm:admin_request_service"), service_data)
        return response

    def test_service_view_race_condition_leads_to_waiting(self):
        """
        Tests for a race condition in ServiceView where a service might be put
        into the Waiting state even if a vacant staff member was available at the
        start of the request. With two concurrent requests and one staff member,
        one service should be assigned and the other should go to the waiting queue.
        """
        num_requests = 2

        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [
                executor.submit(self._make_request, i) for i in range(num_requests)
            ]
            # Wait for all requests to complete
            for future in futures:
                future.result()

        self.assertEqual(Service.objects.count(), 2)

        # One service should be 'Open' and assigned, the other should be 'Waiting'
        self.assertEqual(Service.objects.filter(status="Open").count(), 1)
        self.assertEqual(Service.objects.filter(status="Waiting").count(), 1)

        # The 'Waiting' service should be in the queue
        self.assertEqual(ServiceRequestQueue.objects.count(), 1)
        self.assertEqual(
            ServiceRequestQueue.objects.first().service_request,
            Service.objects.get(status="Waiting"),
        )

        # The 'Open' service should be assigned to the single available shift
        self.assertEqual(Service.objects.get(status="Open").assigned_to, self.shift)

    def test_high_load_with_limited_staff(self):
        """
        Tests ServiceView under high load with more requests than available staff.
        100 requests for a block with only 7 staff members.
        """
        # 1. Add 6 more staff members and their shifts to reach a total of 7
        num_staff = 7
        now = timezone.now()

        for i in range(1, num_staff):  # setUp already created one staff
            staff = CustomUsers.objects.create_user(
                username=f"concurrent_staff_{i + 1}",
                password="password",
                role=USER,
                department=self.gda_dept,
                status="vacant",
                employee_id=f"EMP-C-{i + 1}",
            )
            ShiftSchedule.objects.create(
                shift_type="day",
                shift_block=self.block,
                shift_staffs=staff,
                start_time=now - timedelta(hours=4),
                end_time=now + timedelta(hours=4),
                status="ongoing",
                is_active=True,
            )

        self.assertEqual(
            CustomUsers.objects.filter(department=self.gda_dept, role=USER).count(),
            num_staff,
        )
        self.assertEqual(
            ShiftSchedule.objects.filter(shift_block=self.block).count(), num_staff
        )

        # 2. Send 100 concurrent requests
        num_requests = 100
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(self._make_request, i) for i in range(num_requests)
            ]
            for future in as_completed(futures):
                future.result()

        # 3. Assert the final state
        self.assertEqual(Service.objects.count(), num_requests)

        self.assertEqual(Service.objects.filter(status="Open").count(), num_staff)
        self.assertEqual(
            Service.objects.filter(status="Waiting").count(), num_requests - num_staff
        )
        self.assertEqual(ServiceRequestQueue.objects.count(), num_requests - num_staff)

        open_services = Service.objects.filter(status="Open")
        assigned_shift_ids = {s.assigned_to.id for s in open_services}
        self.assertEqual(len(assigned_shift_ids), num_staff)

        engaged_staff_count = CustomUsers.objects.filter(
            id__in=ShiftSchedule.objects.filter(id__in=assigned_shift_ids).values(
                "shift_staffs_id"
            ),
            status="engaged",
        ).count()
        self.assertEqual(engaged_staff_count, num_staff)

    def test_service_waits_if_staff_is_in_uncommitted_transaction(self):
        """
        Tests that a new service correctly goes to Waiting if the only
        available staff member is being freed in a transaction that has not
        yet committed. It then verifies the queue logic picks up the service.
        """
        # 1. Create a second staff member and an open service assigned to them.
        staff_2 = CustomUsers.objects.create_user(
            username="concurrent_staff_2",
            password="password",
            role=USER,
            department=self.gda_dept,
            status="engaged",  # Start as engaged
            employee_id="EMP-C-2",
        )
        shift_2 = ShiftSchedule.objects.create(
            shift_type="day",
            shift_block=self.block,
            shift_staffs=staff_2,
            start_time=timezone.now() - timedelta(hours=4),
            end_time=timezone.now() + timedelta(hours=4),
            status="ongoing",
            is_active=True,
        )
        service_to_complete = Service.objects.create(
            service_type=self.service_type,
            request_type="Normal",
            service_block=self.block,
            from_location=self.from_location,
            to_location=self.to_location,
            UHID="C-UHID-COMPLETE",
            created_by=self.requester,
            assigned_to=shift_2,
            status="In Progress",
        )

        # Make the primary staff member from setUp also busy
        self.staff_user.status = "engaged"
        self.staff_user.save()

        t1_started_transaction = threading.Event()
        t1_finished_work = threading.Event()

        def complete_service_slowly():
            # This runs in a separate thread, simulating a concurrent operation.
            # It gets its own database connection.
            with transaction.atomic():
                staff_obj = CustomUsers.objects.get(pk=staff_2.pk)
                staff_obj.status = "vacant"
                staff_obj.save(update_fields=["status"])

                service_obj = Service.objects.get(pk=service_to_complete.pk)
                service_obj.status = "Completed"
                service_obj.completed_at = timezone.now()
                service_obj.save(update_fields=["status", "completed_at"])

                t1_started_transaction.set()
                t1_finished_work.wait(timeout=2)
            # Transaction commits here

        completion_thread = threading.Thread(target=complete_service_slowly)
        completion_thread.start()

        t1_started_transaction.wait(timeout=2)

        # At this point, staff_2 is 'vacant' in an uncommitted transaction.
        # This request should NOT see staff_2 as vacant and will go to Waiting.
        self._make_request(99)

        t1_finished_work.set()
        completion_thread.join(timeout=2)

        # The new service should be in the 'Waiting' state.
        self.assertEqual(
            Service.objects.filter(UHID="C-UHID-99").first().status, "Waiting"
        )

        # The service should now be 'Open' and assigned to staff_2's shift.
        waiting_service = Service.objects.get(UHID="C-UHID-99")
        waiting_service.refresh_from_db()
        self.assertEqual(waiting_service.status, "Open")
        self.assertEqual(waiting_service.assigned_to, shift_2)
        self.assertEqual(ServiceRequestQueue.objects.count(), 0)

        staff_2.refresh_from_db()
        self.assertEqual(staff_2.status, "engaged")
