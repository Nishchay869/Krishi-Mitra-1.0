"""Convert recommended nutrient application rates to product masses.

Grades and nutrient accounting: IFDC Fertilizer Bulk Blending Guide (2022), p27.
https://ifdc.org/wp-content/uploads/2023/04/West-Africa-Fertilizer-Bulk-Blending-Manual-November-2022-Edition.pdf
Inputs are fertilizer recommendations, never raw soil nutrient measurements.
"""
from decimal import Decimal


def calculate_fertilizer(*, nitrogen, phosphorus, potassium, area, area_unit):
    values = [Decimal(str(value)) for value in (nitrogen, phosphorus, potassium, area)]
    if not all(value.is_finite() for value in values):
        raise ValueError('Values must be finite.')
    n, p, k, size = values
    if min(n, p, k) < 0 or size <= 0:
        raise ValueError('Nutrients must be nonnegative and area must be positive.')
    if area_unit not in ('ha', 'acre', 'gunta'):
        raise ValueError('Unknown area unit.')
    hectares = size * {'ha': Decimal(1), 'acre': Decimal('0.40468564224'),
                       'gunta': Decimal('0.010117141056')}[area_unit]
    return {'area_ha': hectares, **_product_masses(n, p, k, hectares)}


def calculate_tree_fertilizer(*, nitrogen, phosphorus, potassium, tree_count):
    values = [Decimal(str(value)) for value in (nitrogen, phosphorus, potassium, tree_count)]
    if not all(value.is_finite() for value in values):
        raise ValueError('Values must be finite.')
    n, p, k, count = values
    if min(n, p, k) < 0 or count < 1 or count != count.to_integral_value():
        raise ValueError('Use nonnegative nutrient rates and a positive whole tree count.')
    # Rates are grams/tree; product masses remain kg for consistent farm totals.
    return {'tree_count': int(count), **_product_masses(
        n / 1000, p / 1000, k / 1000, count)}


PRODUCTS = {
    'MOP': {'name': 'MOP (0–0–60)', 'short_name': 'MOP', 'grade': '0–0–60', 'bag_kg': 50},
    'TSP': {'name': 'TSP (0–46–0)', 'short_name': 'TSP', 'grade': '0–46–0', 'bag_kg': 50},
    'DAP': {'name': 'DAP (18–46–0)', 'short_name': 'DAP', 'grade': '18–46–0', 'bag_kg': 50},
    'UREA': {'name': 'Urea (46–0–0)', 'short_name': 'Urea', 'grade': '46–0–0', 'bag_kg': 45},
}
COMBINATIONS = {'tsp': ('MOP/TSP/Urea', ('MOP', 'TSP', 'UREA')),
                'dap': ('DAP/MOP/Urea', ('DAP', 'MOP', 'UREA'))}


def combination_masses(n, p, k, multiplier, combination_id):
    title, codes = COMBINATIONS[combination_id]
    phosphate = p / Decimal('0.46')
    supplied_n = phosphate * Decimal('0.18') if combination_id == 'dap' else Decimal(0)
    masses = {'MOP': k / Decimal('0.60'), 'TSP': phosphate, 'DAP': phosphate,
              'UREA': max(Decimal(0), n - supplied_n) / Decimal('0.46')}
    products = []
    for code in codes:
        total = masses[code] * multiplier
        products.append(dict(PRODUCTS[code], code=code, per_unit=masses[code], total=total,
                             bags=total / PRODUCTS[code]['bag_kg']))
    return {'id': combination_id, 'title': title, 'products': products,
            'excess_n_per_unit': max(Decimal(0), supplied_n - n),
            'excess_n_total': max(Decimal(0), supplied_n - n) * multiplier}


def _product_masses(n, p, k, multiplier):
    combinations = [combination_masses(n, p, k, multiplier, key) for key in COMBINATIONS]
    dap = combinations[1]
    # Retain the original DAP calculation contract for callers.
    products = sorted(dap['products'], key=lambda item: ('DAP', 'UREA', 'MOP').index(item['code']))
    return {'products': products, 'excess_n_per_unit': dap['excess_n_per_unit'],
            'excess_n_total': dap['excess_n_total'], 'combinations': combinations}


def calculate_plant_fertilizer(*, nitrogen, phosphorus, potassium, plant_count, area, area_unit):
    """Per-plant references require actual count; field area never implies density."""
    tree_result = calculate_tree_fertilizer(nitrogen=nitrogen, phosphorus=phosphorus,
                                           potassium=potassium, tree_count=plant_count)
    area_result = calculate_fertilizer(nitrogen=0, phosphorus=0, potassium=0,
                                       area=area, area_unit=area_unit)
    tree_result['plant_count'] = tree_result.pop('tree_count')
    tree_result['area_ha'] = area_result['area_ha']
    return tree_result
