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
            {"name": "Schedule", "url_name": "srm:schedule", "view_name":"ShiftSchedule", "icon": "fa-solid fa-calender"},
            {"name": "Service", "url_name": "srm:admin_service", "view_name":"AllServiceView", "icon": "fa-solid fa-wheelchair"}
        ],
        'user': [
            {"name": "Dashboard", "url_name": "srm:staff_dashboard", "view_name":"StaffDashboard", "icon": "fa-solid fa-chart-line"},
            {"name": "Service", "url_name": "srm:staff_service", "view_name":"AllServiceView", "icon": "fa-solid fa-wheelchair"}
        ]
    },
}
