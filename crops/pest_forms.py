from uuid import uuid4
from django import forms
from django.utils.text import slugify
from . import pests
from .models import PestEntry


class PestEntryForm(forms.ModelForm):
    crop_slug = forms.ChoiceField(label='Crop')
    stages = forms.MultipleChoiceField(label='Growth stages',
        choices=[(slug, name) for slug, name, *_ in pests.STAGES],
        widget=forms.CheckboxSelectMultiple)
    kind = forms.ChoiceField(label='Issue type', choices=[(kind, kind) for kind in pests.KINDS])

    class Meta:
        model = PestEntry
        fields = ['crop_slug', 'title', 'kind', 'stages', 'symptoms', 'more_info',
                  'treat_now', 'organic_control', 'chemical_control', 'preventive_measures',
                  'photo', 'photo_caption', 'source_url']
        labels = {'title': 'Pest or disease name', 'treat_now': 'Treat now',
                  'photo': 'Upload photograph', 'photo_caption': 'Photograph caption'}
        widgets = {name: forms.Textarea(attrs={'rows': 5}) for name in
                   ['symptoms', 'more_info', 'treat_now', 'organic_control',
                    'chemical_control', 'preventive_measures']}
        help_texts = {'photo': 'JPG, PNG or WebP, up to 5 MB. Upload a photograph you can use.',
                      'chemical_control': 'Include the applicable crop, product label, dose and harvest interval when relevant.',
                      'source_url': 'Optional supporting reference for these details.'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['crop_slug'].choices = [(c['slug'], c['name']) for c in pests.crops()]
        if self.instance.issue_slug:
            self.fields['crop_slug'].disabled = True
        for name, field in self.fields.items():
            if name != 'stages':
                field.widget.attrs['class'] = 'form-control'
            if isinstance(field, forms.CharField) and isinstance(field.widget, forms.Textarea):
                field.max_length = 20000
                field.widget.attrs['maxlength'] = 20000
        self.fields['photo'].widget.attrs['accept'] = 'image/jpeg,image/png,image/webp'

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and hasattr(photo, 'content_type') and photo.content_type not in {
                'image/jpeg', 'image/png', 'image/webp'}:
            raise forms.ValidationError('Upload a JPG, PNG or WebP photograph.')
        return photo

    def save(self, commit=True):
        entry = super().save(commit=False)
        if not entry.issue_slug:
            entry.issue_slug = f'{slugify(entry.title)[:100] or "issue"}-{uuid4().hex[:8]}'
        if commit:
            entry.save()
        return entry
