from .menus import MENU_STRUCTURE

def sidebar_menu(request):
    user = request.user
    if not user.is_authenticated:
        return {}

    role = getattr(user, "role", "user").lower()

    current_app = request.resolver_match.app_name if request.resolver_match else None

    menu = MENU_STRUCTURE.get(current_app, {}).get(role, [])

    return {"sidebar_menu": menu}
