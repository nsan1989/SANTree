from django.urls import path
from .views import *

app_name = "ams"

urlpatterns = [
    path('staff/dashboard/', StaffDashboardView, name='staff_dashboard'),
    path('admin/dashboard/', AdminDashboardView, name='admin_dashboard'),
    path('licenses/', LicenseView, name='all_licenses'),
    path('admin/accessories/', AccessoriesView, name='admin_accessories'),
    path('staff/accessories/', AccessoriesView, name='staff_accessories'),
    path('admin/consumables/', ConsumablesView, name='admin_consumables'),
    path('staff/consumables/', ConsumablesView, name='staff_consumables'),
    path('admin/components/', ComponentsView, name='admin_components'),
    path('staff/components/', ComponentsView, name='staff_components'),
]
