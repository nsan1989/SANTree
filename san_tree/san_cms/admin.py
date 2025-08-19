from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(ComplaintType)
admin.site.register(Complaint)
admin.site.register(ComplaintHistory)
admin.site.register(ReassignedComplaint)
admin.site.register(ComplaintRemarks)
