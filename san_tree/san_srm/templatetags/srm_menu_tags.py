from django import template

register = template.Library()

@register.inclusion_tag('san_srm/srm_menu.html', takes_context=True)
def srm_menu(context):
    from django.urls import reverse
    request = context['request']
    if request.user.role == 'User':
        return {
            'menu_items': [
                {'icon': '<i class="fa-solid fa-tv"></i>', 'label': 'Dashboard', 'url': reverse('srm:staff_dashboard')},
                {'icon': '<i class="fa-solid fa-wheelchair"></i>', 'label': 'Service', 'url': reverse('srm:staff_service')},
                {'icon': '<i class="fa-solid fa-user"></i>', 'label': 'Profile', 'url': reverse('srm:staff_profile')},
            ]
        }
    else:
        return {
            'menu_items': [
                {'icon': '<i class="fa-solid fa-tv"></i>', 'label': 'Dashboard', 'url': reverse('srm:admin_dashboard')},
                {'icon': '<i class="fa-solid fa-wheelchair"></i>', 'label': 'Service', 'url': reverse('srm:admin_service')},
                {'icon': '<i class="fa-solid fa-user-tie"></i>', 'label': 'Profile', 'url': reverse('srm:admin_profile')},
            ]
        }
