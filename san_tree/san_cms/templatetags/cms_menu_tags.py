from django import template

register = template.Library()

@register.inclusion_tag('san_cms/cms_menu.html', takes_context=True)
def cms_menu(context):
    from django.urls import reverse
    request = context['request']
    if request.user.role == 'User':
        return {
            'menu_items': [
                {'icon': '<i class="fa-solid fa-tv"></i>', 'label': 'Dashboard', 'url': reverse('cms:staff_dashboard')},
                {'icon': '<i class="fa-regular fa-flag"></i>', 'label': 'Complaints', 'url': reverse('cms:staff_complaints_history')},
                {'icon': '<i class="fa-solid fa-list-check"></i>', 'label': 'Tasks', 'url': reverse('cms:staff_assigned_tasks')},
                {'icon': '<i class="fa-solid fa-user"></i>', 'label': 'Profile', 'url': reverse('cms:staff_profile')},
            ]
        }
    else:
        return {
            'menu_items': [
                {'icon': '<i class="fa-solid fa-tv"></i>', 'label': 'Dashboard', 'url': reverse('cms:admin_dashboard')},
                {'icon': '<i class="fa-regular fa-flag"></i>', 'label': 'Complaints', 'url': reverse('cms:incharge_complaints_history')},
                {'icon': '<i class="fa-solid fa-hourglass-start"></i>', 'label': 'Review', 'url': reverse('cms:review_complaints')},
                {'icon': '<i class="fa-solid fa-list-check"></i>', 'label': 'Tasks', 'url': reverse('cms:assigned_complaint')},
                {'icon': '<i class="fa-solid fa-user-tie"></i>', 'label': 'Profile', 'url': reverse('cms:admin_profile')},
            ]
        }
