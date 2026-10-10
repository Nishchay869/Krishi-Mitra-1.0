from django import forms

from accounts.form_utils import BootstrapFormMixin

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
            self.fields[name].choices = [('', '— select —')] + [(v, v) for v in bundle[key]]
