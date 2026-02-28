from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(LicenseModel)
admin.site.register(AccessoryCategoryModel)
admin.site.register(AccessoryModel)
admin.site.register(AssetModel)
admin.site.register(AssetCategoryModel)
admin.site.register(ComponentModel)
admin.site.register(ComponentCategoryModel)
admin.site.register(ConsumableModel)
admin.site.register(ConsumableCategoryModel)
admin.site.register(AssetRequest)
