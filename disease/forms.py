from django import forms

from accounts.form_utils import BootstrapFormMixin

MAX_UPLOAD_MB = 5


class LeafImageForm(BootstrapFormMixin, forms.Form):
    image = forms.ImageField(
        help_text='Clear photo of a single leaf (JPG/PNG, max 5 MB).',
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}),
    )

    crop = forms.CharField(label='Crop / plant name', required=False, max_length=100,
                           help_text='Optional, but helps check the plant identity.')
    location = forms.CharField(label='Village / district / state', required=False, max_length=200)
    notes = forms.CharField(label='What have you noticed?', required=False, max_length=1000,
                            widget=forms.Textarea(attrs={'rows': 3}),
                            help_text='Growth stage, how long symptoms have been present, spread, recent weather, and previous treatments.')

    def clean_image(self):
        image = self.cleaned_data['image']
        if image.size > MAX_UPLOAD_MB * 1024 * 1024:
            raise forms.ValidationError(f'Image must be under {MAX_UPLOAD_MB} MB.')
        return image
