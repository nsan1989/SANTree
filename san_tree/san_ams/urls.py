from django.urls import path
from .views import *

app_name = "ams"

urlpatterns = [
    path('admin/add_license/', AddLicenseView, name='add_license'),
    path('admin/add_accessory_category/', AddAccessoryCategoryView, name='add_accessory_category'),
    path('admin/add_accessory/', AddAccessoryView, name='add_accessory'),
    path('admin/add_consumable_category/', AddConsumableCategoryView, name='add_consumable_category'),
    path('admin/add_consumable/', AddConsumableView, name='add_consumable'),
    path('admin/add_component_category/', AddComponentCategoryView, name='add_component_category'),
    path('admin/add_component/', AddComponentView, name='add_component'),
    path('admin/add_asset_category/', AddAssetCategoryView, name='add_asset_category'),
    path('admin/add_asset/', AddAssetView, name='add_asset'),
    path('asset_pie_chart/', AssetPieChart, name='asset_chart'),
    path('staff/dashboard/', StaffDashboardView, name='staff_dashboard'),
    path('admin/dashboard/', AdminDashboardView, name='admin_dashboard'),
    path('admin/assets/', AssetView, name='admin_assets'),
    path('admin/assets/assign_asset/<int:asset_id>/', AssignedAssetView, name='admin_assigned_assets'),
    path('admin/assets/asset_detail/<int:asset_id>/', AssetDetailView, name='admin_asset_detail'),
    path('staff/assets/', AssetView, name='staff_assets'),
    path('staff/assets/assign_asset/<int:asset_id>/', AssignedAssetView, name='staff_assigned_assets'),
    path('staff/assets/asset_detail/<int:asset_id>/', AssetDetailView, name='staff_asset_detail'),
    path('admin/licenses/', LicenseView, name='all_licenses'),
    path('admin/licenses/assign_license/', AssignedLicensesView, name='assigned_license'),
    path('admin/licenses/license_detail/<int:license_id>/', LicenseDetailView, name='license_detail'),
    path('admin/accessories/', AccessoriesView, name='admin_accessories'),
    path('staff/accessories/', AccessoriesView, name='staff_accessories'),
    path('admin/consumables/', ConsumablesView, name='admin_consumables'),
    path('staff/consumables/', ConsumablesView, name='staff_consumables'),
    path('admin/components/', ComponentsView, name='admin_components'),
    path('staff/components/', ComponentsView, name='staff_components'),
    path('admin/asset_users/', AssetUsersView, name='admin_asset_users'),
    path('staff/asset_users/', AssetUsersView, name='staff_asset_users'),
    path('asset-requests/', AssetRequestView, name='asset_requests'),
    path('admin/asset_requests/', AllAssetsRequestsView, name='admin_asset_requests'),
]
