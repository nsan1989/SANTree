from django import forms
from .models import *

# Add License Form
class AddLicenseForm(forms.ModelForm):
    class Meta:
        model = LicenseModel
        fields = ['name', 'manufacturer', 'product_key', 'purchase_date', 'expiry_date','buyer_name', 'buyer_phone', 'buyer_email', 'quantity', 'cost']

# Add Accessory Categories Form
class AddAccessoryCategoryForm(forms.ModelForm):
    class Meta:
        model = AccessoryCategoryModel
        fields = ['name']

# Add Accessory Form
class AddAccessoryForm(forms.ModelForm):
    class Meta:
        model = AccessoryModel
        fields = ['name', 'category', 'model_number', 'manufacturer', 'image', 'purchase_date', 'cost', 'quantity']

# Add Consumable Categories Form
class AddConsumableCategoryForm(forms.ModelForm):
    class Meta:
        model = ConsumableCategoryModel
        fields = ['name']

# Add Consumable Form
class AddConsumableForm(forms.ModelForm):
    class Meta:
        model = ConsumableModel
        fields = ['name', 'category', 'model_number', 'manufacturer', 'image', 'purchase_date', 'cost', 'quantity']

# Add Component Categories Form
class AddComponentCategoryForm(forms.ModelForm):
    class Meta:
        model = ComponentCategoryModel
        fields = ['name']

# Add Component Form
class AddComponentForm(forms.ModelForm):
    class Meta:
        model = ComponentModel
        fields = ['name', 'category', 'image', 'serial_number', 'model_number', 'manufacturer', 'quantity', 'cost', 'purchase_date']

# Add Asset Category Form
class AddAssetCategoryForm(forms.ModelForm):
    class Meta:
        model = AssetCategoryModel
        fields = ['name']

# Add Asset Form
class AddAssetForm(forms.ModelForm):
    class Meta:
        model = AssetModel
        fields = ['name', 'category', 'manufacturer', 'model_number', 'serial_number', 'image', 'purchase_date', 'cost', 'expiry_date']

# Assigned License Form
class AssignedLicenseForm(forms.ModelForm):
    
    assigned_to = forms.ModelChoiceField(
        queryset=CustomUsers.objects.all(),
        label="Assign License To",
        required=True
    )

    class Meta:
        model = LicenseModel
        fields = ['assigned_to']

# Assigned Asset Form
class AssignedAssetForm(forms.ModelForm):
    class Meta:
        model = AssetModel
        fields = ['assigned_to']
    