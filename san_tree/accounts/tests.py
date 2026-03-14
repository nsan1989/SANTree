from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Departments, Location, CustomUsers


# account models test case.
class DepartmentModelTest(TestCase):

    def setUp(self):
        """
        Runs before each test case
        """
        self.department = Departments.objects.create(name="Patient Care Assistant")
        self.location = Location.objects.create(name="Itocha Block")
        self.user = CustomUsers.objects.create(
            role="User",
            status="vacant",
            department=self.department,
            designation="Staff",
            employee_id="MIS016",
            phone_number="1111111111",
            username="Rahul",
            password="demo@pass",
        )

    def testModelSetup(self):
        """
        Test if model is created successfully
        """
        dept = Departments.objects.get(name="Patient Care Assistant")
        location = Location.objects.get(name="Itocha Block")
        user = CustomUsers.objects.get(username="Rahul")

        self.assertEqual(dept.name, "Patient Care Assistant")
        self.assertEqual(location.name, "Itocha Block")
        self.assertEqual(user.username, "Rahul")

    def testStringRepresentation(self):
        """
        Test __str__ method
        """
        self.assertEqual(str(self.department), "Patient Care Assistant")
        self.assertEqual(str(self.location), "Itocha Block")
        self.assertEqual(str(self.user), "Rahul Patient Care Assistant")

    def testDuplicateNamesCaseInsensitive(self):
        """
        Test duplicate names (case-insensitive)
        """
        with self.assertRaises(ValidationError):
            dept = Departments(name="Patient Care Assistant")
            dept.save()
            loc = Location(name="Itocha Block")
            loc.save()
            user = CustomUsers(username="Rahul")
            user.save()

    def testUpdateNamesWithoutDuplicate(self):
        """
        Updating the same names should not raise ValidationError
        """
        self.department.name = "Patient Care Assistant"
        self.location.name = "Itocha Block"
        self.user.username = "Rahul"

        try:
            self.department.save()
            self.location.save()
            self.user.save()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly!")


"""
    def testDepartmentOrdering(self):
#       Test ordering defined in Meta
        Departments.objects.create(name="Radiology")
        Departments.objects.create(name="Anesthesiology")

        departments = Departments.objects.all()
        names = [dept.name for dept in departments]

        self.assertEqual(names, sorted(names))
"""
