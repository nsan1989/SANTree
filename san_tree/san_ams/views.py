from django.shortcuts import render
from .models import *
from .forms import *
from django.core.exceptions import PermissionDenied
from django.contrib import messages

# Staff Dashboard.
def StaffDashboardView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        activity = AssetModel.objects.all()
        if activity.exists():
            context["activities"] = activity[:10]
        else:
            context["activity_message"] = "No current activity!"
        total_asset_users = CustomUsers.objects.filter(
            id__in=AssetModel.objects.values('assigned_to')
        ).count()
        total_assets = AssetModel.objects.count()
        total_components = ComponentModel.objects.count()
        total_consumables = ConsumableModel.objects.count()
        total_assessories = AccessoryModel.objects.count()
        context.update ({
            'asset_users': total_asset_users,
            'asset': total_assets,
            'consumable': total_consumables,
            'component': total_components,
            'accessory': total_assessories,
        })
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:staff_dashboard" and current_user_role == 'User':
        return render(request, 'asset_staff_dashboard.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# Admin Dashboard.
def AdminDashboardView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        activity = AssetModel.objects.all()
        if activity.exists():
            context["activities"] = activity
        else:
            context["activity_message"] = "No current activity!"
        total_asset_users = CustomUsers.objects.filter(
            id__in=AssetModel.objects.values('assigned_to')
        ).count()
        total_assets = AssetModel.objects.count()
        total_licenses = LicenseModel.objects.count()
        total_components = ComponentModel.objects.count()
        total_consumables = ConsumableModel.objects.count()
        total_assessories = AccessoryModel.objects.count()
        context.update ({
            'asset_users': total_asset_users,
            'asset': total_assets,
            'license': total_licenses,
            'consumable': total_consumables,
            'component': total_components,
            'accessory': total_assessories,
        })
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_dashboard" and current_user_role == 'Admin':
        return render(request, 'asset_admin_dashboard.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# Asset View.
def AssetView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_assets" and current_user_role == 'Admin':
        return render(request, 'admin_assets.html', context)
    if view_name == "ams:staff_assets" and current_user_role == 'User':
        return render(request, 'staff_assets.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# License View.
def LicenseView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        license = LicenseModel.objects.all()
        if license.exists():
            context["licenses"] = license
        else:
            context["license_message"] = "No licenses found!"
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:all_licenses" and current_user_role == 'Admin':
        return render(request, 'licenses.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# Accessories View.
def AccessoriesView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        accessories = AccessoryModel.objects.all()
        if accessories.exists():
            context["accessories"] = accessories
        else:
            context["accessories_message"] = "No accessories found!"
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_accessories" and current_user_role == 'Admin':
        return render(request, 'admin_accessories_page.html', context)
    if view_name == "ams:staff_accessories" and current_user_role == 'User':
        return render(request, 'staff_accessories_page.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# Consumables View.
def ConsumablesView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        consumables = ConsumableModel.objects.all()
        if consumables.exists():
            context["consumables"] = consumables
        else:
            context["consumables_message"] = "No consumables found!"
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_consumables" and current_user_role == 'Admin':
        return render(request, 'admin_consumables_page.html', context)
    if view_name == "ams:staff_consumables" and current_user_role == 'User':
        return render(request, 'staff_consumables_page.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# Components View.
def ComponentsView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        components = ComponentModel.objects.all()
        if components.exists():
            context["components"] = components
        else:
            context["components_message"] = "No components found!"
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_components" and current_user_role == 'Admin':
        return render(request, 'admin_components_page.html', context)
    if view_name == "ams:staff_components" and current_user_role == 'User':
        return render(request, 'staff_components_page.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# Asset Users View.
def AssetUsersView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        asset_users = CustomUsers.objects.filter(
                id__in=AssetModel.objects.values('assigned_to')
            )
        if asset_users.exists():
            context["asset_users"] = asset_users
        else:
            context["asset_users_message"] = "No active users!"
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_asset_users" and current_user_role == 'Admin':
        return render(request, 'admin_asset_users.html', context)
    if view_name == "ams:staff_asset_users" and current_user_role == 'User':
        return render(request, 'staff_asset_users.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# Add License View.
def AddLicenseView(request):
    if request.method == 'POST':
        form = AddLicenseForm(request.POST)
        if form.is_valid():
            license = form.save(commit=False)
            exists = LicenseModel.objects.filter(name__iexact=license.name).exists()
            if exists:
                messages.error(request, 'License already exist!')
            else:
                license.save()
                messages.success(request, 'License added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddLicenseForm()

    return render(request, 'asset_form_templates/license_form.html', {'form': form})

# Add Accesspry Category View.
def AddAccessoryCategoryView(request):
    if request.method == 'POST':
        form = AddAccessoryCategoryForm(request.POST)
        if form.is_valid():
            accessory = form.save(commit=False)
            exists = AccessoryCategoryModel.objects.filter(name__iexact=accessory.name).exists()
            if exists:
                messages.error(request, 'Accessory Category already exist!')
            else:
                accessory.save()
                messages.error(request, 'Accessory Category added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddAccessoryCategoryForm()

    return render(request, 'asset_form_templates/accessory_category_form.html', {'form': form})

# Add Accessory View.
def AddAccessoryView(request):
    if request.method == 'POST':
        form = AddAccessoryForm(request.POST)
        if form.is_valid():
            accessory = form.save(commit=False)
            exists = AccessoryModel.objects.filter(name__iexact=accessory.name).exists()
            if exists:
                messages.error(request, 'Accessory already exist!')
            else:
                accessory.save()
                messages.error(request, 'Accessory added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddAccessoryCategoryForm()

    return render(request, 'asset_form_templates/accessory_form.html', {'form': form})

# Add Consumable Category Form.
def AddConsumableCategoryView(request):
    if request.method == 'POST':
        form = AddConsumableCategoryForm(request.POST)
        if form.is_valid():
            consumable = form.save(commit=False)
            exists = ConsumableCategoryModel.objects.filter(name__iexact=consumable.name).exists()
            if exists:
                messages.error(request, 'Consumable Category already exist!')
            else:
                consumable.save()
                messages.error(request, 'Consumable Category added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddConsumableCategoryForm()

    return render(request, 'asset_form_templates/consumable_category_form.html', {'form': form})

# Add Consumable Form
def AddConsumableView(request):
    if request.method == 'POST':
        form = AddConsumableForm(request.POST)
        if form.is_valid():
            consumable = form.save(commit=False)
            exists = ConsumableModel.objects.filter(name__iexact=consumable.name).exists()
            if exists:
                messages.error(request, 'Consumable already exist!')
            else:
                consumable.save()
                messages.error(request, 'Consumable added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddConsumableForm()

    return render(request, 'asset_form_templates/consumable_form.html', {'form': form})

# Add Component Category Form
def AddComponentCategoryView(request):
    if request.method == 'POST':
        form = AddComponentCategoryForm(request.POST)
        if form.is_valid():
            component = form.save(commit=False)
            exists = ComponentCategoryModel.objects.filter(name__iexact=component.name).exists()
            if exists:
                messages.error(request, 'Component Category already exist!')
            else:
                component.save()
                messages.error(request, 'Component Category added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddComponentCategoryForm()

    return render(request, 'asset_form_templates/component_category_form.html', {'form': form})

# Add Component Form
def AddComponentView(request):
    if request.method == 'POST':
        form = AddComponentForm(request.POST)
        if form.is_valid():
            component = form.save(commit=False)
            exists = ComponentModel.objects.filter(name__iexact=component.name).exists()
            if exists:
                messages.error(request, 'Component already exist!')
            else:
                component.save()
                messages.error(request, 'Component added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddComponentForm()

    return render(request, 'asset_form_templates/component_category_form.html', {'form': form})

# Add Asset Category Form
def AddAssetCategoryView(request):
    if request.method == 'POST':
        form = AddAssetCategoryForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            exists = AssetCategoryModel.objects.filter(name__iexact=asset.name).exists()
            if exists:
                messages.error(request, 'Asset category already exist!')
            else:
                asset.save()
                messages.error(request, 'Asset category added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddAssetCategoryForm()

    return render(request, 'asset_form_templates/asset_category_form.html', {'form': form})

# Add Asset Form
def AddAssetView(request):
    if request.method == 'POST':
        form = AddAssetForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            exists = AssetCategoryModel.objects.filter(name__iexact=asset.name).exists()
            if exists:
                messages.error(request, 'Asset category already exist!')
            else:
                asset.save()
                messages.error(request, 'Asset category added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddAssetForm()

    return render(request, 'asset_form_templates/asset_form.html', {'form': form})
