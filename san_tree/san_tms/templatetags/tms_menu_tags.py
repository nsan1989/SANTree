from django import template

register = template.Library()

@register.inclusion_tag('san_tms/tms_menu.html', takes_context=True)
def tms_menu(context):
    from django.urls import reverse
    request = context['request']
    if request.user.role == 'User':
        return {
            'menu_items': [
                {'icon': '<i class="fa-solid fa-tv"></i>', 'label': 'Dashboard', 'url': reverse('tms:staff_dashboard')},
                {'icon': '<i class="fa-solid fa-list-check"></i>', 'label': 'My Tasks', 'url': reverse('tms:my_tasks')},
                {'icon': '<i class="fa-solid fa-user"></i>', 'label': 'Profile', 'url': reverse('tms:staff_profile')},
            ]
        }
    else:
        return {
            'menu_items': [
                {'icon': '<i class="fa-solid fa-tv"></i>', 'label': 'Dashboard', 'url': reverse('tms:admin_dashboard')},
                {'icon': '<i class="fa-solid fa-list-check"></i>', 'label': 'Tasks', 'url': reverse('tms:tasks')},
                {'icon': '<i class="fa-solid fa-user-tie"></i>', 'label': 'Profile', 'url': reverse('tms:admin_profile')},
            ]
        }
