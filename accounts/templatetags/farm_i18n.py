from django import template

from accounts.localization import ui_text

register = template.Library()
register.filter('ui_text', ui_text)
