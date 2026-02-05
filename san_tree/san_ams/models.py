from django.db import models
import os
from django.utils import timezone
from accounts.models import Departments, Location, CustomUsers
from datetime import date
from django.db import transaction

# license status choices.
LICENSE_STATUS = [
    ('active', 'Active'),
    ('assigned', 'Assigned'),
    ('available', 'Available'),
    ('renewal due', 'Renewal Due'),
    ('expired', 'Expired'),
    ('revoked', 'Revoked'),
]

# license model.
class LicenseModel(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    product_key = models.CharField(max_length=255, unique=True)
    purchase_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField(default=timezone.now)
    buyer_name = models.CharField(max_length=100)
    buyer_phone = models.CharField(max_length=15)
    buyer_email = models.EmailField(unique=True)
    quantity = models.PositiveSmallIntegerField(default=0)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    is_expire = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=LICENSE_STATUS, default='active')
    assigned_to = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, null=True, blank=True, related_name='license_user')
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, null=True, blank=True, related_name='license_user_department')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, related_name='license_user_location')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'License'
    
# accessory category model.
class AccessoryCategoryModel(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'AccessoryCategories'
    
# accessory image path.
def accessory_image_path(instance, filename):
    filename = os.path.basename(filename)
    return f'accessory_images/{filename}'
    
# accessory model.
class AccessoryModel(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(AccessoryCategoryModel, on_delete=models.CASCADE, related_name='accessory_category')
    model_number = models.CharField(max_length=50, unique=True)
    manufacturer = models.CharField(max_length=100)
    image = models.ImageField(upload_to=accessory_image_path, null=True, blank=True)
    purchase_date = models.DateField(default=timezone.now)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Accessories'
    
# consumable category model.
class ConsumableCategoryModel(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'ConsumableCategories'
    
# consumable image path.
def consumable_image_path(instance, filename):
    filename = os.path.basename(filename)
    return f'consumable_images/{filename}'

# consumable model.
class ConsumableModel(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ConsumableCategoryModel, on_delete=models.CASCADE, related_name='consumable_category')
    model_number = models.CharField(max_length=50, unique=True)
    manufacturer = models.CharField(max_length=100)
    image = models.ImageField(upload_to=consumable_image_path, null=True, blank=True)
    purchase_date = models.DateField(default=timezone.now)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Consumables'
    
# component category model.
class ComponentCategoryModel(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'ComponentCategories'
    
# component image path.
def component_image_path(instance, filename):
    filename = os.path.basename(filename)
    return f'component_images/{filename}'
    
# component model.
class ComponentModel(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ComponentCategoryModel, on_delete=models.CASCADE, related_name='component_category')
    image = models.ImageField(upload_to=component_image_path, null=True, blank=True)
    serial_number = models.CharField(max_length=50, unique=True)
    model_number = models.CharField(max_length=50, unique=True)
    manufacturer = models.CharField(max_length=100)
    quantity = models.PositiveSmallIntegerField(default=0)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    purchase_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Components'

# asset category model.
class AssetCategoryModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'AssetCategories'

# asset image path.
def asset_image_path(instance, filename):
    filename = os.path.basename(filename)
    return f'asset_images/{filename}'

# asset status choices.
ASSET_STATUS = [
    ('available', 'Available'),
    ('requested', 'Requested'),
    ('deployed', 'Deployed'),
    ('ready to deploy', 'Ready to Deploy'),
    ('repair', 'Repair'),
    ('broken', 'Broken'),
    ('waiting', 'Waiting'),
]

# asset model.
class AssetModel(models.Model):
    asset_tag = models.CharField(max_length=20, unique=True, blank=True, null=True)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(AssetCategoryModel, on_delete=models.CASCADE, related_name='asset_category')
    manufacturer = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100, unique=True)
    serial_number = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to=asset_image_path, null=True, blank=True)
    purchase_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField(default=timezone.now)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    asset_component = models.ManyToManyField(ComponentModel, blank=True, related_name='asset_components')
    asset_consumable = models.ManyToManyField(ConsumableModel, blank=True, related_name='asset_consumables')
    asset_accessory = models.ManyToManyField(AccessoryModel, blank=True, related_name='asset_accessories')
    asset_license = models.ManyToManyField(LicenseModel, blank=True, related_name='asset_licenses')
    status = models.CharField(max_length=20, choices=ASSET_STATUS, default='available')
    handler = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, null=True, blank=True, related_name='asset_handler')
    created_by = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, null=True, blank=True, related_name='asset_created_by')
    assigned_to = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, null=True, blank=True, related_name='asset_user')
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, null=True, blank=True, related_name='asset_department')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, related_name='asset_location')
    requestable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Assets'

    @property
    def useful_life_years(self):
        days = (self.expiry_date - self.purchase_date).days
        return max(days / 365, 1)
    
    @property
    def annual_depreciation(self):
        return float(self.cost) / self.useful_life_years
    
    @property
    def accumulated_depreciation(self):
        elapsed_years = (date.today() - self.purchase_date).days / 365
        depreciation = self.annual_depreciation * elapsed_years
        return min(depreciation, float(self.cost))
    
    @property
    def current_value(self):
        return max(float(self.cost) - self.accumulated_depreciation, 0)
    
    def save(self, *args, **kwargs):
        if not self.asset_tag:
            with transaction.atomic():
                last_asset = (
                    AssetModel.objects
                    .select_for_update()
                    .order_by('-created_at')
                    .first()
                )

                if last_asset and last_asset.asset_tag:
                    last_number = int(last_asset.asset_tag.replace('ASSET', ''))
                    self.asset_tag = f"ASSET{last_number + 1:05d}"
                else:
                    self.asset_tag = "ASSET00001"

                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

# asset request model.
class AssetRequest(models.Model):
    asset = models.ForeignKey(AssetModel, on_delete=models.CASCADE, related_name='requests')
    requested_by = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, null=True, blank=True, related_name='asset_requests_made')
    requested_to = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, null=True, blank=True, related_name='asset_requests_received')
    department = models.ForeignKey(Departments, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected'),
            ('DEPLOYED', 'Deployed'),
        ],
        default='PENDING'
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.asset.name
    
    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Asset Requests'
