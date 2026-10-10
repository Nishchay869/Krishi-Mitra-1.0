"""Actionable advice for PlantVillage classes (spec §3.2).

Keys are matched against the normalized disease part of the class name, so both
"Tomato___Late_blight" and "Tomato_Late_blight" folder spellings resolve.
"""

GENERAL_HYGIENE = 'Remove and destroy badly affected leaves, avoid overhead watering, and keep good spacing for airflow.'

TREATMENTS = {
    'apple scab': 'Spray captan 50 WP (2.5 g/L) or mancozeb 75 WP (2.5 g/L) from green-tip stage at 10-14 day intervals in wet weather. Rake and destroy fallen leaves.',
    'black rot': 'Prune out cankers and mummified fruit; spray captan or mancozeb (2.5 g/L) during bloom and fruit set in wet periods.',
    'cedar apple rust': 'Remove nearby juniper/cedar hosts where possible; spray mancozeb (2.5 g/L) or a recommended triazole fungicide from pink bud stage.',
    'powdery mildew': 'Spray wettable sulphur 80 WP (2-3 g/L) or a recommended triazole such as hexaconazole 5 EC (1 ml/L). Avoid excess nitrogen.',
    'cercospora leaf spot gray leaf spot': 'Use resistant hybrids and crop rotation; spray mancozeb (2.5 g/L) or propiconazole 25 EC (1 ml/L) at first symptoms.',
    'common rust': 'Use resistant hybrids; spray mancozeb (2.5 g/L) at early pustule appearance if disease is spreading.',
    'northern leaf blight': 'Use resistant hybrids and rotate crops; spray mancozeb (2.5 g/L) or propiconazole (1 ml/L) at early symptoms.',
    'esca black measles': 'No curative spray. Prune infected wood in dry weather, seal pruning wounds, and remove severely affected vines.',
    'leaf blight isariopsis leaf spot': 'Spray mancozeb (2.5 g/L) or copper oxychloride 50 WP (3 g/L); remove infected leaves.',
    'haunglongbing citrus greening': 'No cure. Remove and destroy infected trees, control the citrus psyllid vector (e.g. imidacloprid as per label), and plant certified disease-free saplings.',
    'bacterial spot': 'Use disease-free seed/transplants; spray copper oxychloride 50 WP (3 g/L), optionally with streptocycline (0.1 g/L) where permitted. Avoid working with wet plants.',
    'early blight': 'Spray mancozeb 75 WP (2.5 g/L) or chlorothalonil (2 g/L) at 10-day intervals from first symptoms; remove lower infected leaves and rotate crops.',
    'late blight': 'Spray mancozeb 75 WP (2.5 g/L) preventively; at first symptoms use cymoxanil + mancozeb (3 g/L) or metalaxyl + mancozeb (2.5 g/L). Destroy infected plants.',
    'leaf scorch': 'Remove infected leaves after harvest, avoid overhead irrigation, and spray captan or a recommended fungicide during wet periods.',
    'leaf mold': 'Improve ventilation and reduce humidity (especially in polyhouses); spray mancozeb (2.5 g/L) or chlorothalonil (2 g/L).',
    'septoria leaf spot': 'Remove lower infected leaves, mulch to prevent soil splash, and spray mancozeb (2.5 g/L) or chlorothalonil (2 g/L).',
    'spider mites two-spotted spider mite': 'Spray water on leaf undersides, use neem oil (5 ml/L); if severe use a recommended acaricide such as spiromesifen 22.9 SC (0.8 ml/L) as per label.',
    'target spot': 'Remove infected lower leaves, improve airflow, and spray chlorothalonil (2 g/L) or mancozeb (2.5 g/L).',
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
