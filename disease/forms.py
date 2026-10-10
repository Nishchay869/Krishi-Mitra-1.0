from django import forms

from accounts.form_utils import BootstrapFormMixin

MAX_UPLOAD_MB = 5


class LeafImageForm(BootstrapFormMixin, forms.Form):
    image = forms.ImageField(
        help_text='Clear photo of a single leaf (JPG/PNG, max 5 MB).',
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}),
    )

    def clean_image(self):
        image = self.cleaned_data['image']
        if image.size > MAX_UPLOAD_MB * 1024 * 1024:
            raise forms.ValidationError(f'Image must be under {MAX_UPLOAD_MB} MB.')
        return image
