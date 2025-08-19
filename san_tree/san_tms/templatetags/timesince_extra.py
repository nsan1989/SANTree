from django import template

register = template.Library()

@register.filter
def duration_display(td):
    if not td:
        return "--"
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"
