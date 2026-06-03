import io
from threading import Lock

import matplotlib.pyplot as plt
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import *
from .models import *

plot_lock = Lock()
import logging
from datetime import timedelta

from django.db import IntegrityError
from django.http import HttpResponse

from accounts.models import Departments
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q
from itertools import chain

logger = logging.getLogger(__name__)


# Asset Pie Chart.
def AssetPieChart(request):
    current_user = request.user
    dept_asset = AssetModel.objects.filter(department=current_user.department).all()
    deploy_asset = dept_asset.filter(status="deployed").count()
    ready_asset = dept_asset.filter(status="ready to deploy").count()
    repair_asset = dept_asset.filter(status="repair").count()
    broken_asset = dept_asset.filter(status="broken").count()
    if deploy_asset + ready_asset + repair_asset + broken_asset == 0:
        labels = ["No Data"]
        sizes = [1]
        colors = ["#d3d3d3"]
    else:
        raw_data = [
            ("Deployed", deploy_asset, "#006600"),
            ("Ready to Deploy", ready_asset, "#0066ff"),
            ("Repair", repair_asset, "#ff6600"),
            ("Broken", broken_asset, "#eb0707"),
        ]
        filtered_data = [
            (label, size, color) for label, size, color in raw_data if size > 0
        ]
        if not filtered_data:
            labels = ["No Data"]
            sizes = [1]
            colors = ["#d3d3d3"]
        else:
            labels, sizes, colors = zip(*filtered_data)

    buffer = io.BytesIO()

    with plot_lock:
        bg_color = (0, 0, 0, 0.4)
        fig, ax = plt.subplots(figsize=(4, 2), facecolor=bg_color)
        ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
            textprops={"color": "white"},
        )
        ax.axis("equal")
        plt.savefig(buffer, format="png", facecolor=fig.get_facecolor())
        plt.close(fig)

    buffer.seek(0)
    return HttpResponse(buffer.read(), content_type="image/png")


