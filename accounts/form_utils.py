from django import forms
from django.forms.utils import pretty_name
from django.utils.translation import gettext_lazy as _


class BootstrapFormMixin:
    """Add Bootstrap 5 classes to every widget, plus is-invalid on fields with errors."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.label = _(field.label or pretty_name(name))
            field.help_text = _(field.help_text) if field.help_text else field.help_text
            field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'

    def full_clean(self):
        # Runs lazily on first access to .errors, i.e. after subclasses finish configuring fields.
        super().full_clean()
        for name in self.errors:
            if name in self.fields:
                self.fields[name].widget.attrs['class'] += ' is-invalid'
