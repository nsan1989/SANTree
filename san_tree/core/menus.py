MENU_STRUCTURE = {
    'cms': {
        'admin': [
            {"name": "Dashboard", "url_name": "cms:admin_dashboard", "icon": "fa-solid fa-chart-line"},
            {"name": "Complaints", "url_name": "cms:incharge_complaints_history", "icon": "fa-solid fa-person-circle-exclamation"},
            {"name": "Review", "url_name": "cms:review_complaints", "icon": "fa-solid fa-list-check"},
            {"name": "Tasks", "url_name": "cms:assigned_complaint", "icon": "fa-regular fa-square-check"}
        ],
        'user': [
            {"name": "Dashboard", "url_name": "cms:staff_dashboard", "icon": "fa-solid fa-chart-line"},
            {"name": "Complaints", "url_name": "cms:staff_complaints_history", "icon": "fa-solid fa-person-circle-exclamation"},
            {"name": "Tasks", "url_name": "cms:staff_assigned_tasks", "icon": "fa fa-tasks"}
        ]
    },
    'tms': {
        'admin': [
            {"name": "Dashboard", "url_name": "tms:admin_dashboard", "view_name":"TaskDashboard", "icon": "fa-solid fa-chart-line"},
            {"name": "Tasks", "url_name": "tms:tasks", "view_name":"AllTasks", "icon": "fa-solid fa-person-circle-exclamation"}
        ],
        'user': [
            {"name": "Dashboard", "url_name": "tms:staff_dashboard", "view_name":"TaskDashboard", "icon": "fa-solid fa-chart-line"},
            {"name": "Tasks", "url_name": "tms:my_tasks", "view_name":"MyTasks", "icon": "fa-solid fa-person-circle-exclamation"}
        ]
    },
    'srm': {
        'admin': [
            {"name": "Dashboard", "url_name": "srm:admin_dashboard", "view_name":"AdminDashboard", "icon": "fa-solid fa-chart-line"},
            {"name": "Schedule", "url_name": "srm:schedule", "view_name":"ShiftSchedule", "icon": "fa-solid fa-calendar-days"},
            {"name": "Service", "url_name": "srm:admin_service", "view_name":"AllServiceView", "icon": "fa-solid fa-wheelchair"}
        ],
        'user': [
            {"name": "Dashboard", "url_name": "srm:staff_dashboard", "view_name":"StaffDashboard", "icon": "fa-solid fa-chart-line"},
            {"name": "Schedule", "url_name": "srm:schedule", "view_name":"ShiftSchedule", "icon": "fa-solid fa-calendar-days"},
            {"name": "Service", "url_name": "srm:staff_service", "view_name":"AllServiceView", "icon": "fa-solid fa-wheelchair"}
        ]
    },
    'ams': {
        'admin': [
            {"name": "Dashboard", "url_name": "ams:admin_dashboard", "view_name": "AdminDashboardView", "icon": "fa-solid fa-chart-line"},
            {"name": "Assets", "url_name": "ams:admin_assets", "view_name": "AssetView", "icon": "fa-solid fa-warehouse"},
            {"name": "Licenses", "url_name": "ams:all_licenses", "view_name": "LicenseView", "icon": "fa-solid fa-file-contract"},
            {"name": "Accessories", "url_name": "ams:admin_accessories", "view_name": "AccessoriesView", "icon": "fa-solid fa-keyboard"},
            {"name": "Consumables", "url_name": "ams:admin_consumables", "view_name": "ConsumablesView", "icon": "fa-solid fa-paperclip"},
            {"name": "Components", "url_name": "ams:admin_components", "view_name": "ComponentsView", "icon": "fa-solid fa-microchip"},
            {"name": "Asset Users", "url_name": "ams:admin_asset_users", "view_name": "AssetUsersView", "icon": "fa-solid fa-users"},
            {"name": "Settings", "url_name": None, "view_name": None, "icon": "fa-solid fa-gear", "dropdown_icon": "fa-solid fa-angle-down", 
             "children": [
                {"name": "Assets", "url_name": "ams:add_asset", "view_name": "AddAssetView", "icon": "fa-solid fa-plus"},
                {"name": "Accessory Category", "url_name": "ams:add_asset_category", "view_name": "AddAccessoryCategoryView", "icon": "fa-solid fa-plus"},
                {"name": "Accessory", "url_name": "ams:add_accessory", "view_name": "AddAccessoryView", "icon": "fa-solid fa-plus"},
                {"name": "Components Category", "url_name": "ams:add_component_category", "view_name": "AddComponentCategoryView", "icon": "fa-solid fa-plus"},
                {"name": "Components", "url_name": "ams:add_component", "view_name": "AddAccessoryView", "icon": "fa-solid fa-plus"},
                {"name": "Consumables Category", "url_name": "ams:add_consumable_category", "view_name": "AddConsumableCategoryView", "icon": "fa-solid fa-plus"},
                {"name": "Consumables", "url_name": "ams:add_consumable", "view_name": "AddConsumableView", "icon": "fa-solid fa-plus"},
                {"name": "Licenses", "url_name": "ams:add_license", "view_name": "AddLicenseView", "icon": "fa-solid fa-plus"},
             ]
             },
        ],
        'user': [
            {"name": "Dashboard", "url_name": "ams:staff_dashboard", "view_name": "StaffDashboardView", "icon": "fa-solid fa-chart-line"},
            {"name": "Assets", "url_name": "ams:staff_assets", "view_name": "AssetView", "icon": "fa-solid fa-warehouse"},
#            {"name": "Accessories", "url_name": "ams:staff_accessories", "view_name": "AccessoriesView", "icon": "fa-solid fa-keyboard"},
#            {"name": "Consumables", "url_name": "ams:staff_consumables", "view_name": "ConsumablesView", "icon": "fa-solid fa-paperclip"},
#            {"name": "Components", "url_name": "ams:staff_components", "view_name": "ComponentsView", "icon": "fa-solid fa-microchip"},
#            {"name": "Asset Users", "url_name": "ams:staff_asset_users", "view_name": "AssetUsersView", "icon": "fa-solid fa-users"},
#            {"name": "Settings", "url_name": None, "view_name": None, "icon": "fa-solid fa-gear", 
#             "children": [
#                {"name": "Assets", "url_name": "ams:add_asset", "view_name": "AddAssetView", "icon": "fa-solid fa-plus"},
#                {"name": "Accessory Category", "url_name": "ams:add_asset_category", "view_name": "AddAccessoryCategoryView", "icon": "fa-solid fa-plus"},
#                {"name": "Accessory", "url_name": "ams:add_accessory", "view_name": "AddAccessoryView", "icon": "fa-solid fa-plus"},
#                {"name": "Components Category", "url_name": "ams:add_component_category", "view_name": "AddComponentCategoryView", "icon": "fa-solid fa-plus"},
#                {"name": "Components", "url_name": "ams:add_component", "view_name": "AddAccessoryView", "icon": "fa-solid fa-plus"},
#                {"name": "Consumables Category", "url_name": "ams:add_consumable_category", "view_name": "AddConsumableCategoryView", "icon": "fa-solid fa-plus"},
#                {"name": "Consumables", "url_name": "ams:add_consumable", "view_name": "AddConsumableView", "icon": "fa-solid fa-plus"},
#                {"name": "Licenses", "url_name": "ams:add_license", "view_name": "AddLicenseView", "icon": "fa-solid fa-plus"},
#                ]
#            },
        ]
    },
}
