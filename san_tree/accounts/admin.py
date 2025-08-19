from django.contrib import admin
from .models import Departments, CustomUsers, Location

# Registered models.
admin.site.register(Departments)
admin.site.register(CustomUsers)
admin.site.register(Location)
