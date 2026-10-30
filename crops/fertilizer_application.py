"""Nutrient-equivalent stage calculations from linked regional references.

All ratios are N, P2O5, K2O fractions of the preset total. Product substitutions
are arithmetic equivalents, not evidence of agronomic interchangeability.
"""
from decimal import Decimal
from fractions import Fraction

from .fertilizer import combination_masses

STAGES = {
    'tomato': [('At planting', ('1/2', '1', '1')), ('30 days after planting', ('1/2', '0', '0'))],
    'potato': [('At planting', ('1/2', '1/2', '1/2')), ('30 days after sowing', ('1/2', '1/2', '1/2'))],
    'okra': [('At sowing', ('1/2', '1', '1')), ('30 days after sowing', ('1/2', '0', '0'))],
    'onion': [('At sowing', ('1/2', '1', '1')), ('30 days after sowing', ('1/2', '0', '0'))],
    'carrot': [('At sowing', ('2/3', '2/3', '2/3')), ('45 days after sowing', ('1/3', '1/3', '1/3'))],
    'taro': [('At planting', ('1/2', '1/2', '1/2')), ('45 days after planting', ('1/2', '1/2', '1/2'))],
    'rice': [('At planting', ('1/4', '1', '1/4')), ('Active tillering', ('1/4', '0', '1/4')),
             ('Panicle initiation', ('1/4', '0', '1/4')), ('Heading', ('1/4', '0', '1/4'))],
    'wheat': [('At sowing', ('1/2', '1', '1')), ('Crown root initiation (15–20 days after sowing)', ('1/2', '0', '0'))],
    'Mango': [('September–October', ('1', '1', '1'))],
    'Coconut': [('June–July', ('1/2', '1/2', '1/2')), ('December–January', ('1/2', '1/2', '1/2'))],
    'cucumber': [('Before sowing', ('0', '3/4', '0')),
                 ('Crop establishment (days 1–10)', ('1/10', '1/20', '1/10')),
                 ('Vegetative growth (days 11–30)', ('3/10', '3/40', '3/10')),
                 ('Flower initiation to first picking (days 31–50)', ('3/10', '3/40', '1/5')),
                 ('Harvesting (days 51–90)', ('3/10', '1/20', '2/5'))],
}


def application_stages(preset_key, preset, inputs, result, combination_id, customized=False):
    if customized:
        return {'stages': [], 'unavailable': 'Edited nutrient totals need a locally confirmed application split.'}
    if result['excess_n_total'] and combination_id == 'dap':
        return {'stages': [], 'unavailable': 'DAP exceeds the nitrogen target. Choose the TSP combination or ask an agronomist for another phosphorus source.'}
    schedule = preset.get('stages') or STAGES.get(preset_key, STAGES.get(preset['crop']))
    if not schedule:
        return {'stages': [], 'unavailable': 'An application schedule is not available for this crop.'}
    tree = preset['mode'] == 'trees'
    per_plant = preset.get('basis') == 'plant'
    multiplier = (Decimal(inputs['tree_count']) if tree else
                  Decimal(inputs['plant_count']) if per_plant else result['area_ha'])
    rates = [Decimal(inputs[key]) / (1000 if tree or per_plant else 1)
             for key in ('nitrogen', 'phosphorus', 'potassium')]
    allocated = [Decimal(0)] * 3
    stages = []
    for index, (label, fractions) in enumerate(schedule):
        targets = []
        for nutrient, fraction in enumerate(fractions):
            ratio = Fraction(fraction)
            target = (rates[nutrient] - allocated[nutrient] if index == len(schedule) - 1
                      else rates[nutrient] * Decimal(ratio.numerator) / Decimal(ratio.denominator))
            targets.append(target)
            allocated[nutrient] += target
        stage = combination_masses(*targets, multiplier, combination_id)
        if stage['excess_n_total'] > Decimal('0.000000001'):
            return {'stages': [], 'unavailable': 'DAP supplies too much nitrogen in an early stage to match this reference split. Use the TSP stage breakdown or confirm a different split with an agronomist.'}
        stages.append({'label': label, 'products': stage['products']})
    return {'stages': stages, 'unavailable': '', 'fertigation': preset_key == 'cucumber'}
