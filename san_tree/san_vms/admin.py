from django.contrib import admin
from .models import *

# Registered models.
admin.site.register(Vehicle)
admin.site.register(Driver)
admin.site.register(Cargo)
admin.site.register(Booking)
admin.site.register(DriverSchedule)
admin.site.register(VehicleMaintenance)
