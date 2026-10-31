"""Actionable advice and agronomic knowledge base for PlantVillage classes (spec §3.2).

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


DISEASE_METADATA = {
    'apple scab': {
        'disease_type': 'fungal',
        'title': 'Apple Scab',
        'summary': 'Apple scab lesions detected. Immediate protective fungicidal intervention and removal of fallen infected leaves recommended.',
        'description': 'Apple scab is caused by the fungus Venturia inaequalis. It produces olive-green to dark velvety spots on leaves and fruit, causing premature leaf drop and cracked, corky fruit deformities.',
        'symptoms': [
            'Olive-green to dark brown velvety spots on upper leaf surfaces',
            'Leaves curl, yellow, and drop prematurely in wet spring periods',
            'Scabby, corky, cracked circular lesions on developing fruits'
        ],
        'immediate_actions': [
            'Rake and safely destroy fallen leaves harboring overwintering fungal spores',
            'Apply protective fungicide spray during wet foliage periods',
            'Prune dense branches to open tree canopy for improved sunlight and airflow'
        ],
        'cultural_control': [
            'Prune annually to maintain an open canopy structure',
            'Avoid overhead sprinkler irrigation that extends leaf wetness',
            'Plant scab-resistant apple cultivars such as Liberty, Enterprise, or Freedom'
        ],
        'biological_control': [
            'Foliar spray of Bacillus subtilis or Trichoderma viride at bud break',
            'Neem seed kernel extract (NSKE 5%) applied preventively'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Mancozeb 75% WP',
                'chemical_group': 'Dithiocarbamate (FRAC M03)',
                'purpose': 'Multi-site contact protectant preventing fungal spore germination.',
                'application_method': 'Foliar spray at 2.5 g per litre of water covering both leaf surfaces.',
                'timing': 'Apply from green-tip stage onward at 10-14 day intervals during wet weather.',
                'precautions': 'Wear protective gear; observe minimum 14-day pre-harvest interval.'
            },
            {
                'active_ingredient': 'Captan 50% WP',
                'chemical_group': 'Phthalimide (FRAC M04)',
                'purpose': 'Broad-spectrum contact fungicide protecting foliage and young fruit.',
                'application_method': 'Foliar spray at 2.5 g per litre of water.',
                'timing': 'Apply during pink bud to petal fall stages before rain.',
                'precautions': 'Do not mix with horticultural oils or alkaline chemicals.'
            }
        ],
        'spray_schedule': [
            'Green tip stage: Mancozeb 75% WP @ 2.5 g/L preventively.',
            'Pink bud stage: Captan 50% WP @ 2.5 g/L if wet weather persists.',
            'Petal fall: Alternate with systemic fungicide if lesions appear.'
        ],
        'resistance_management': [
            'Alternate contact multi-site fungicides with single-site systemic options.',
            'Limit single-site systemic applications to maximum 2 sprays per season.'
        ],
        'prevention': [
            'Collect and compost or burn fallen leaves in autumn.',
            'Ensure adequate tree spacing (4-6 m) for rapid leaf drying.'
        ],
        'follow_up': [
            'Scout trees weekly, especially inner lower canopy leaves after rainfall.',
            'Check developing fruit clusters for early corky spot development.'
        ]
    },
    'black rot': {
        'disease_type': 'fungal',
        'title': 'Black Rot',
        'summary': 'Black rot detected. Prune out cankers and mummified fruit, and apply targeted protective fungicides.',
        'description': 'Black rot is caused by Botryosphaeria obtusa in apples and Guignardia bidwellii in grapes. It produces circular frog-eye leaf lesions and shriveled, mummified black fruit clusters.',
        'symptoms': [
            'Circular frog-eye leaf spots with tan centers and purple-brown margins',
            'Small black pycnidia (fruiting bodies) visible within leaf lesions',
            'Fruit rots quickly, turns black, and shrivels into hard mummies'
        ],
        'immediate_actions': [
            'Prune out and destroy infected twigs, cankers, and dead wood',
            'Remove and destroy all mummified fruit clinging to vines or trees',
            'Apply a protective contact fungicide prior to anticipated rainfall'
        ],
        'cultural_control': [
            'Disinfect pruning tools with 70% alcohol between cuts',
            'Ensure canopy allows good light penetration and air movement',
            'Eradicate wild grapevines and abandoned host trees near orchards'
        ],
        'biological_control': [
            'Apply Bacillus amyloliquefaciens foliar spray early in shoot growth',
            'Trichoderma harzianum wound treatment after pruning'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Mancozeb 75% WP',
                'chemical_group': 'Dithiocarbamate (FRAC M03)',
                'purpose': 'Protective multi-site contact barrier on foliage and fruit.',
                'application_method': 'Foliar spray at 2.5 g per litre of water.',
                'timing': 'Early shoot growth through post-bloom in wet periods.',
                'precautions': 'Do not apply within 14 days of harvest.'
            },
            {
                'active_ingredient': 'Captan 50% WP',
                'chemical_group': 'Phthalimide (FRAC M04)',
                'purpose': 'Contact protectant against ascospore and conidia infection.',
                'application_method': 'Foliar spray at 2.5 g per litre of water.',
                'timing': 'Apply during bloom and fruit set in wet periods.',
                'precautions': 'Avoid tank mixing with sulphur.'
            }
        ],
        'spray_schedule': [
            'Early shoot development: Mancozeb 75% WP @ 2.5 g/L.',
            'Bloom to fruit set: Captan 50% WP @ 2.5 g/L at 10-14 day intervals.',
            'Post-harvest: Remove all remaining mummies.'
        ],
        'resistance_management': [
            'Use multi-site protectants as the foundation of your spray program.'
        ],
        'prevention': [
            'Remove and burn all old mummified fruits during winter pruning.',
            'Maintain balanced vine and tree pruning.'
        ],
        'follow_up': [
            'Inspect foliage and grape clusters weekly throughout warm rainy weather.'
        ]
    },
    'cedar apple rust': {
        'disease_type': 'fungal',
        'title': 'Cedar Apple Rust',
        'summary': 'Cedar apple rust symptoms observed. Remove alternate juniper hosts nearby and spray protective fungicide.',
        'description': 'Caused by Gymnosporangium juniperi-virginianae, this rust fungus alternates between apple trees and eastern red cedar/juniper hosts. It produces bright yellow-orange spots on apple foliage.',
        'symptoms': [
            'Bright yellow-orange circular spots on upper apple leaf surfaces',
            'Raised orange pustules with tiny black dots in lesion centers',
            'Cylindrical tube-like spore structures on lower leaf surfaces'
        ],
        'immediate_actions': [
            'Remove nearby juniper or red cedar trees within 200-500 m if feasible',
            'Prune cedar galls from nearby ornamental junipers before spring rains',
            'Apply protective fungicide from pink bud stage'
        ],
        'cultural_control': [
            'Plant rust-resistant apple cultivars such as Enterprise, Freedom, or Liberty',
            'Avoid locating new orchards near dense juniper hedgerows'
        ],
        'biological_control': [
            'Wettable sulfur spray applied preventively during spring spore release'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Mancozeb 75% WP',
                'chemical_group': 'Dithiocarbamate',
                'purpose': 'Protective foliar shield against basidiospore infection.',
                'application_method': 'Foliar spray at 2.5 g per litre of water.',
                'timing': 'Apply from pink bud through petal fall before rain events.',
                'precautions': 'Adhere strictly to label safety directions.'
            },
            {
                'active_ingredient': 'Myclobutanil 10% WP',
                'chemical_group': 'Triazole (FRAC 3)',
                'purpose': 'Systemic curative action with 72-96 hour kickback activity.',
                'application_method': 'Foliar spray at 0.4 g per litre of water.',
                'timing': 'Apply within 3 days of an infectious rain event.',
                'precautions': 'Limit to maximum 3 sprays per season.'
            }
        ],
        'spray_schedule': [
            'Pink bud stage: Mancozeb 75% WP @ 2.5 g/L.',
            'Petal fall: Myclobutanil 10% WP @ 0.4 g/L if wet weather continues.'
        ],
        'resistance_management': [
            'Rotate triazoles with multi-site contact protectants.'
        ],
        'prevention': [
            'Inspect neighboring cedar trees for brown ball-like galls in winter.'
        ],
        'follow_up': [
            'Inspect apple leaves 10-14 days after petal fall for orange rust lesion emergence.'
        ]
    },
    'powdery mildew': {
        'disease_type': 'fungal',
        'title': 'Powdery Mildew',
        'summary': 'Powdery mildew detected. Apply sulfur or triazole spray, improve aeration, and avoid excess nitrogen.',
        'description': 'Powdery mildew is caused by specialized biotrophic fungi (Podosphaera species). It coats leaves, tender shoots, and buds with a distinct white-to-gray powdery fungal growth, distorting leaves.',
        'symptoms': [
            'White to grayish powdery coating on upper and lower leaf surfaces',
            'Leaves crinkle, curl upwards, and become brittle and discolored',
            'Stunted new shoot elongation and premature leaf defoliation'
        ],
        'immediate_actions': [
            'Prune off and safely destroy heavily infected terminal shoots',
            'Spray wettable sulphur or bio-fungicide at early onset',
            'Avoid excess urea or nitrogenous fertilizer that drives susceptible succulent growth'
        ],
        'cultural_control': [
            'Ensure adequate plant spacing and prune interior canopy to maximize airflow',
            'Provide full sunlight exposure (powdery mildew thrives in shade)',
            'Use drip irrigation to keep foliage dry'
        ],
        'biological_control': [
            'Wettable sulphur (80 WP) @ 2-3 g/L',
            'Potassium bicarbonate (5 g/L) foliar spray with a mild wetting agent',
            'Bacillus subtilis bio-fungicide'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Wettable Sulphur 80% WP',
                'chemical_group': 'Inorganic Sulphur (FRAC M02)',
                'purpose': 'Protective multi-site contact fungicide and miticide.',
                'application_method': 'Foliar spray at 2.5-3 g per litre of water.',
                'timing': 'Apply at first sign of white patches; repeat every 10-12 days.',
                'precautions': 'Do not apply when temperature exceeds 32°C or within 14 days of oil sprays.'
            },
            {
                'active_ingredient': 'Hexaconazole 5% EC',
                'chemical_group': 'Triazole (FRAC 3)',
                'purpose': 'Systemic curative and protective action against powdery mildew mycelium.',
                'application_method': 'Foliar spray at 1 ml per litre of water.',
                'timing': 'Apply when mildew patches begin expanding to new growth.',
                'precautions': 'Do not apply more than 2 consecutive sprays; wear safety gear.'
            }
        ],
        'spray_schedule': [
            'Round 1: Wettable Sulphur 80% WP @ 2.5 g/L at first visible white patches.',
            'Round 2 (10-12 days later): Hexaconazole 5% EC @ 1 ml/L if new shoots are infected.',
            'Round 3: Potassium bicarbonate or bio-fungicide to rotate modes of action.'
        ],
        'resistance_management': [
            'Never apply triazole fungicides repeatedly without alternating with contact sulfur.'
        ],
        'prevention': [
            'Avoid overhead watering and dense, shaded canopies.'
        ],
        'follow_up': [
            'Inspect tender terminal shoots and underside of leaves every 4-5 days.'
        ]
    },
    'cercospora leaf spot gray leaf spot': {
        'disease_type': 'fungal',
        'title': 'Cercospora / Gray Leaf Spot',
        'summary': 'Gray leaf spot detected on maize/corn. Rotate crops and apply foliar fungicide if spreading up the canopy.',
        'description': 'Caused by Cercospora zeae-maydis, gray leaf spot is a major foliar pathogen of maize. It creates characteristic rectangular tan lesions restricted by leaf veins that coalesce and blight entire leaves.',
        'symptoms': [
            'Narrow, distinctly rectangular tan to grayish lesions parallel to leaf veins',
            'Lesions restricted by parallel veins giving a blocky geometric appearance',
            'Extensive leaf blighting progressing from lower canopy upward'
        ],
        'immediate_actions': [
            'Scout lower maize canopy to evaluate disease progression up the plant',
            'Apply systemic fungicide if lesions reach ear leaf before or during silking',
            'Avoid late afternoon sprinkler irrigation'
        ],
        'cultural_control': [
            'Rotate fields with non-host crops like soybean or cotton for 1-2 seasons',
            'Incorporate infected crop residue after harvest to accelerate decomposition',
            'Plant resistant or tolerant maize hybrids'
        ],
        'biological_control': [
            'Seed treatment with Trichoderma harzianum to boost seedling vigor'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Mancozeb 75% WP',
                'chemical_group': 'Dithiocarbamate',
                'purpose': 'Protective foliar shield against airborne spore germination.',
                'application_method': 'Foliar spray at 2.5 g per litre of water.',
                'timing': 'Apply at first detection on lower canopy.',
                'precautions': 'Ensure good spray coverage on both leaf surfaces.'
            },
            {
                'active_ingredient': 'Propiconazole 25% EC',
                'chemical_group': 'Triazole (FRAC 3)',
                'purpose': 'Systemic translaminar protection and curative containment.',
                'application_method': 'Foliar spray at 1 ml per litre of water.',
                'timing': 'Apply between tasseling (VT) and blister stage (R2) if disease is progressing.',
                'precautions': 'Do not apply within 30 days of harvest.'
            }
        ],
        'spray_schedule': [
            'Early detection: Mancozeb @ 2.5 g/L on lower leaves.',
            'Tasseling: Propiconazole 25% EC @ 1 ml/L if lesions reach the ear leaf.'
        ],
        'resistance_management': [
            'Rotate triazole with strobilurin modes of action.'
        ],
        'prevention': [
            'Avoid continuous corn-on-corn cultivation; rotate fields.'
        ],
        'follow_up': [
            'Scout ear leaf and leaves above ear weekly until dough stage.'
        ]
    },
    'common rust': {
        'disease_type': 'fungal',
        'title': 'Common Rust',
        'summary': 'Common rust detected on maize. Monitor pustule spread and apply protective fungicide if spreading.',
        'description': 'Caused by Puccinia sorghi, common rust produces powdery cinnamon-brown pustules on both upper and lower surfaces of maize leaves during cool, humid weather.',
        'symptoms': [
            'Small, circular to elongated cinnamon-brown powdery pustules (uredinia)',
            'Pustules break through epidermal tissue on both upper and lower surfaces',
            'Pustules turn brownish-black late in the season as teliospores form'
        ],
        'immediate_actions': [
            'Scout fields to determine if rust pustules are active on upper leaves',
            'Apply protective spray if rust covers more than 5% of leaf area before silking',
            'Ensure balanced fertilization; avoid excess nitrogen'
        ],
        'cultural_control': [
            'Plant rust-resistant corn hybrids carrying Rp resistance genes',
            'Plant early in the season to escape peak airborne rust spore showers'
        ],
        'biological_control': [
            'Bacillus subtilis bio-fungicide foliar sprays during early vegetative stages'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Mancozeb 75% WP',
                'chemical_group': 'Dithiocarbamate',
                'purpose': 'Contact protective spray against airborne rust urediniospores.',
                'application_method': 'Foliar spray at 2.5 g per litre of water.',
                'timing': 'Apply at early pustule appearance on whorl or lower leaves.',
                'precautions': 'Wear protective equipment.'
            },
            {
                'active_ingredient': 'Azoxystrobin 18.2% + Difenoconazole 11.4% SC',
                'chemical_group': 'Strobilurin + Triazole',
                'purpose': 'Dual systemic curative and protective control against rust fungi.',
                'application_method': 'Foliar spray at 1 ml per litre of water.',
                'timing': 'Apply when rust threatens upper canopy before tasseling.',
                'precautions': 'Do not exceed 2 applications per crop season.'
            }
        ],
        'spray_schedule': [
            'Initial: Mancozeb 75% WP @ 2.5 g/L on early pustules.',
            'Follow-up (10-14 days): Systemic triazole/strobilurin mix if cool, moist weather continues.'
        ],
        'resistance_management': [
            'Do not rely exclusively on single-mode fungicides.'
        ],
        'prevention': [
            'Select certified resistant hybrids and avoid staggered plantings nearby.'
        ],
        'follow_up': [
            'Check upper canopy leaves every 5 days.'
        ]
    },
    'northern leaf blight': {
        'disease_type': 'fungal',
        'title': 'Northern Leaf Blight',
        'summary': 'Northern corn leaf blight detected. Rotate crops and apply fungicide at first symptom.',
        'description': 'Caused by Exserohilum turcicum, northern corn leaf blight produces long, cigar-shaped elliptical grayish-green to tan lesions on maize leaves that lead to extensive blighting.',
        'symptoms': [
            'Long (2.5-15 cm), cigar-shaped elliptical grayish-green to tan lesions',
            'Dark olive fungal sporulation inside lesions in humid conditions',
            'Premature blighting of leaves starting from bottom of plant'
        ],
        'immediate_actions': [
            'Assess lesion development on ear leaf and leaves above ear',
            'Apply protective fungicide spray promptly if conditions are humid and cool',
            'Ensure field drainage to reduce local microclimate humidity'
        ],
        'cultural_control': [
            'Plant resistant hybrids with Ht resistance genes',
            'Practice 2-year crop rotation with non-host crops (pulses, oilseeds)',
            'Bury infected corn residue where conservation tillage permits'
        ],
        'biological_control': [
            'Seed treatment with Trichoderma viride'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Mancozeb 75% WP',
                'chemical_group': 'Dithiocarbamate',
                'purpose': 'Broad-spectrum contact protectant against conidia germination.',
                'application_method': 'Foliar spray at 2.5 g per litre of water.',
                'timing': 'Apply at first detection of cigar-shaped lesions.',
                'precautions': 'Ensure thorough spray coverage on both leaf surfaces.'
            },
            {
                'active_ingredient': 'Propiconazole 25% EC',
                'chemical_group': 'Triazole',
                'purpose': 'Systemic translaminar protection and lesion containment.',
                'application_method': 'Foliar spray at 1 ml per litre of water.',
                'timing': 'Apply prior to tasseling if lesions reach lower canopy.',
                'precautions': 'Observe 30-day pre-harvest interval.'
            }
        ],
        'spray_schedule': [
            'Early spray: Mancozeb 75% WP @ 2.5 g/L.',
            'Repeat (10-14 days): Propiconazole @ 1 ml/L if lesions expand towards ear leaf.'
        ],
        'resistance_management': [
            'Alternate triazoles with multi-site contact protectants.'
        ],
        'prevention': [
            'Rotate away from corn residue; choose certified resistant seed.'
        ],
        'follow_up': [
            'Monitor ear leaf every 4-6 days until dough stage.'
        ]
    },
    'esca black measles': {
        'disease_type': 'fungal',
        'title': 'Esca (Black Measles)',
        'summary': 'Esca (black measles) identified in grape. Prune infected wood during dry weather and protect pruning wounds.',
        'description': 'Esca is a complex grapevine trunk disease caused by fungi including Phaeomoniella chlamydospora and Phaeoacremonium minimum. It creates striking tiger-stripe leaf patterns and black measles spots on berries.',
        'symptoms': [
            'Tiger-stripe interveinal pattern of yellow/red chlorosis and necrosis',
            'Small, dark brown to black spots with purple halos on berries ("measles")',
            'Internal wood necrosis with dark brown streaking and spongy white heart rot'
        ],
        'immediate_actions': [
            'Mark affected vines for delayed winter pruning',
            'Prune infected cordons or trunks down to healthy white wood during dry weather',
            'Immediately apply wound sealant or copper paste on all pruning cuts'
        ],
        'cultural_control': [
            'Delay pruning until late winter when vine sap flow is beginning',
            'Prune only during dry, clear weather to avoid wound infection',
            'Remove and burn dead vines and wood piles outside the vineyard'
        ],
        'biological_control': [
            'Apply Trichoderma-based pruning wound protectant within 24 hours of cutting',
            'Maintain balanced vine vigor without over-irrigation'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Copper Oxychloride Paste',
                'chemical_group': 'Inorganic Copper',
                'purpose': 'Protective barrier coating over large pruning wounds to block fungal entry.',
                'application_method': 'Paint thick paste directly onto pruning cuts > 2 cm diameter.',
                'timing': 'Immediately after pruning cuts are made in dry weather.',
                'precautions': 'Do not apply during wet weather or sap bleeding.'
            }
        ],
        'spray_schedule': [
            'There is no effective foliar curative spray for established internal Esca.',
            'Focus all interventions on wound protection and sanitation during pruning.'
        ],
        'resistance_management': [
            'Use sanitary pruning protocols rather than chemical reliance.'
        ],
        'prevention': [
            'Purchase certified disease-free vine rootstocks.',
            'Sterilize pruning shears between vines using 70% alcohol.'
        ],
        'follow_up': [
            'Monitor marked vines throughout summer for sudden apoplexy or fruit measles.'
        ]
    },
    'leaf blight isariopsis leaf spot': {
        'disease_type': 'fungal',
        'title': 'Isariopsis Leaf Spot',
        'summary': 'Isariopsis leaf spot detected on grape. Spray copper or mancozeb and remove infected leaves.',
        'description': 'Caused by Pseudocercospora clavispora (Isariopsis clavispora), this fungal disease creates reddish-brown angular spots on grape leaves that coalesce and cause severe pre-harvest defoliation.',
        'symptoms': [
            'Large, irregular reddish-brown necrotic spots on upper leaf surfaces',
            'Dark olivaceous-brown velvety fungal tufts on lower leaf surfaces',
            'Severe leaf scorch and premature drop exposing grape bunches to sunburn'
        ],
        'immediate_actions': [
            'Remove and burn heavily spotted fallen leaves',
            'Apply protective contact fungicide covering lower leaf surfaces thoroughly',
            'Prune dense leaf canopies around grape clusters for better ventilation'
        ],
        'cultural_control': [
            'Adopt proper canopy management (shoot positioning and desuckering)',
            'Avoid overhead irrigation or micro-sprinklers inside vine canopy',
            'Collect and destroy vineyard floor debris after pruning'
        ],
        'biological_control': [
            'Neem oil or horticultural oil spray during early shoot growth',
            'Bio-fungicide sprays with Trichoderma viride'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Mancozeb 75% WP',
                'chemical_group': 'Dithiocarbamate',
                'purpose': 'Protective multi-site fungicide to prevent spore penetration.',
                'application_method': 'Foliar spray at 2.5 g per litre of water.',
                'timing': 'Apply at first sign of spots; repeat at 10-12 day intervals.',
                'precautions': 'Do not apply within 21 days of grape harvest.'
            },
            {
                'active_ingredient': 'Copper Oxychloride 50% WP',
                'chemical_group': 'Inorganic Copper',
                'purpose': 'Protective contact spray against fungal spores on foliage.',
                'application_method': 'Foliar spray at 3 g per litre of water.',
                'timing': 'Apply post-bloom and during monsoon wet periods.',
                'precautions': 'Avoid application during hot midday sun.'
            }
        ],
        'spray_schedule': [
            'Round 1: Mancozeb 75% WP @ 2.5 g/L upon observing early spots.',
            'Round 2 (12 days): Copper Oxychloride 50% WP @ 3 g/L.',
            'Post-harvest: Copper spray to protect foliage until natural leaf drop.'
        ],
        'resistance_management': [
            'Rotate dithiocarbamates with copper and strobilurin fungicides.'
        ],
        'prevention': [
            'Ensure trellis orientation allows maximum morning sun exposure.'
        ],
        'follow_up': [
            'Inspect lower canopy leaves every week during warm, humid weather.'
        ]
    },
    'haunglongbing citrus greening': {
        'disease_type': 'bacterial',
        'title': 'Citrus Greening (HLB)',
        'summary': 'Citrus greening (HLB) suspected. Inspect for psyllid vectors and contact local KVK / horticulture office.',
        'description': 'Huanglongbing (HLB), or Citrus Greening, is caused by Candidatus Liberibacter asiaticus, transmitted by the Asian citrus psyllid (Diaphorina citri). It causes asymmetrical yellow mottling of leaves and bitter, lopsided fruit.',
        'symptoms': [
            'Asymmetric yellow blotchy mottle across leaf veins (one side yellow, other green)',
            'Yellowing of veins followed by vein corking and thickening',
            'Small, lopsided, poorly colored fruit with bitter taste and dark aborted seeds'
        ],
        'immediate_actions': [
            'There is currently no chemical cure for infected citrus trees',
            'Uproot and burn confirmed infected trees to protect remaining orchard',
            'Control Asian citrus psyllid vector immediately across the entire grove'
        ],
        'cultural_control': [
            'Plant only certified disease-free saplings from accredited insect-proof nurseries',
            'Remove alternative rutaceous hosts like Murraya paniculata (orange jasmine) nearby',
            'Maintain optimum irrigation and soil nutrition to sustain unaffected trees'
        ],
        'biological_control': [
            'Release parasitic wasps (Tamarixia radiata) for biological psyllid management',
            'Neem oil or insecticidal soap sprays on new flush shoots to deter psyllid feeding'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Imidacloprid 17.8% SL',
                'chemical_group': 'Neonicotinoid',
                'purpose': 'Systemic insecticide to control Asian citrus psyllid vectors and halt disease transmission.',
                'application_method': 'Foliar spray @ 0.5 ml/L or soil drench around trunk root zone.',
                'timing': 'Apply during new leaf flush when psyllid activity is highest.',
                'precautions': 'Avoid application during citrus flowering to protect pollinators.'
            },
            {
                'active_ingredient': 'Thiamethoxam 25% WG',
                'chemical_group': 'Neonicotinoid',
                'purpose': 'Systemic control of sucking insect vectors on flush growth.',
                'application_method': 'Foliar spray at 0.3 g per litre of water.',
                'timing': 'Alternate with organophosphates on newly emerging shoot flushes.',
                'precautions': 'Follow strict pollinator safety measures.'
            }
        ],
        'spray_schedule': [
            'New flush onset: Imidacloprid 17.8% SL @ 0.5 ml/L for psyllid knockdown.',
            'Second flush (15-20 days): Alternate with Thiamethoxam 25% WG @ 0.3 g/L.',
            'Regular scouting for psyllid eggs and nymphs on tender shoot tips.'
        ],
        'resistance_management': [
            'Rotate insecticides between IRAC chemical classes to prevent psyllid resistance.'
        ],
        'prevention': [
            'Never graft or propagate budwood from unverified field sources.'
        ],
        'follow_up': [
            'Send leaf samples to an accredited plant pathology lab or KVK for PCR confirmation.'
        ]
    },
    'bacterial spot': {
        'disease_type': 'bacterial',
        'title': 'Bacterial Spot',
        'summary': 'Bacterial spot detected. Avoid overhead watering and working with wet foliage, and spray copper bactericide.',
        'description': 'Bacterial spot, caused by Xanthomonas species, creates small, water-soaked, dark brown-to-black angular spots on leaves, stems, and fruit. In wet weather, lesions coalesce, leading to severe leaf blight and fruit dropping.',
        'symptoms': [
            'Small (1-3 mm), water-soaked angular spots turning dark brown or black',
            'Lesions often surrounded by a light yellow ring or halo',
            'Scabby, raised pustules on fruits that reduce market value'
        ],
        'immediate_actions': [
            'Avoid overhead irrigation and splashing water onto foliage',
            'Do not prune, harvest, or walk through fields while foliage is wet',
            'Spray copper oxychloride with streptocycline to suppress bacterial spread'
        ],
        'cultural_control': [
            'Use certified pathogen-free seed or hot-water treated seed (50°C for 25 min)',
            'Rotate fields out of nightshade crops for at least 2 seasons',
            'Disinfect pruning tools with 70% alcohol or 10% bleach solution between rows'
        ],
        'biological_control': [
            'Bio-control using bacteriophages specific to Xanthomonas',
            'Bacillus subtilis (Serenade) foliar spray'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Copper Oxychloride 50% WP',
                'chemical_group': 'Inorganic Copper (FRAC M01)',
                'purpose': 'Broad-spectrum bactericide to reduce bacterial populations on leaf surface.',
                'application_method': 'Foliar spray at 3 g per litre of water.',
                'timing': 'Apply preventively or at first appearance of spots; repeat at 7-10 day intervals.',
                'precautions': 'Avoid spraying during extreme heat; observe 7-day pre-harvest interval.'
            },
            {
                'active_ingredient': 'Streptocycline (Streptomycin + Tetracycline)',
                'chemical_group': 'Antibacterial',
                'purpose': 'Antibiotic spray for severe bacterial leaf spot suppression (where permitted).',
                'application_method': 'Tank mix 1 g in 10 litres of water along with Copper Oxychloride.',
                'timing': 'Apply during early active infection stages in wet weather.',
                'precautions': 'Use strictly as per local government and pesticide regulations.'
            }
        ],
        'spray_schedule': [
            'Round 1: Copper Oxychloride 50% WP @ 3 g/L + Streptocycline @ 0.1 g/L.',
            'Round 2 (7-10 days): Copper Hydroxide @ 2 g/L.',
            'Repeat after heavy rain events if bacterial spots continue developing.'
        ],
        'resistance_management': [
            'Combine copper sprays with mancozeb to increase bactericidal activity and reduce copper-tolerant strains.'
        ],
        'prevention': [
            'Avoid working in wet fields.',
            'Install drip irrigation instead of overhead sprinklers.'
        ],
        'follow_up': [
            'Check new growth flushes weekly for grease-like water-soaked spots.'
        ]
    },
    'early blight': {
        'disease_type': 'fungal',
        'title': 'Early Blight',
        'summary': 'Early blight detected. Prune infected lower foliage, avoid leaf wetness, and spray protective fungicide.',
        'description': 'Early blight, caused by Alternaria solani, primarily attacks older foliage. It begins as small, brown-to-black spots on lower leaves that enlarge and develop characteristic concentric rings (target board pattern) surrounded by yellow chlorotic halos.',
        'symptoms': [
            'Concentric circular rings ("target-board" appearance) on older leaves',
            'Yellowing (chlorosis) around dark necrotic lesions',
            'Premature defoliation starting from the bottom of the plant upwards'
        ],
        'immediate_actions': [
            'Prune and safely destroy heavily infected lower leaves',
            'Avoid overhead sprinkler watering to keep leaves dry',
            'Apply a protective fungicide spray immediately if lesions are spreading'
        ],
        'cultural_control': [
            'Mulch soil around plants to prevent soil splash onto lower foliage',
            'Practice 2-3 year crop rotation away from solanaceous crops (tomato, potato, eggplant)',
            'Ensure adequate plant spacing for good airflow and canopy drying'
        ],
        'biological_control': [
            'Foliar spray of Trichoderma harzianum or Bacillus subtilis as a preventive bio-agent',
            'Neem oil spray (5 ml/L of water) with sticker during early growth'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Mancozeb 75% WP',
                'chemical_group': 'Dithiocarbamate (FRAC M03)',
                'purpose': 'Multi-site contact protective fungicide.',
                'application_method': 'Foliar spray at 2.5 g per litre of water covering both sides of leaves.',
                'timing': 'Apply at first sign of symptoms or during humid warm spells.',
                'precautions': 'Observe 7-10 day pre-harvest interval; wear gloves and mask.'
            },
            {
                'active_ingredient': 'Chlorothalonil 75% WP',
                'chemical_group': 'Chloronitrile (FRAC M05)',
                'purpose': 'Broad-spectrum contact fungicide to protect uninfected leaves.',
                'application_method': 'Foliar spray at 2 g per litre of water.',
                'timing': 'Repeat every 7-10 days during warm, humid conditions.',
                'precautions': 'Do not mix with surfactants or oil-based additives.'
            }
        ],
        'spray_schedule': [
            'Initial spray: Mancozeb 75% WP @ 2.5 g/L upon noticing early lesions.',
            'Second spray (7-10 days later): Alternate with Chlorothalonil 75% WP @ 2 g/L.',
            'Maintenance: Repeat at 10-14 day intervals if wet, warm weather continues.'
        ],
        'resistance_management': [
            'Alternate multi-site contact fungicides (Mancozeb, Chlorothalonil) with strobilurin or triazole fungicides.',
            'Do not use single-site systemic fungicides consecutively.'
        ],
        'prevention': [
            'Use certified disease-free seeds and certified transplants.',
            'Stake plants to keep foliage off the ground.',
            'Ensure balanced nitrogen fertilization (avoid excess vegetative growth).'
        ],
        'follow_up': [
            'Inspect lower canopy every 3-4 days after rainfall or high humidity.',
            'Monitor fruit calyx for dark sunken lesions.'
        ]
    },
    'late blight': {
        'disease_type': 'fungal',
        'title': 'Late Blight',
        'summary': 'Late blight detected. Highly destructive and fast-spreading in cool, wet weather. Immediate systemic spray required.',
        'description': 'Late blight, caused by the oomycete Phytophthora infestans, is a destructive disease that spreads rapidly in cool, wet weather. It causes large, water-soaked, dark green to brown lesions with white moldy fungal growth on leaf undersides.',
        'symptoms': [
            'Large irregular water-soaked spots that turn dark brown to purplish-black',
            'Delicate white cottony fungal growth on leaf undersides in humid mornings',
            'Rapid collapse and browning of leaves and stems (resembles frost damage)'
        ],
        'immediate_actions': [
            'Uproot and destroy severely infected plants immediately (do not compost)',
            'Stop all overhead irrigation immediately',
            'Apply curative/penetrant systemic fungicide without delay'
        ],
        'cultural_control': [
            'Destroy volunteer potato and tomato plants and cull piles',
            'Ensure wide row spacing for maximum sunlight and ventilation',
            'Plant resistant varieties when available'
        ],
        'biological_control': [
            'Bio-fungicides like Trichoderma viride applied to soil and foliage preventively',
            'Copper hydroxide formulations approved for organic farming'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Cymoxanil 8% + Mancozeb 64% WP',
                'chemical_group': 'Acetamide + Dithiocarbamate',
                'purpose': 'Curative and protective dual-action spray to arrest active mycelium.',
                'application_method': 'Foliar spray at 3 g per litre of water.',
                'timing': 'Apply immediately at first detection of late blight lesions.',
                'precautions': 'Do not exceed 3 applications per crop season.'
            },
            {
                'active_ingredient': 'Metalaxyl 8% + Mancozeb 64% WP',
                'chemical_group': 'Phenylamide + Dithiocarbamate',
                'purpose': 'Systemic translaminar protection for rapidly growing shoots.',
                'application_method': 'Foliar spray at 2.5 g per litre of water.',
                'timing': 'Apply during high-risk cool, foggy, or rainy weather.',
                'precautions': 'Rotate with non-phenylamide fungicides to prevent resistance.'
            }
        ],
        'spray_schedule': [
            'Day 1: Cymoxanil + Mancozeb @ 3 g/L immediately upon detection.',
            'Day 7: Metalaxyl + Mancozeb @ 2.5 g/L if wet/foggy conditions persist.',
            'Day 14: Mancozeb 75% WP @ 2.5 g/L as a protective barrier spray.'
        ],
        'resistance_management': [
            'Strictly limit phenylamides (metalaxyl) to maximum 2 sprays per season.',
            'Always use mixtures containing multi-site protectants like mancozeb.'
        ],
        'prevention': [
            'Avoid working in wet fields to prevent mechanically spreading zoospores.',
            'Monitor weather forecasts for periods with RH > 90% and temps 12-22°C.'
        ],
        'follow_up': [
            'Check adjacent rows and neighbouring fields daily.',
            'Inspect tubers/fruits for firm, dark brown dry rot.'
        ]
    },
    'leaf scorch': {
        'disease_type': 'fungal',
        'title': 'Leaf Scorch',
        'summary': 'Strawberry leaf scorch detected. Prune infected leaves, avoid overhead watering, and spray captan.',
        'description': 'Caused by Diplocarpon earlianum, strawberry leaf scorch produces numerous small, irregular dark purple spots that enlarge and cause leaves to appear burned or scorched.',
        'symptoms': [
            'Small, angular dark purple spots without white centers on upper leaf surface',
            'Spots coalesce causing the entire leaf blade to turn reddish-brown, dry, and curl',
            'Affected leaves look burned or scorched and drop prematurely'
        ],
        'immediate_actions': [
            'Remove and destroy heavily scorched leaves after harvest or during renovation',
            'Switch from overhead sprinkling to drip irrigation to keep crowns dry',
            'Apply protective fungicide during wet periods'
        ],
        'cultural_control': [
            'Maintain well-drained planting beds and avoid overcrowded runner plants',
            'Mow and renovate strawberry beds immediately after harvest',
            'Plant resistant strawberry cultivars'
        ],
        'biological_control': [
            'Trichoderma viride root and crown dips before transplanting',
            'Bacillus subtilis bio-fungicide foliar applications'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Captan 50% WP',
                'chemical_group': 'Phthalimide',
                'purpose': 'Multi-site contact fungicide protecting new leaves from fungal spores.',
                'application_method': 'Foliar spray at 2.5 g per litre of water.',
                'timing': 'Apply during spring emergence and post-harvest renovation before rains.',
                'precautions': 'Do not tank mix with oils.'
            },
            {
                'active_ingredient': 'Copper Hydroxide 77% WP',
                'chemical_group': 'Inorganic Copper',
                'purpose': 'Protective foliar shield against leaf spot and scorch pathogens.',
                'application_method': 'Foliar spray at 2 g per litre of water.',
                'timing': 'Apply during post-harvest bed renovation.',
                'precautions': 'Observe plant tolerance; avoid spraying during extreme temperatures.'
            }
        ],
        'spray_schedule': [
            'Spring growth: Captan 50% WP @ 2.5 g/L.',
            'Post-harvest: Copper Hydroxide @ 2 g/L following old foliage removal.'
        ],
        'resistance_management': [
            'Rely on multi-site protectants to prevent fungicide resistance.'
        ],
        'prevention': [
            'Ensure wide bed spacing and straw mulching to minimize splash.'
        ],
        'follow_up': [
            'Check newly emerged runner leaves every 7-10 days.'
        ]
    },
    'leaf mold': {
        'disease_type': 'fungal',
        'title': 'Leaf Mold',
        'summary': 'Leaf mold detected on tomato. Improve airflow, reduce humidity, and apply mancozeb or chlorothalonil.',
        'description': 'Caused by Passalora fulva (Cladosporium fulvum), leaf mold is common in greenhouses and high-humidity areas. It forms pale green-to-yellow spots on leaf upper surfaces with velvety olive-green fungal growth underneath.',
        'symptoms': [
            'Pale green or yellowish spots with diffuse margins on upper leaf surface',
            'Velvety olive-green to grayish-brown fungal sporulation on leaf undersides',
            'Leaves curl, wither, and drop prematurely from the bottom up'
        ],
        'immediate_actions': [
            'Increase greenhouse or polyhouse ventilation immediately',
            'Keep relative humidity strictly below 85%',
            'Prune lower leaves to allow air circulation through bottom of plants'
        ],
        'cultural_control': [
            'Use circulating fans and roof vents to keep leaves dry',
            'Water only at base in early morning using drip systems',
            'Plant resistant tomato hybrids with Cf resistance genes'
        ],
        'biological_control': [
            'Bio-fungicide spray containing Bacillus amyloliquefaciens',
            'Trichoderma harzianum foliar spray'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Mancozeb 75% WP',
                'chemical_group': 'Dithiocarbamate',
                'purpose': 'Protective barrier against leaf mold spore germination.',
                'application_method': 'Foliar spray at 2.5 g/L covering undersides of foliage thoroughly.',
                'timing': 'Apply at first detection of yellow upper-leaf spots.',
                'precautions': 'Ensure complete coverage on leaf undersides.'
            },
            {
                'active_ingredient': 'Chlorothalonil 75% WP',
                'chemical_group': 'Chloronitrile',
                'purpose': 'Broad-spectrum contact protective spray.',
                'application_method': 'Foliar spray at 2 g per litre of water.',
                'timing': 'Repeat every 7-10 days under humid conditions.',
                'precautions': 'Do not apply within 7 days of harvest.'
            }
        ],
        'spray_schedule': [
            'Initial: Mancozeb 75% WP @ 2.5 g/L focusing on leaf undersides.',
            'Follow-up (7-10 days): Alternate with Chlorothalonil 75% WP @ 2 g/L.'
        ],
        'resistance_management': [
            'Alternate between chemical groups and rely on ventilation for control.'
        ],
        'prevention': [
            'Maintain daytime and night-time humidity below 85% with fans.'
        ],
        'follow_up': [
            'Inspect lower leaf undersides every 3 days.'
        ]
    },
    'septoria leaf spot': {
        'disease_type': 'fungal',
        'title': 'Septoria Leaf Spot',
        'summary': 'Septoria leaf spot detected. Remove lower infected leaves, mulch soil, and apply protective fungicide.',
        'description': 'Caused by Septoria lycopersici, this disease produces numerous small, circular spots with dark brown margins and sunken grayish-white centers dotted with tiny black pycnidia.',
        'symptoms': [
            'Small (1.5-3 mm), circular spots with dark brown margins and light gray centers',
            'Tiny black specks (pycnidia fruiting bodies) clearly visible inside gray centers',
            'Severe lower leaf yellowing and defoliation progressing upward'
        ],
        'immediate_actions': [
            'Carefully prune and dispose of infected bottom leaves',
            'Apply mulch around tomato base to stop soil splash from spreading spores',
            'Avoid handling wet plants'
        ],
        'cultural_control': [
            'Stake or cage tomato plants to elevate canopy from moist soil',
            'Rotate out of solanaceous crops for 2-3 years',
            'Destroy crop residue at the end of every season'
        ],
        'biological_control': [
            'Copper-based fungicides approved for organic production',
            'Bacillus subtilis preventive foliar spray'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Mancozeb 75% WP',
                'chemical_group': 'Dithiocarbamate',
                'purpose': 'Multi-site contact protectant to arrest leaf infection.',
                'application_method': 'Foliar spray at 2.5 g per litre of water.',
                'timing': 'Apply at first sign of circular spots on bottom foliage.',
                'precautions': 'Wear protective gear; do not spray before rain.'
            },
            {
                'active_ingredient': 'Chlorothalonil 75% WP',
                'chemical_group': 'Chloronitrile',
                'purpose': 'Contact protective barrier on foliage.',
                'application_method': 'Foliar spray at 2 g per litre of water.',
                'timing': 'Every 7-10 days during rainy or humid spells.',
                'precautions': 'Follow label dosage and harvest intervals.'
            }
        ],
        'spray_schedule': [
            'Day 1: Mancozeb 75% WP @ 2.5 g/L.',
            'Day 8-10: Chlorothalonil @ 2 g/L if wet weather continues.'
        ],
        'resistance_management': [
            'Rotate contact protectants with systemic triazole fungicides if needed.'
        ],
        'prevention': [
            'Install plastic or straw mulch beneath all plants before rainy season.'
        ],
        'follow_up': [
            'Check lower leaves every 3-4 days for new spot emergence.'
        ]
    },
    'spider mites two-spotted spider mite': {
        'disease_type': 'pest',
        'title': 'Two-Spotted Spider Mite',
        'summary': 'Spider mite infestation detected. Wash leaf undersides, apply neem oil or targeted miticide.',
        'description': 'Two-spotted spider mites (Tetranychus urticae) are tiny arachnid pests that pierce plant cells on leaf undersides to feed on sap. They cause fine stippling, chlorosis, and delicate fine webbing on leaves.',
        'symptoms': [
            'Fine yellow, white, or bronze speckling (stippling) on upper leaf surface',
            'Fine silken webbing spun across leaf undersides and shoot tips',
            'Leaves turn yellow, dry out, become brittle, and drop prematurely'
        ],
        'immediate_actions': [
            'Spray strong stream of water on leaf undersides to knock down mite colonies',
            'Apply neem oil (5 ml/L) thoroughly covering leaf undersides',
            'Avoid broad-spectrum synthetic pyrethroid insecticides that kill natural mite predators'
        ],
        'cultural_control': [
            'Keep plants well-irrigated (drought-stressed plants are highly vulnerable)',
            'Maintain overhead humidity or misting in greenhouses to suppress mite reproduction',
            'Remove and destroy heavily webbed shoots'
        ],
        'biological_control': [
            'Release predatory mites (Phytoseiulus persimilis or Neoseiulus californicus)',
            'Apply neem oil or insecticidal potassium salts of fatty acids'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Spiromesifen 22.9% SC',
                'chemical_group': 'Tetronic acid (IRAC 23)',
                'purpose': 'Lipid biosynthesis inhibitor with ovicidal and nymphicidal activity against mites.',
                'application_method': 'Foliar spray at 0.8 ml per litre of water on both leaf surfaces.',
                'timing': 'Apply when mite populations first begin building up.',
                'precautions': 'Do not apply more than twice per season; observe 3-day PHI.'
            },
            {
                'active_ingredient': 'Propargite 57% EC',
                'chemical_group': 'Sulfite ester (IRAC 12C)',
                'purpose': 'Specific contact acaricide effective against all active motile stages of mites.',
                'application_method': 'Foliar spray at 2 ml per litre of water.',
                'timing': 'Apply as a knockdown spray if mite numbers are high.',
                'precautions': 'Do not spray during high temperatures (>30°C) to avoid phytotoxicity.'
            }
        ],
        'spray_schedule': [
            'Day 1: Water wash + Neem oil @ 5 ml/L or Spiromesifen @ 0.8 ml/L.',
            'Day 5-7: Inspect leaf undersides; repeat miticide if eggs have hatched.'
        ],
        'resistance_management': [
            'Never apply the same miticide class consecutively. Always rotate IRAC groups.'
        ],
        'prevention': [
            'Control broadleaf weeds around borders which serve as overwintering mite reservoirs.'
        ],
        'follow_up': [
            'Use a 10x hand lens to check leaf undersides twice weekly.'
        ]
    },
    'target spot': {
        'disease_type': 'fungal',
        'title': 'Target Spot',
        'summary': 'Target spot detected on tomato. Remove lower diseased leaves, enhance airflow, and spray fungicide.',
        'description': 'Caused by Corynespora cassiicola, target spot produces brown circular lesions with concentric rings and chlorotic halos that resemble early blight, causing extensive defoliation.',
        'symptoms': [
            'Circular brown lesions with discrete concentric target-like rings',
            'Light brown centers that often crack or fall out leaving a shot-hole appearance',
            'Leaf yellowing, curling, and rapid drop in warm, humid weather'
        ],
        'immediate_actions': [
            'Prune off heavily infected lower foliage to reduce inoculum',
            'Increase plant spacing and trellising for rapid canopy drying',
            'Apply protective contact fungicide'
        ],
        'cultural_control': [
            'Rotate fields with non-host crops like corn or grasses for 2 seasons',
            'Use drip irrigation and avoid overhead wetting of foliage',
            'Stake plants and maintain adequate air circulation'
        ],
        'biological_control': [
            'Bio-agent foliar application with Trichoderma harzianum or Bacillus subtilis'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Chlorothalonil 75% WP',
                'chemical_group': 'Chloronitrile',
                'purpose': 'Multi-site contact protectant against conidia germination.',
                'application_method': 'Foliar spray at 2 g per litre of water.',
                'timing': 'Apply at first sign of target lesions on foliage.',
                'precautions': 'Observe 7-day pre-harvest interval.'
            },
            {
                'active_ingredient': 'Mancozeb 75% WP',
                'chemical_group': 'Dithiocarbamate',
                'purpose': 'Protective multi-site barrier against fungal leaf spot pathogens.',
                'application_method': 'Foliar spray at 2.5 g per litre of water.',
                'timing': 'Every 10-14 days during wet, humid weather.',
                'precautions': 'Wear protective gear during handling.'
            }
        ],
        'spray_schedule': [
            'Initial: Chlorothalonil 75% WP @ 2 g/L.',
            'Follow-up (10-12 days): Mancozeb 75% WP @ 2.5 g/L.'
        ],
        'resistance_management': [
            'Avoid repeated use of single-site fungicides.'
        ],
        'prevention': [
            'Stake tomato vines and mulch soil.'
        ],
        'follow_up': [
            'Check mid-canopy leaves weekly.'
        ]
    },
    'tomato yellow leaf curl virus': {
        'disease_type': 'viral',
        'title': 'Tomato Yellow Leaf Curl Virus',
        'summary': 'Tomato Yellow Leaf Curl Virus (TYLCV) detected. Uproot infected plants and manage whitefly vector.',
        'description': 'Tomato Yellow Leaf Curl Virus (TYLCV) is a devastating begomovirus transmitted by the sweetpotato whitefly (Bemisia tabaci). It causes severe stunting, erect bunchy growth, and yellow curled leaves.',
        'symptoms': [
            'Upward curling, cupping, and twisting of leaf margins',
            'Pronounced interveinal yellowing (chlorosis) on new leaves',
            'Severe stunting and bushy growth; flowers drop before setting fruit'
        ],
        'immediate_actions': [
            'Uproot and destroy infected plants immediately in closed plastic bags (no cure)',
            'Install yellow sticky traps (15-20 per acre) to trap whitefly vectors',
            'Spray targeted systemic insecticide to suppress whitefly vector populations'
        ],
        'cultural_control': [
            'Grow seedlings inside 40-50 mesh insect-proof net nurseries',
            'Plant TYLCV-resistant or tolerant tomato hybrids (e.g. varieties with Ty genes)',
            'Maintain a 2-month host-free period between tomato crops'
        ],
        'biological_control': [
            'Neem oil (5 ml/L) or neem seed kernel extract (NSKE 5%) against whitefly nymphs',
            'Release parasitoids like Encarsia formosa in greenhouses'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Diafenthiuron 50% WP',
                'chemical_group': 'Thiourea (IRAC 12A)',
                'purpose': 'Controls adult and nymphal whitefly vectors transmitting the virus.',
                'application_method': 'Foliar spray at 1 g/L with thorough coverage on leaf undersides.',
                'timing': 'Apply when whitefly counts exceed 2-3 adults per leaf.',
                'precautions': 'Do not apply during peak pollinator foraging hours.'
            },
            {
                'active_ingredient': 'Pyriproxyfen 10% EC',
                'chemical_group': 'Insect Growth Regulator (IRAC 7C)',
                'purpose': 'Sterilizes adult female whiteflies and prevents nymphal development.',
                'application_method': 'Foliar spray at 1 ml per litre of water.',
                'timing': 'Apply in rotation with systemic insecticides to break whitefly lifecycle.',
                'precautions': 'Follow label safety instructions.'
            }
        ],
        'spray_schedule': [
            'Vector control round 1: Diafenthiuron 50% WP @ 1 g/L on leaf undersides.',
            'Vector control round 2 (8-10 days): Pyriproxyfen 10% EC @ 1 ml/L.'
        ],
        'resistance_management': [
            'Strictly alternate insecticide chemical classes to prevent whitefly resistance.'
        ],
        'prevention': [
            'Never plant tomato fields near old, unmanaged solanaceous or cucurbit fields.'
        ],
        'follow_up': [
            'Monitor yellow sticky traps daily for whitefly count spikes.'
        ]
    },
    'tomato mosaic virus': {
        'disease_type': 'viral',
        'title': 'Tomato Mosaic Virus',
        'summary': 'Tomato Mosaic Virus (ToMV) detected. Disinfect hands and tools, remove infected plants; no chemical cure exists.',
        'description': 'Tomato Mosaic Virus (ToMV) is an extremely stable and infectious tobamovirus. It spreads mechanically via hands, pruning shears, stakes, and infected seed, causing mottled light and dark green patterns on leaves.',
        'symptoms': [
            'Mottled light and dark green mosaic patterns on leaves',
            'Distorted, crinkled, or shoe-string-like narrow leaf blades',
            'Internal brown necrosis in fruit and overall plant stunting'
        ],
        'immediate_actions': [
            'Immediately rogue out and safely burn or bury infected plants',
            'Disinfect hands and all tools in 20% skimmed milk solution or 10% trisodium phosphate',
            'Do not smoke, chew tobacco, or touch healthy plants after touching infected ones'
        ],
        'cultural_control': [
            'Purchase certified virus-free seed treated with dry heat or trisodium phosphate',
            'Grow tomato varieties with Tm-2 or Tm-2^2 resistance genes',
            'Thoroughly sterilize plant stakes and trellising wires between seasons'
        ],
        'biological_control': [
            'Milk spray (10-20% non-fat dry milk) during transplant handling to reduce mechanical transmission'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Sanitation (No Chemical Cure)',
                'chemical_group': 'Sanitation & Disinfection',
                'purpose': 'Viruses have no curative chemical spray; management relies strictly on sanitation.',
                'application_method': 'Disinfect pruning tools and wash hands frequently.',
                'timing': 'Throughout entire crop production cycle.',
                'precautions': 'Do not waste fungicides or insecticides trying to cure viral infections.'
            }
        ],
        'spray_schedule': [
            'No pesticide spray is effective against viruses.',
            'Focus exclusively on sanitation, seed treatment, and rogueing.'
        ],
        'resistance_management': [
            'Select genetically resistant tomato hybrids.'
        ],
        'prevention': [
            'Enforce strict hand washing protocols before handling seedlings.'
        ],
        'follow_up': [
            'Scout field twice a week to remove any newly symptomatic plants.'
        ]
    },
    'healthy': {
        'disease_type': 'healthy',
        'title': 'Healthy Leaf',
        'summary': 'The leaf appears healthy with normal chlorophyll pigmentation and no visible pathogen damage.',
        'description': 'The leaf exhibits strong vigor, uniform pigmentation, and no visible necrotic lesions, fungal sporulation, bacterial spots, or pest feeding injury.',
        'symptoms': [
            'Clean, vibrant leaf surface with uniform green coloration',
            'No visible chlorosis, necrotic spotting, or wilting',
            'Intact leaf margins and healthy vein structure'
        ],
        'immediate_actions': [
            'Continue routine field monitoring and balanced crop nutrition',
            'Keep drip irrigation scheduling optimized to prevent moisture stress',
            'Maintain field sanitation and remove fallen weed debris'
        ],
        'cultural_control': [
            'Maintain recommended planting spacing for adequate aeration',
            'Apply balanced NPK fertilizer based on soil testing (avoid excess nitrogen)',
            'Inspect plants weekly for early detection of any emerging pest or disease pressure'
        ],
        'biological_control': [
            'Neem seed kernel extract (NSKE 5%) or neem oil spray (3 ml/L) as a general preventive repellent',
            'Encourage beneficial predatory insects like ladybird beetles and lacewings'
        ],
        'chemical_options': [],
        'spray_schedule': [
            'No pesticide spray is required for healthy leaves.',
            'Continue standard preventive foliar micronutrient or bio-stimulant regimen as scheduled.'
        ],
        'resistance_management': [
            'No chemical application needed.'
        ],
        'prevention': [
            'Maintain consistent field sanitation and weed management.',
            'Scout crops early in the morning twice weekly.'
        ],
        'follow_up': [
            'Re-check field in 7-10 days or after significant rainfall events.'
        ]
    }
}


def get_disease_metadata(normalized_disease):
    if normalized_disease == 'healthy':
        return DISEASE_METADATA['healthy']
    for key, data in DISEASE_METADATA.items():
        if key in normalized_disease or normalized_disease in key:
            return data
    # Fallback default metadata
    return {
        'disease_type': 'fungal',
        'title': normalized_disease.title(),
        'summary': f'{normalized_disease.title()} symptoms detected. Consult local agricultural experts for a targeted spray plan.',
        'description': f'Leaf symptoms are consistent with {normalized_disease}. Early intervention helps protect yield and limit field spread.',
        'symptoms': [
            f'Lesions and discoloration characteristic of {normalized_disease}',
            'Affected leaf tissue showing reduced photosynthetic capacity'
        ],
        'immediate_actions': [
            'Isolate and inspect neighboring plants to verify spread',
            'Avoid overhead watering and prune heavily affected lower leaves',
            'Consult your local Krishi Vigyan Kendra (KVK) for confirmation'
        ],
        'cultural_control': [
            'Maintain optimal plant spacing for ventilation',
            'Practice multi-year crop rotation'
        ],
        'biological_control': [
            'Neem-based preventive spray (5 ml/L of water)'
        ],
        'chemical_options': [
            {
                'active_ingredient': 'Mancozeb 75% WP',
                'chemical_group': 'Dithiocarbamate',
                'purpose': 'Broad-spectrum protective contact fungicide.',
                'application_method': 'Foliar spray at 2.5 g per litre of water.',
                'timing': 'Apply at first sign of symptoms in humid weather.',
                'precautions': 'Follow manufacturer safety instructions and harvest intervals.'
            }
        ],
        'spray_schedule': [
            'Day 1: Protective fungicide spray upon confirmation.',
            'Day 10: Assess leaf response and re-apply if necessary.'
        ],
        'resistance_management': [
            'Rotate fungicide classes with different FRAC codes.'
        ],
        'prevention': [
            'Use certified disease-free planting material.'
        ],
        'follow_up': [
            'Re-examine foliage every 5 days.'
        ]
    }


def get_diagnosis_details(class_name, confidence=1.0, crop_context='', location='', notes='', alternatives=None):
    """Enrich a prediction class with complete agronomic metadata matching UI expectations."""
    base_advice = advice_for(class_name)
    plant = base_advice['plant']
    disease_str = base_advice['disease']
    is_healthy = base_advice['is_healthy']
    norm_disease = parse_class(class_name)[1]
    meta = get_disease_metadata(norm_disease)

    # Determine status and certainty
    if is_healthy:
        status = 'healthy'
        certainty = 'high' if confidence >= 0.70 else 'medium'
    elif confidence >= 0.35:
        status = 'likely_disease'
        certainty = 'high' if confidence >= 0.75 else ('medium' if confidence >= 0.50 else 'low')
    else:
        status = 'needs_confirmation'
        certainty = 'low'

    # Observations tailored to the model prediction
    observations = [
        f"Deep learning model detected {meta['title']} visual patterns with {round(confidence * 100, 1)}% confidence.",
        f"Primary leaf tissue features correspond to {plant} foliage.",
    ]
    if crop_context and crop_context.lower() in plant.lower():
        observations.append(f"Specified crop ({crop_context}) matches model classification ({plant}).")
    elif crop_context:
        observations.append(f"Image analyzed with context for {crop_context}.")

    if notes:
        observations.append(f"Field notes considered: {notes}")

    # Possible causes
    possible_causes = []
    if alternatives:
        for alt in alternatives[:3]:
            possible_causes.append(
                f"{alt.get('plant')} — {alt.get('disease')} (model confidence: {round(alt.get('confidence', 0) * 100, 1)}%)"
            )
    if not possible_causes:
        possible_causes = [
            'High relative humidity and extended leaf wetness duration.',
            'Soil splash or physical handling in wet field conditions.'
        ]

    disease_name = meta['title'] if not is_healthy else 'Healthy'

    return {
        'status': status,
        'plant': plant,
        'disease': disease_name,
        'disease_type': meta.get('disease_type', 'unknown'),
        'certainty': certainty,
        'confidence': round(float(confidence), 4),
        'summary': meta.get('summary', base_advice['treatment']),
        'disease_description': meta.get('description', ''),
        'symptoms': meta.get('symptoms', []),
        'observations': observations,
        'possible_causes': possible_causes,
        'immediate_actions': meta.get('immediate_actions', []),
        'cultural_control': meta.get('cultural_control', []),
        'biological_control': meta.get('biological_control', []),
        'chemical_options': meta.get('chemical_options', []),
        'spray_schedule': meta.get('spray_schedule', []),
        'resistance_management': meta.get('resistance_management', []),
        'prevention': meta.get('prevention', []),
        'follow_up': meta.get('follow_up', []),
        'treatment': base_advice['treatment'],
        'label': class_name,
        'provider': 'ml',
        'model': 'disease_cnn.keras',
        'source': 'Trained Deep Learning CNN Model (PlantVillage / ICAR Guidelines)',
        'alternatives': alternatives or [],
        'is_healthy': is_healthy,
    }
