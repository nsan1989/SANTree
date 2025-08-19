from django.contrib import admin
from .models import *

# Registered Models.
admin.site.register(TasksTypes)
admin.site.register(Tasks)
admin.site.register(TasksRemarks)
