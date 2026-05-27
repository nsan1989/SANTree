from .menus import MENU_STRUCTURE


def sidebar_menu(request):
    user = request.user
    if not user.is_authenticated:
        return {}

    role = getattr(user, "role", "user").lower()
    current_app = request.resolver_match.app_name if request.resolver_match else None
    menu_role = role

    app_menus = MENU_STRUCTURE.get(current_app, {})
    # If an app defines transport-specific admin menu, route admin users by department.
    if role == "admin" and "transport_admin" in app_menus:
        department_name = (
            getattr(getattr(user, "department", None), "name", "") or ""
        ).strip().lower()
        menu_role = "transport_admin" if department_name == "transport" else "admin"

    menu = app_menus.get(menu_role, app_menus.get(role, []))

    return {"sidebar_menu": menu}
