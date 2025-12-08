from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .forms import *
from django.core.exceptions import PermissionDenied
from django.contrib import messages
import io
import matplotlib.pyplot as plt
from threading import Lock
plot_lock = Lock()
from django.http import HttpResponse
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

# Asset Pie Chart.
def AssetPieChart(request):
    current_user = request.user
    dept_asset = AssetModel.objects.filter(department = current_user.department).all()
    deploy_asset = dept_asset.filter(status = 'deployed').count()
    ready_asset = dept_asset.filter(status='ready to deploy').count()
    repair_asset = dept_asset.filter(status='repair').count()
    broken_asset = dept_asset.filter(status='broken').count()
    if deploy_asset + ready_asset + repair_asset + broken_asset == 0:
        labels = ['No Data']
        sizes = [1]
        colors = ['#d3d3d3']
    else:
        raw_data = [
            ('Deployed', deploy_asset, '#006600'),
            ('Ready to Deploy', ready_asset, '#0066ff'),
            ('Repair', repair_asset, '#ff6600'),
            ('Broken', broken_asset, '#eb0707')
        ]
        filtered_data = [(label, size, color) for label, size, color in raw_data if size > 0]
        if not filtered_data:
            labels = ['No Data']
            sizes = [1]
            colors = ['#d3d3d3']
        else:
            labels, sizes, colors = zip(*filtered_data)

    buffer = io.BytesIO()

    with plot_lock:
        bg_color = (0, 0, 0, 0.4)
        fig, ax = plt.subplots(figsize=(4, 2), facecolor=bg_color) 
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, textprops={'color': 'white'})
        ax.axis('equal')
        plt.savefig(buffer, format='png', facecolor=fig.get_facecolor())
        plt.close(fig)

    buffer.seek(0)
    return HttpResponse(buffer.read(), content_type='image/png')

# Staff Dashboard.
def StaffDashboardView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    # asset handler
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
    # asset requester
    try:
        assets_requested = AssetModel.objects.filter(created_by = current_user).order_by('created_at')
        if assets_requested.exists():
            context.update["assets"] = assets_requested[:10]
        else:
            context.update["assets_message"] = "No asset have been requested!"
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

# Asset View.
def AssetView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        assets = AssetModel.objects.all()
        if assets.exists():
            context["assets"] = assets
        else:
            context["assets_message"] = "No assets found!"
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_assets" and current_user_role == 'Admin':
        return render(request, 'admin_assets.html', context)
    if view_name == "ams:staff_assets" and current_user_role == 'User':
        return render(request, 'staff_assets.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# Assigned Asset View.
def AssignedAssetView(request, asset_id):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    asset = get_object_or_404(AssetModel, id=asset_id)
    context = {"asset": asset}

    form = AssignedAssetForm(request.POST or None)
    
    try:
        if request.method == 'POST':
            if form.is_valid():
                selected_user_id = form.cleaned_data("assigned_to")
                selected_user = get_object_or_404(CustomUsers, id=selected_user_id)
                asset.assigned_to = selected_user
                asset.status = 'assigned'
                asset.save()
                context["success"] = f"Asset assigned to {selected_user.username} successfully."
                return redirect("ams:admin_assets")
            
        context = {
            "form": form,
            "asset": asset,
        }
        
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_assigned_assets" and current_user_role == 'Admin':
        return render(request, 'assign_asset_form.html', context)
    if view_name == "ams:staff_assigned_assets" and current_user_role == 'User':
        return render(request, 'assign_asset_form.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# Asset Detail View.
def AssetDetailView(request, asset_id):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        asset = get_object_or_404(AssetModel, id=asset_id)
        context["asset"] = asset
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_asset_detail" and current_user_role == 'Admin':
        return render(request, 'asset_detail.html', context)
    if view_name == "ams:staff_asset_detail" and current_user_role == 'User':
        return render(request, 'asset_detail.html', context)
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

# Assigned Licenses View.
def AssignedLicensesView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        if request.method == 'POST':
            form = AssignedLicenseForm(request.POST)
            if form.is_valid():
                selected_user_id = form.cleaned_data.get("user")
                selected_license_id = form.cleaned_data.get("license")

                selected_user = get_object_or_404(CustomUsers, id=selected_user_id)
                selected_license = get_object_or_404(
                    LicenseModel, id=selected_license_id,
                    status='available', assigned_to__isnull=True
                )
                selected_license.assigned_to = selected_user
                selected_license.status = "assigned"
                selected_license.save()
                context["success"] = f"License assigned to {selected_user.username} successfully."
                return redirect("ams:assigned_license")
            else:
                context["error"] = "Invalid form submission."
        else:
            form = AssignedLicenseForm()
        context["form"] = form
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:assigned_license" and current_user_role == 'Admin':
        return render(request, 'assign_license_form.html', context)
    raise PermissionDenied("You are not authorized to view this page. Please contact administrator!")

# License Update View.
def LicenseUpdateView():
    licenses = LicenseModel.objects.all()
    current_date = timezone.now().date()
    for license in licenses:
        try:
            if current_date > license.expiry_date:
                license.status = 'expired'
                license.is_expire = True

            elif current_date >= (license.expiry_date - timedelta(days=5)):
                license.status = 'renewal due'
                license.is_expire = False

            else:
                license.is_expire = False
                license.status = 'active'
                
            license.save()
        except Exception as e:
            logger.error(f"[License Update ERROR] {license} -> {e}")

    logger.info("✔ License update job completed.")

# License Detail View.
def LicenseDetailView(request, license_id):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        license = get_object_or_404(LicenseModel, id=license_id)
        context["license"] = license
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:license_detail" and current_user_role == 'Admin':
        return render(request, 'license_detail.html', context)
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
