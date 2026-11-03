from decimal import Decimal
from django import forms
from django.utils.translation import gettext_lazy as _

from accounts.form_utils import BootstrapFormMixin
from accounts.localization import ui_text

from .predictor import FIELD_RANGES


def _field(name, label):
    lo, hi = FIELD_RANGES[name]
    return forms.FloatField(label=label, min_value=lo, max_value=hi,
                            widget=forms.NumberInput(attrs={'step': 'any'}))


class CropForm(BootstrapFormMixin, forms.Form):
    N = _field('N', 'Nitrogen (N, kg/ha)')
    P = _field('P', 'Phosphorus (P, kg/ha)')
    K = _field('K', 'Potassium (K, kg/ha)')
    temperature = _field('temperature', 'Temperature (°C)')
    humidity = _field('humidity', 'Relative humidity (%)')
    ph = _field('ph', 'Soil pH')
    rainfall = _field('rainfall', 'Rainfall (mm)')


class YieldForm(BootstrapFormMixin, forms.Form):
    """Choices come from the trained model so farmers can only pick crops/states it knows."""
    crop = forms.ChoiceField()
    season = forms.ChoiceField()
    state = forms.ChoiceField()
    rainfall = forms.FloatField(label='Expected annual rainfall (mm)', min_value=0, max_value=6000,
                                widget=forms.NumberInput(attrs={'step': 'any'}))
    area_ha = forms.FloatField(label='Your farm area (hectares, optional)', required=False, min_value=0.01,
                               max_value=1000, widget=forms.NumberInput(attrs={'step': 'any'}),
                               help_text='1 acre = 0.405 ha. Used to estimate total production.')

    def __init__(self, *args, bundle, **kwargs):
        super().__init__(*args, **kwargs)
        for name, key in (('crop', 'crops'), ('season', 'seasons'), ('state', 'states')):
            self.fields[name].choices = [('', _('— select —'))] + [(v, ui_text(v)) for v in bundle[key]]


class FertilizerForm(BootstrapFormMixin, forms.Form):
    crop_preset = forms.ChoiceField(required=False, widget=forms.HiddenInput)
    planting_type = forms.ChoiceField(choices=[('plants', 'Plants'), ('trees', 'Trees')],
                                      widget=forms.HiddenInput)
    nitrogen = forms.DecimalField(label='Recommended nitrogen (N, kg/ha)', min_value=0,
                                   max_value=1000, max_digits=8, decimal_places=3)
    phosphorus = forms.DecimalField(label='Recommended phosphate (P2O5, kg/ha)', min_value=0,
                                     max_value=1000, max_digits=8, decimal_places=3)
    potassium = forms.DecimalField(label='Recommended potash (K2O, kg/ha)', min_value=0,
                                    max_value=1000, max_digits=8, decimal_places=3)
    area = forms.DecimalField(label='Field size', min_value=Decimal('0.001'), max_value=100000,
                               max_digits=12, decimal_places=3)
    area_unit = forms.ChoiceField(label='Area unit', choices=[('ha', _('Hectares')), ('acre', _('Acres')), ('gunta', _('Gunta'))])
    tree_count = forms.IntegerField(label='Number of trees', min_value=1, max_value=1000000)
    plant_count = forms.IntegerField(label='Plants in this field', min_value=1, max_value=100000000)

    def __init__(self, *args, planting_type='plants', preset=None, **kwargs):
        super().__init__(*args, **kwargs)
        from .fertilizer_presets import get_effective_presets, preset_label
        presets = get_effective_presets()
        self.fields['crop_preset'].choices = [(key, preset_label(value)) for key, value in presets.items()
                                                if value['mode'] == planting_type]
        per_plant = preset is not None and preset.get('basis') == 'plant'
        if not per_plant:
            del self.fields['plant_count']
        elif preset.get('count_pits'):
            self.fields['plant_count'].label = _('Planting pits in this field')
        if planting_type == 'trees':
            del self.fields['area']
            del self.fields['area_unit']
            for name, label in (
                ('nitrogen', 'Recommended nitrogen (N, grams/tree)'),
                ('phosphorus', 'Recommended phosphate (P2O5, grams/tree)'),
                ('potassium', 'Recommended potash (K2O, grams/tree)'),
            ):
                self.fields[name] = forms.DecimalField(
                    label=_(label), min_value=0, max_value=10000,
                    max_digits=8, decimal_places=3,
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
                )
        else:
            del self.fields['tree_count']
            if per_plant:
                for name, label in (('nitrogen', 'Recommended nitrogen (N, grams/plant)'),
                                    ('phosphorus', 'Recommended phosphate (P2O5, grams/plant)'),
                                    ('potassium', 'Recommended potash (K2O, grams/plant)')):
                    if preset.get('count_pits'):
                        label = {'nitrogen':'N (g/pit)',
                                 'phosphorus':'P2O5 (g/pit)',
                                 'potassium':'K2O (g/pit)'}[name]
                    self.fields[name] = forms.DecimalField(label=_(label), min_value=0,
                        max_value=10000, max_digits=8, decimal_places=3,
                        widget=forms.NumberInput(attrs={'class':'form-control','step':'0.001'}))
