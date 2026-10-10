from django import forms


class BootstrapFormMixin:
    """Add Bootstrap 5 classes to every widget, plus is-invalid on fields with errors."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'

    def full_clean(self):
        # Runs lazily on first access to .errors, i.e. after subclasses finish configuring fields.
        super().full_clean()
        for name in self.errors:
            if name in self.fields:
                self.fields[name].widget.attrs['class'] += ' is-invalid'
