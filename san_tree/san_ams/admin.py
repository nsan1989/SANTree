from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import *


# license model resources.
class LicenseResources(resources.ModelResource):
    models = LicenseModel
    fields = (
        "id",
        "name",
        "manufacturer",
        "product_key",
        "purchase_date",
        "expiry_date",
        "buyer_name",
        "buyer_phone",
        "buyer_email",
        "quantity",
        "cost",
        "is_expire",
        "status",
        "assigned_to",
        "department",
        "location",
        "created_at",
        "updated_at",
    )


# license admin model.
@admin.register(LicenseModel)
class LicenseAdmin(ImportExportModelAdmin):
    resource_class = LicenseResources
    list_display = (
        "name",
        "manufacturer",
        "product_key",
        "purchase_date",
        "expiry_date",
        "buyer_name",
        "buyer_phone",
        "buyer_email",
        "quantity",
        "cost",
        "is_expire",
        "status",
        "assigned_to",
        "department",
        "location",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)


# accessory category model resources.
class AccessoryCategoryResources(resources.ModelResource):
    models = AccessoryCategoryModel
    fields = (
        "id",
        "name",
    )


# accessory category model admin.
@admin.register(AccessoryCategoryModel)
class AccessoryCategoryAdmin(ImportExportModelAdmin):
    resource_class = AccessoryCategoryResources
    list_display = ("name",)
    search_fields = ("name",)


# accessory model resources.
class AccessoryResources(resources.ModelResource):
    models = AccessoryModel
    fields = (
        "id",
        "name",
        "category",
        "model_number",
        "manufacturer",
        "image",
        "purchase_date",
        "cost",
        "quantity",
        "created_at",
        "updated_at",
    )


# accessory model admin.
@admin.register(AccessoryModel)
class AccessoryAdmin(ImportExportModelAdmin):
    resource_class = AccessoryResources
    list_display = (
        "name",
        "category",
        "model_number",
        "manufacturer",
        "image",
        "purchase_date",
        "cost",
        "quantity",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)


# consumable category resources.
class ConsumableResources(resources.ModelResource):
    models = ConsumableCategoryModel
    fields = (
        "id",
        "name",
    )


# consumable category admin
@admin.register(ConsumableCategoryModel)
class ConsumableAdmin(ImportExportModelAdmin):
    resource_class = ConsumableResources
    list_display = ("name",)
    search_fields = ("name",)


# consumable resources.
class ConsumableResources(resources.ModelResource):
    models = ConsumableModel
    fields = (
        "id",
        "name",
        "category",
        "model_number",
        "manufacturer",
        "image",
        "purchase_date",
        "cost",
        "quantity",
        "created_at",
        "updated_at",
    )


# consumable admin.
@admin.register(ConsumableModel)
class ConsumableAdmin(ImportExportModelAdmin):
    resource_class = ConsumableResources
    list_display = (
        "name",
        "category",
        "model_number",
        "manufacturer",
        "image",
        "purchase_date",
        "cost",
        "quantity",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)


# component category resources.
class ComponentCategoryResources(resources.ModelResource):
    models = ComponentCategoryModel
    fields = ("id", "name")


# component category admin.
@admin.register(ComponentCategoryModel)
class ComponentCategoryAdmin(ImportExportModelAdmin):
    resource_class = ComponentCategoryResources
    list_display = ("name",)
    search_fields = ("name",)


# component resources.
class ComponentResources(resources.ModelResource):
    models = ComponentModel
    fields = (
        "id",
        "name",
        "category",
        "image",
        "serial_number",
        "model_number",
        "manufacturer",
        "quantity",
        "cost",
        "purchase_date",
        "created_at",
        "updated_at",
    )


# component admin.
@admin.register(ComponentModel)
class ComponentAdmin(ImportExportModelAdmin):
    resource_class = ComponentResources
    list_display = (
        "name",
        "category",
        "image",
        "serial_number",
        "model_number",
        "manufacturer",
        "quantity",
        "cost",
        "purchase_date",
        "created_at",
        "updated_at",
    )
    search_fields = ("name",)


# asset category resources.
class AssetCategoryResources(resources.ModelResource):
    models = AssetCategoryModel
    fields = ("id", "name")


# asset category admin.
@admin.register(AssetCategoryModel)
class AssetCategoryAdmin(ImportExportModelAdmin):
    resource_class = AssetCategoryResources
    list_display = ("name",)
    search_fields = ("name",)


# asset resources.
class AssetResources(resources.ModelResource):
    models = AssetModel
    fields = "__all__"


# asset admin.
@admin.register(AssetModel)
class AssetAdmin(ImportExportModelAdmin):
    resource_class = AssetResources
    list_display = (
        "id",
        "asset_tag",
        "name",
        "category",
        "manufacturer",
        "model_number",
        "serial_number",
        "image",
        "purchase_date",
        "expiry_date",
        "cost",
        "components",
        "consumables",
        "accessories",
        "licenses",
        "status",
        "handler",
        "created_by",
        "assigned_to",
        "department",
        "location",
        "requestable",
        "created_at",
        "updated_at",
        "is_active",
    )
    search_fields = ("name",)

    def components(self, obj):
        return ", ".join(str(i) for i in obj.asset_component.all()[:3])

    components.short_description = "Components"

    def consumables(self, obj):
        return ", ".join(str(i) for i in obj.asset_consumable.all()[:3])

    consumables.short_description = "Consumables"

    def accessories(self, obj):
        return ", ".join(str(i) for i in obj.asset_accessory.all()[:3])

    accessories.short_description = "Accessories"

    def licenses(self, obj):
        return ", ".join(str(i) for i in obj.asset_license.all()[:3])

    licenses.short_description = "Licenses"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            "asset_component",
            "asset_consumable",
            "asset_accessory",
            "asset_license",
        )


# asset request resources.
class AssetRequestResources(resources.ModelResource):
    models = AssetRequest
    fields = (
        "id",
        "asset",
        "requested_by",
        "requested_to",
        "department",
        "status",
        "remarks",
        "created_at",
    )


# asset admin.
@admin.register(AssetRequest)
class AssetRequestAdmin(ImportExportModelAdmin):
    resource_class = AssetRequestResources
    list_display = (
        "asset",
        "requested_by",
        "requested_to",
        "department",
        "status",
        "remarks",
        "created_at",
    )
    search_fields = ("asset__name",)


# asset last user resources.
class AssetLastUserResources(resources.ModelResource):
    models = AssetLastUser
    fields = (
        "id",
        "asset",
        "user",
        "assigned_at",
        "unassigned_at",
    )


# asset last user admin.
@admin.register(AssetLastUser)
class AssetLastUserAdmin(ImportExportModelAdmin):
    resource_class = AssetLastUserResources
    list_display = (
        "asset",
        "user",
        "assigned_at",
        "unassigned_at",
    )
    search_fields = ("asset__name", "user__username")
