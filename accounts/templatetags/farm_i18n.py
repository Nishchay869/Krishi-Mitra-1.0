from django import template

from accounts.localization import ui_text

register = template.Library()
register.filter('ui_text', ui_text)


@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(str(key)) or dictionary.get(key)
    return None



@register.filter
def short_ago(value):
    """'2 hours ago' / '3 days ago': one unit only (timesince gives '3 days, 4 hours')."""
    if not value:
        return ''
    from django.utils.timesince import timesince
    return f'{timesince(value, depth=1)} ago'
