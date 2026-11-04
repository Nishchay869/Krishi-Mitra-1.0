from django import template

from accounts.localization import ui_text

register = template.Library()
register.filter('ui_text', ui_text)


@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(str(key)) or dictionary.get(key)
    return None

