"""Actionable advice for PlantVillage classes (spec §3.2).

Keys are matched against the normalized disease part of the class name, so both
"Tomato___Late_blight" and "Tomato_Late_blight" folder spellings resolve.
"""

GENERAL_HYGIENE = 'Remove and destroy badly affected leaves, avoid overhead watering, and keep good spacing for airflow.'

TREATMENTS = {
    'apple scab': 'Spray captan 50% wettable powder (50 WP) at 2.5 grams per litre of water or mancozeb 75% wettable powder (75 WP) at 2.5 grams per litre of water from green-tip stage at 10-14 day intervals in wet weather. Rake and destroy fallen leaves.',
    'black rot': 'Prune out cankers and mummified fruit; spray captan or mancozeb at 2.5 grams per litre of water during bloom and fruit set in wet periods.',
    'cedar apple rust': 'Remove nearby juniper/cedar hosts where possible; spray mancozeb at 2.5 grams per litre of water or a recommended triazole fungicide from pink bud stage.',
    'powdery mildew': 'Spray wettable sulphur 80% (80 WP) at 2-3 grams per litre of water or a recommended triazole such as hexaconazole 5% emulsifiable concentrate (5 EC) at 1 ml per litre of water. Avoid excess nitrogen (urea).',
    'cercospora leaf spot gray leaf spot': 'Use resistant hybrids and crop rotation; spray mancozeb at 2.5 grams per litre of water or propiconazole 25% emulsifiable concentrate (25 EC) at 1 ml per litre of water at first symptoms.',
    'common rust': 'Use resistant hybrids; spray mancozeb at 2.5 grams per litre of water at early pustule appearance if disease is spreading.',
    'northern leaf blight': 'Use resistant hybrids and rotate crops; spray mancozeb at 2.5 grams per litre of water or propiconazole at 1 ml per litre of water at early symptoms.',
    'esca black measles': 'No curative spray. Prune infected wood in dry weather, seal pruning wounds, and remove severely affected vines.',
    'leaf blight isariopsis leaf spot': 'Spray mancozeb at 2.5 grams per litre of water or copper oxychloride 50% wettable powder (50 WP) at 3 grams per litre of water; remove infected leaves.',
    'haunglongbing citrus greening': 'No cure. Remove and destroy infected trees, control the citrus psyllid vector (e.g. imidacloprid as per label), and plant certified disease-free saplings.',
    'bacterial spot': 'Use disease-free seed/transplants; spray copper oxychloride 50% wettable powder (50 WP) at 3 grams per litre of water, optionally with streptocycline at 0.1 grams per litre of water where permitted. Avoid working with wet plants.',
    'early blight': 'Spray mancozeb 75% wettable powder (75 WP) at 2.5 grams per litre of water or chlorothalonil at 2 grams per litre of water at 10-day intervals from first symptoms; remove lower infected leaves and rotate crops.',
    'late blight': 'Spray mancozeb 75% wettable powder (75 WP) at 2.5 grams per litre of water preventively; at first symptoms use cymoxanil + mancozeb at 3 grams per litre of water or metalaxyl + mancozeb at 2.5 grams per litre of water. Destroy infected plants.',
    'leaf scorch': 'Remove infected leaves after harvest, avoid overhead irrigation, and spray captan or a recommended fungicide during wet periods.',
    'leaf mold': 'Improve ventilation and reduce humidity (especially in polyhouses); spray mancozeb at 2.5 grams per litre of water or chlorothalonil at 2 grams per litre of water.',
    'septoria leaf spot': 'Remove lower infected leaves, mulch to prevent soil splash, and spray mancozeb at 2.5 grams per litre of water or chlorothalonil at 2 grams per litre of water.',
    'spider mites two-spotted spider mite': 'Spray water on leaf undersides, use neem oil at 5 ml per litre of water; if severe use a recommended acaricide such as spiromesifen 22.9% suspension concentrate (22.9 SC) at 0.8 ml per litre of water as per label.',
    'target spot': 'Remove infected lower leaves, improve airflow, and spray chlorothalonil at 2 grams per litre of water or mancozeb at 2.5 grams per litre of water.',
    'tomato yellow leaf curl virus': 'No cure. Uproot infected plants early, use yellow sticky traps and neem oil to control whitefly vectors, grow seedlings under insect-proof nets, and use tolerant varieties.',
    'tomato mosaic virus': 'No cure. Remove infected plants, disinfect tools and hands, avoid tobacco use near plants, and use virus-free seed.',
}

HEALTHY_ADVICE = 'The leaf looks healthy. Continue regular monitoring, balanced fertilization and field hygiene.'


def _normalize(text):
    return ' '.join(text.replace('_', ' ').replace('(', ' ').replace(')', ' ').replace(',', ' ').lower().split())


def parse_class(class_name):
    """Split a PlantVillage class name into (plant, disease)."""
    if '___' in class_name:
        plant, disease = class_name.split('___', 1)
    else:
        plant, _, disease = class_name.partition('_')
    plant = ' '.join(plant.replace('_', ' ').replace(',', '').split())
    return plant[:1].upper() + plant[1:], _normalize(disease)


def advice_for(class_name):
    plant, disease = parse_class(class_name)
    healthy = disease == 'healthy'
    if healthy:
        treatment = HEALTHY_ADVICE
    else:
        treatment = next((t for key, t in TREATMENTS.items() if key in disease or disease in key), None)
        treatment = treatment or 'Consult your local Krishi Vigyan Kendra (KVK) for a confirmed diagnosis and spray schedule.'
        treatment = f'{treatment} {GENERAL_HYGIENE}'
    return {
        'plant': plant,
        'disease': 'Healthy' if healthy else disease.capitalize(),
        'is_healthy': healthy,
        'treatment': treatment,
        'source': 'ICAR / State Agricultural University plant protection recommendations',
    }
