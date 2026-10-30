"""Translate display labels without changing model inputs, user data, or source URLs."""
from django.utils.translation import gettext


def ui_text(value):
    text = str(value) if value is not None else ''
    from disease.treatments import GENERAL_HYGIENE
    suffix = ' ' + GENERAL_HYGIENE
    if text.endswith(suffix):
        return gettext(text[:-len(suffix)]) + ' ' + gettext(GENERAL_HYGIENE)
    translated = gettext(text)
    if translated == text:
        translated = gettext(text.title())
        if translated == text.title():
            return text
    return translated