# Staff Dashboard.
def StaffDashboardView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        req_asset = AssetRequest.objects.filter(requested_by=current_user)
        req_handler = AssetRequest.objects.filter(asset__handler=current_user)
        asset_handler = AssetModel.objects.filter(handler=current_user)
        activity = req_handler if req_handler.exists() else asset_handler
        context["my_asset"] = req_asset
        if activity.exists():
            context["activities"] = activity
        else:
            context["activity_message"] = "No current activity!"
        total_asset_users = CustomUsers.objects.filter(
            id__in=AssetModel.objects.values("assigned_to")
        ).count()
        total_assets = AssetModel.objects.count()
        total_components = ComponentModel.objects.count()
        total_consumables = ConsumableModel.objects.count()
        total_assessories = AccessoryModel.objects.count()
        context.update(
            {
                "asset_users": total_asset_users,
                "asset": total_assets,
                "consumable": total_consumables,
                "component": total_components,
                "accessory": total_assessories,
            }
        )
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:staff_dashboard" and current_user_role == "User":
        return render(request, "asset_staff_dashboard.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# Admin Dashboard.
def AdminDashboardView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        activity = AssetRequest.objects.filter(department=current_user.department)
        if activity.exists():
            context["activities"] = activity
        else:
            context["activity_message"] = "No current activity!"
        total_asset_users = CustomUsers.objects.filter(
            id__in=AssetModel.objects.values("assigned_to")
        ).count()
        assets = AssetModel.objects.filter(department=current_user.department)
        total_assets = assets.count()
        licenses = LicenseModel.objects.filter(department=current_user.department)
        total_licenses = licenses.count()
        total_components = ComponentModel.objects.count()
        total_consumables = ConsumableModel.objects.count()
        total_assessories = AccessoryModel.objects.count()
        context.update(
            {
                "asset_users": total_asset_users,
                "asset": total_assets,
                "license": total_licenses,
                "consumable": total_consumables,
                "component": total_components,
                "accessory": total_assessories,
            }
        )
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_dashboard" and current_user_role == "Admin":
        return render(request, "asset_admin_dashboard.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# Add License View.
def AddLicenseView(request):
    if request.method == "POST":
        form = AddLicenseForm(request.POST)
        if form.is_valid():
            license = form.save(commit=False)
            exists = LicenseModel.objects.filter(name__iexact=license.name).exists()
            if exists:
                messages.error(request, "License already exist!")
            else:
                license.save()
                messages.success(request, "License added successfully!")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddLicenseForm()

    return render(request, "asset_form_templates/license_form.html", {"form": form})


# Add Accesspry Category View.
def AddAccessoryCategoryView(request):
    if request.method == "POST":
        form = AddAccessoryCategoryForm(request.POST)
        if form.is_valid():
            accessory = form.save(commit=False)
            exists = AccessoryCategoryModel.objects.filter(
                name__iexact=accessory.name
            ).exists()
            if exists:
                messages.error(request, "Accessory Category already exist!")
            else:
                accessory.save()
                messages.error(request, "Accessory Category added successfully!")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddAccessoryCategoryForm()

    return render(
        request, "asset_form_templates/accessory_category_form.html", {"form": form}
    )


# Add Accessory View.
def AddAccessoryView(request):

    category = AssetCategoryModel.objects.all()

    if request.method == "POST":
        form = AddAccessoryForm(request.POST)
        if form.is_valid():
            accessory = form.save(commit=False)
            exists = AccessoryModel.objects.filter(name__iexact=accessory.name).exists()
            if exists:
                messages.error(request, "Accessory already exist!")
            else:
                accessory.save()
                messages.error(request, "Accessory added successfully!")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddAccessoryCategoryForm()

    context = {"form": form, "category": category}

    return render(request, "asset_form_templates/accessory_form.html", context)


# Add Consumable Category Form.
def AddConsumableCategoryView(request):
    if request.method == "POST":
        form = AddConsumableCategoryForm(request.POST)
        if form.is_valid():
            consumable = form.save(commit=False)
            exists = ConsumableCategoryModel.objects.filter(
                name__iexact=consumable.name
            ).exists()
            if exists:
                messages.error(request, "Consumable Category already exist!")
            else:
                consumable.save()
                messages.error(request, "Consumable Category added successfully!")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddConsumableCategoryForm()

    return render(
        request, "asset_form_templates/consumable_category_form.html", {"form": form}
    )


# Add Consumable Form
def AddConsumableView(request):
    category = AssetCategoryModel.objects.all()
    if request.method == "POST":
        form = AddConsumableForm(request.POST)
        if form.is_valid():
            consumable = form.save(commit=False)
            exists = ConsumableModel.objects.filter(
                name__iexact=consumable.name
            ).exists()
            if exists:
                messages.error(request, "Consumable already exist!")
            else:
                consumable.save()
                messages.error(request, "Consumable added successfully!")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddConsumableForm()

    context = {
        "form": form,
        "category": category,
    }

    return render(request, "asset_form_templates/consumable_form.html", context)


# Add Component Category Form
def AddComponentCategoryView(request):
    if request.method == "POST":
        form = AddComponentCategoryForm(request.POST)
        if form.is_valid():
            component = form.save(commit=False)
            exists = ComponentCategoryModel.objects.filter(
                name__iexact=component.name
            ).exists()
            if exists:
                messages.error(request, "Component Category already exist!")
            else:
                component.save()
                messages.error(request, "Component Category added successfully!")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddComponentCategoryForm()

    return render(
        request, "asset_form_templates/component_category_form.html", {"form": form}
    )


# Add Component Form
def AddComponentView(request):

    category = AssetCategoryModel.objects.all()

    if request.method == "POST":
        form = AddComponentForm(request.POST)
        if form.is_valid():
            component = form.save(commit=False)
            exists = ComponentModel.objects.filter(name__iexact=component.name).exists()
            if exists:
                messages.error(request, "Component already exist!")
            else:
                component.save()
                messages.error(request, "Component added successfully!")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddComponentForm()

    context = {
        "form": form,
        "category": category,
    }

    return render(request, "asset_form_templates/component_form.html", context)


# Add Asset Category Form
def AddAssetCategoryView(request):
    if request.method == "POST":
        form = AddAssetCategoryForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            exists = AssetCategoryModel.objects.filter(name__iexact=asset.name).exists()
            if exists:
                messages.error(request, "Asset category already exist!")
            else:
                asset.save()
                messages.error(request, "Asset category added successfully!")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddAssetCategoryForm()

    return render(
        request, "asset_form_templates/asset_category_form.html", {"form": form}
    )


# Add Asset Form
def AddAssetView(request):
    user = request.user
    category = AssetCategoryModel.objects.all()
    dept_users = CustomUsers.objects.filter(
        department__name=user.department.name, role="User"
    )

    if request.method == "POST":
        form = AddAssetForm(request.POST, request.FILES)
        if form.is_valid():
            asset_name = form.cleaned_data["name"]

            if AssetModel.objects.filter(name__iexact=asset_name).exists():
                messages.error(request, "Asset already exists!")
            else:
                try:
                    asset_name = form.save(commit=False)
                    asset_name.department = request.user.department
                    asset_name.created_by = request.user
                    form.save()
                    messages.success(request, "Asset added successfully!")
                except IntegrityError:
                    messages.error(
                        request,
                        "Asset with same model number or serial number already exists!",
                    )
        else:
            print(form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddAssetForm()

    context = {
        "form": form,
        "category": category,
        "dept_user": dept_users,
    }

    return render(request, "asset_form_templates/asset_form.html", context)


# Asset View.
def AssetView(request):
    current_user = request.user
    print(current_user)
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        if current_user_role == "Admin":
            asset = AssetModel.objects.filter(department=current_user.department).all()
        else:
            asset = AssetModel.objects.filter(
                Q(handler=current_user) | Q(assigned_to=current_user)
            )
        statuses = [choice[1] for choice in assetChoices.choices]
        if asset.exists():
            context = {
                "assets": asset,
                "statuses": statuses,
                "request_user": current_user,
            }
        else:
            context["assets_message"] = "No assets found!"
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_assets" and current_user_role == "Admin":
        return render(request, "admin_assets.html", context)
    if view_name == "ams:staff_assets" and current_user_role == "User":
        return render(request, "staff_assets.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# load assets
def load_assets(request):
    department_id = request.GET.get("department_id")

    assets = AssetModel.objects.filter(
        department_id=department_id, is_active=True, requestable=True
    ).select_related("category")

    data = [
        {
            "id": asset.id,
            "text": f"{asset.asset_tag} | {asset.name} | {asset.category.name}",
        }
        for asset in assets
    ]

    return JsonResponse(data, safe=False)


# Asset Request View.
def AssetRequestView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    form = AssetRequestForm(request.POST or None, user=request.user)
    try:
        if request.method == "POST":
            if form.is_valid():
                asset_request = form.save(commit=False)
                asset_request.requested_by = current_user
                asset_admin = CustomUsers.objects.filter(
                    role="Admin",
                    department=asset_request.asset.department,
                    is_active=True,
                ).first()
                asset_request.requested_to = asset_admin
                asset_request.department = asset_request.asset.department
                asset_request.status = "pending"
                asset_request.save()
                context["success"] = "Asset request submitted successfully."

                return redirect("ams:success_asset")
        else:
            form = AssetRequestForm(user=request.user)

        context = {
            "form": form,
        }
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"

    return render(request, "asset_request.html", context)


# Assigned Asset View.
def AssignedAssetView(request, id):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    request_asset = get_object_or_404(AssetRequest, id=id)
    asset = request_asset.asset
    request_user = CustomUsers.objects.filter(
        username=request_asset.requested_by.username
    )
    context = {"asset": asset}

    form = AssignedAssetForm(request.POST or None, users=request_user)

    try:
        if request.method == "POST":
            if form.is_valid():
                asset.assigned_to = request_asset.requested_by
                asset.status = "ASSIGNED"
                asset.requestable = False
                asset.save(
                    update_fields=[
                        "assigned_to",
                        "status",
                    ]
                )
                request_asset.status = "ASSIGNED"
                request_asset.save(update_fields=["status"])
                context["success"] = (
                    f"Asset assigned to {asset.assigned_to.username} successfully."
                )
                if current_user_role == "Admin":
                    return redirect("ams:admin_assets")
                else:
                    return redirect("ams:staff_assets")

        context = {
            "form": form,
            "asset": asset,
            "request_asset": request_asset,
        }

    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_assigned_assets" and current_user_role == "Admin":
        return render(request, "assign_asset_form.html", context)
    if view_name == "ams:staff_assigned_assets" and current_user_role == "User":
        return render(request, "assign_asset_form.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


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
    if view_name == "ams:admin_asset_detail" and current_user_role == "Admin":
        return render(request, "asset_detail.html", context)
    if view_name == "ams:staff_asset_detail" and current_user_role == "User":
        return render(request, "asset_detail.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


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
    if view_name == "ams:all_licenses" and current_user_role == "Admin":
        return render(request, "licenses.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# Assigned Licenses View.
def AssignedLicensesView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        if request.method == "POST":
            form = AssignedLicenseForm(request.POST)
            if form.is_valid():
                selected_user_id = form.cleaned_data.get("user")
                selected_license_id = form.cleaned_data.get("license")

                selected_user = get_object_or_404(CustomUsers, id=selected_user_id)
                selected_license = get_object_or_404(
                    LicenseModel,
                    id=selected_license_id,
                    status="available",
                    assigned_to__isnull=True,
                )
                selected_license.assigned_to = selected_user
                selected_license.status = "assigned"
                selected_license.save()
                context["success"] = (
                    f"License assigned to {selected_user.username} successfully."
                )
                return redirect("ams:assigned_license")
            else:
                context["error"] = "Invalid form submission."
        else:
            form = AssignedLicenseForm()
        context["form"] = form
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:assigned_license" and current_user_role == "Admin":
        return render(request, "assign_license_form.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# License Update View.
def LicenseUpdateView():
    licenses = LicenseModel.objects.all()
    current_date = timezone.now().date()
    for license in licenses:
        try:
            if current_date > license.expiry_date:
                license.status = "expired"
                license.is_expire = True

            elif current_date >= (license.expiry_date - timedelta(days=5)):
                license.status = "renewal due"
                license.is_expire = False

            else:
                license.is_expire = False
                license.status = "active"

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
    if view_name == "ams:license_detail" and current_user_role == "Admin":
        return render(request, "license_detail.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


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
    if view_name == "ams:admin_accessories" and current_user_role == "Admin":
        return render(request, "admin_accessories_page.html", context)
    if view_name == "ams:staff_accessories" and current_user_role == "User":
        return render(request, "staff_accessories_page.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


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
    if view_name == "ams:admin_consumables" and current_user_role == "Admin":
        return render(request, "admin_consumables_page.html", context)
    if view_name == "ams:staff_consumables" and current_user_role == "User":
        return render(request, "staff_consumables_page.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


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
    if view_name == "ams:admin_components" and current_user_role == "Admin":
        return render(request, "admin_components_page.html", context)
    if view_name == "ams:staff_components" and current_user_role == "User":
        return render(request, "staff_components_page.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


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
            id__in=AssetModel.objects.values("assigned_to")
        )
        if asset_users.exists():
            context["asset_users"] = asset_users
        else:
            context["asset_users_message"] = "No active users!"
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_asset_users" and current_user_role == "Admin":
        return render(request, "admin_asset_users.html", context)
    if view_name == "ams:staff_asset_users" and current_user_role == "User":
        return render(request, "staff_asset_users.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# All Assets Request View.
def AllAssetsRequestsView(request):
    current_user = request.user
    try:
        current_user_role = current_user.role
    except:
        raise PermissionDenied("User profile not found")
    context = {}
    try:
        request_assets = AssetRequest.objects.filter(requested_to=current_user)
        if request_assets.exists():
            context["request_assets"] = request_assets
        else:
            context["asset_requests_message"] = "No assets requests!"
    except Exception as e:
        context["error"] = f"An unexpected error occurred: {e}"
    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_asset_requests" and current_user_role == "Admin":
        return render(request, "all_assets_request.html", context)
    raise PermissionDenied(
        "You are not authorized to view this page. Please contact administrator!"
    )


# admin asset update status.
def AdminUpdateStatus(request, id):
    user = request.user
    try:
        user_role = user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")

    request_asset = get_object_or_404(AssetRequest, id=id)

    asset = request_asset.asset

    if request.method == "POST":
        new_status = request.POST.get("status")

        if new_status == "APPROVED":
            request_asset.status = new_status
            request_asset.save(update_fields=["status"])
            asset.status = new_status
            asset.save(update_fields=["status"])

        if new_status == "REJECTED":
            request_asset.status = new_status
            request_asset.save(update_fields=["status"])
            asset.status = new_status
            asset.save(update_fields=["status"])

        return redirect("ams:admin_asset_requests")

    view_name = request.resolver_match.view_name
    if view_name == "ams:admin_update_status" and user_role == "Admin":
        return redirect("ams:admin_asset_requests")
    raise PermissionDenied("You are not authorized to view this page.")


# admin assign asset handler.
def AdminUpdateHandler(request, id):
    user = request.user
    try:
        user_role = user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")

    request_asset = get_object_or_404(AssetRequest, id=id)

    asset = request_asset.asset

    if request.method == "POST":
        form = AssetHandlerForm(request.POST, instance=asset, request=request)
        if form.is_valid():
            form.save()

            return redirect("ams:admin_asset_requests")

    else:
        form = AssetHandlerForm(instance=asset, request=request)

    context = {
        "form": form,
        "asset": asset,
        "request_obj": request_asset,
    }
    return render(request, "handler_select.html", context)


# staff update stautus.
def StaffUpdateStatus(request, id):
    user = request.user
    try:
        user_role = user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")

    request_asset = get_object_or_404(AssetRequest, id=id)

    asset = request_asset.asset

    if request.method == "POST":
        new_status = request.POST.get("status")

        if new_status == "DEPLOYED":
            request_asset.status = new_status
            request_asset.save(update_fields=["status"])
            asset.status = new_status
            asset.save(update_fields=["status"])

        if new_status == "ASSIGNED":
            request_asset.status = new_status
            request_asset.save(update_fields=["status"])
            asset.status = new_status
            asset.save(update_fields=["status"])

        if new_status == "FAULTY":
            request_asset.status = new_status
            request_asset.save(update_fields=["status"])
            asset.status = new_status
            asset.save(update_fields=["status"])

        if new_status == "REPAIR":
            request_asset.status = new_status
            request_asset.save(update_fields=["status"])
            asset.status = new_status
            asset.assigned_to = None
            asset.save(update_fields=["status", "assigned_to"])

        return redirect("ams:staff_assets")

    view_name = request.resolver_match.view_name
    if view_name == "ams:staff_update_status" and user_role == "User":
        return redirect("ams:staff_assets")
    raise PermissionDenied("You are not authorized to view this page.")


# asset success.
def AssetSuccessView(request):
    if request.user.role == "Admin":
        redirect_url = reverse("ams:admin_dashboard")
    else:
        redirect_url = reverse("ams:staff_dashboard")

    return render(request, "asset_success.html", {"redirect_url": redirect_url})
