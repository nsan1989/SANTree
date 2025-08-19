from django.contrib import admin
from .models import *

# Registered Models.
admin.site.register(ServiceTypes)
admin.site.register(Service)
admin.site.register(ServiceRemarks)
