from django.contrib import admin
from .models import *

# Registered Models.
admin.site.register(ServiceTypes)
admin.site.register(Service)
admin.site.register(ServiceRemarks)
admin.site.register(Blocks)
admin.site.register(ServiceLocation)
admin.site.register(ShiftSchedule)
admin.site.register(ServiceRequestQueue)
admin.site.register(GenerateService)
