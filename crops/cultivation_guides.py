"""Crop cultivation lifecycle engine: Sowing to Mandi Selling.
Tailored agronomic timelines for Indian farmers with step-by-step practical advice,
actionable metrics, verified photography, and APMC commercial guidance.
"""
from django.utils.text import slugify


def _get_image(crop_slug, stage_key, fallback_key):
    """Resolve stage photo path with crop-specific and universal fallbacks."""
    import os
    from django.conf import settings
    
    specific = f"images/cultivation/{crop_slug}-{stage_key}.jpg"
    specific_path = os.path.join(settings.BASE_DIR, 'static', specific)
    if os.path.exists(specific_path):
        return specific

    universal = f"images/cultivation/{fallback_key}.jpg"
    universal_path = os.path.join(settings.BASE_DIR, 'static', universal)
    if os.path.exists(universal_path):
        return universal

    # Fallback to general crop photo if available
    crop_photo = f"images/crops/{crop_slug}.webp"
    return crop_photo


def get_cultivation_guide(crop_name, crop_data=None):
    """Return comprehensive step-by-step cultivation guide from sowing to selling."""
    crop_name = crop_name.strip() if crop_name else "Tomato"
    c_lower = crop_name.lower()
    crop_slug = slugify(crop_name)

    if any(p in c_lower for p in ['gram', 'mung', 'urad', 'pulse', 'pigeon', 'chickpea']):
        guide = _gram_guide(crop_data)
    elif 'tomato' in c_lower:
        guide = _tomato_guide(crop_data)
    elif 'wheat' in c_lower:
        guide = _wheat_guide(crop_data)
    elif 'rice' in c_lower or 'paddy' in c_lower:
        guide = _rice_guide(crop_data)
    elif 'cotton' in c_lower:
        guide = _cotton_guide(crop_data)
    elif 'potato' in c_lower:
        guide = _potato_guide(crop_data)
    elif 'onion' in c_lower:
        guide = _onion_guide(crop_data)
    elif 'maize' in c_lower:
        guide = _maize_guide(crop_data)
    elif 'chilli' in c_lower or 'pepper' in c_lower:
        guide = _chilli_guide(crop_data)
    elif 'soybean' in c_lower:
        guide = _soybean_guide(crop_data)
    elif 'mustard' in c_lower or 'rapeseed' in c_lower:
        guide = _mustard_guide(crop_data)
    elif 'banana' in c_lower:
        guide = _banana_guide(crop_data)
    elif 'mango' in c_lower:
        guide = _mango_guide(crop_data)
    else:
        guide = _generic_crop_guide(crop_name, crop_data)

    return _attach_plantix_data(guide, crop_name, crop_data)



# ─────────────────────────────────────────────────────────────────────────────
# 0. PLANTIX VISUAL TIMELINE BUILDER & GRAM GUIDE (Matching Plantix UI)
# ─────────────────────────────────────────────────────────────────────────────
def _gram_guide(crop_data):
    return {
        'crop_name': 'Black & Green Gram',
        'hindi_name': 'उड़द एवं मूंग दाल की वैज्ञानिक खेती',
        'botanical_name': 'Vigna mungo / Vigna radiata',
        'total_duration': '65 – 75 Days',
        'ideal_season': 'Kharif (Jun–Jul), Rabi (Oct–Nov), Zaid (Mar–Apr)',
        'expected_yield': '6 – 9 Quintals / Acre',
        'market_channel': 'APMC Dal Mandi, NAFED MSP Procurement, e-NAM',
        'stages': [
            {
                'step_number': 1,
                'title': 'Seed Selection & Rhizobium Bio-Inoculation',
                'hindi_title': 'बीज चयन एवं राइजोबियम बीजोपचार',
                'timeline': '2 weeks before seedling',
                'phase': 'Planting',
                'image': 'images/cultivation/plantix/farmer-field-planting.jpg',
                'image_caption': 'Healthy seed selection and Rhizobium inoculation for black and green gram',
                'metrics': [
                    {'label': 'Seed Rate', 'value': '8 – 10 kg / Acre', 'icon': 'bi-box-seam'},
                    {'label': 'Top Varieties', 'value': 'PU-31, Shekhar-2, IPM-02-3', 'icon': 'bi-stars'},
                    {'label': 'Rhizobium Dose', 'value': '200 g / 10 kg Seed', 'icon': 'bi-capsule'},
                    {'label': 'Spacing', 'value': '30 cm × 10 cm', 'icon': 'bi-rulers'},
                ],
                'actions': [
                    'Select certified, high-germination seed (>85%) of recommended varieties (PU-31, Pant U-30 for black gram; Samrat, Meha for green gram).',
                    'Treat seeds with Carbendazim + Mancozeb (2 g/kg) 24 hours prior to biological inoculation.',
                    'Prepare jaggery slurry and inoculate seeds with crop-specific Rhizobium leguminosarum @ 200 g/10 kg seeds.',
                    'Add Trichoderma viride @ 4 g/kg to protect against collar rot and Macrophomina root rot.',
                    'Dry treated seeds under shade for 30 minutes before sowing in moist field furrows.'
                ],
                'pro_tip': 'Never expose Rhizobium-inoculated seeds to direct hot sun; ultraviolet rays destroy live bacterial inoculants within 15 minutes.',
                'tool_shortcut': {'name': 'Calculate Seed Rate & Spacing', 'url': '/crops/spacing/'},
            },
            {
                'step_number': 2,
                'title': 'Field Preparation & Fine Seedbed Tilth',
                'hindi_title': 'खेत की जुताई व समतलीकरण',
                'timeline': '1 week before seedling',
                'phase': 'Field Preparation',
                'image': 'images/cultivation/plantix/weeding-hoe-field.jpg',
                'image_caption': 'Fine pulverized seedbed tilth for rapid pulse seedling emergence',
                'metrics': [
                    {'label': 'Ploughing', 'value': '1 Deep + 2 Harrowings', 'icon': 'bi-gear-wide-connected'},
                    {'label': 'FYM Manure', 'value': '4 – 5 Tonnes / Acre', 'icon': 'bi-flower1'},
                    {'label': 'Starter DAP', 'value': '40 – 50 kg / Acre', 'icon': 'bi-bag'},
                    {'label': 'Soil pH', 'value': '6.5 – 7.5 (Well-drained)', 'icon': 'bi-droplet-half'},
                ],
                'actions': [
                    'Plough the land 15–20 cm deep, followed by 2 cross-harrowings to create a pulverized, clod-free seedbed.',
                    'Incorporate 4–5 tonnes of well-decomposed FYM during last ploughing to enhance soil water retention.',
                    'Apply starter basal fertilizer: 8 kg Nitrogen, 16 kg Phosphorus (P2O5), and 8 kg Potash (K2O) per acre.',
                    'Level the field evenly using a wooden plank to avoid water accumulation during monsoon rains.'
                ],
                'pro_tip': 'Pulses cannot tolerate standing water; ensure drainage slope to eliminate water stagnation during sudden heavy showers.',
                'tool_shortcut': {'name': 'Check Soil Health Parameters', 'url': '/crops/'},
            },
            {
                'step_number': 3,
                'title': 'Furrow Sowing & Depth Control',
                'hindi_title': 'कतारों में बुवाई व गहराई नियंत्रण',
                'timeline': 'At Sowing & Emergence',
                'phase': 'Planting',
                'image': 'images/cultivation/plantix/furrow-seed-sowing.jpg',
                'image_caption': 'Precision furrow sowing at 3-4 cm depth with 30 cm row spacing',
                'metrics': [
                    {'label': 'Row Spacing', 'value': '30 cm', 'icon': 'bi-rulers'},
                    {'label': 'Plant Spacing', 'value': '10 cm', 'icon': 'bi-arrows-expand'},
                    {'label': 'Sowing Depth', 'value': '3 – 4 cm', 'icon': 'bi-arrow-down-short'},
                    {'label': 'Emergence Time', 'value': '4 – 6 Days', 'icon': 'bi-clock'},
                ],
                'actions': [
                    'Ensure optimal soil moisture (paleva) before opening furrows.',
                    'Sow seeds at 3–4 cm depth using seed drill or country plough with pora attachment.',
                    'Maintain 30 cm row-to-row spacing and 10 cm plant spacing for optimal canopy aeration.',
                    'Cover furrows lightly with friable soil and press gently for good seed-soil contact.'
                ],
                'pro_tip': 'Sowing deeper than 5 cm causes delayed emergence, weak coleoptiles, and seedling mortality.',
                'tool_shortcut': {'name': 'Seed & Spacing Calculator', 'url': '/crops/spacing/'},
            },
            {
                'step_number': 4,
                'title': 'Weed Management & Intercultural Hoeing',
                'hindi_title': 'खरपतवार नियंत्रण व निराई-गुड़ाई',
                'timeline': 'Day 15 – Day 35',
                'phase': 'Weeding',
                'image': 'images/cultivation/plantix/weeding-hoe-field.jpg',
                'image_caption': 'First weeding hoe operation at 20 days after emergence',
                'metrics': [
                    {'label': 'Critical Window', 'value': 'First 30 Days', 'icon': 'bi-calendar-check'},
                    {'label': 'Hand Weeding', 'value': '2 Rounds (Day 20 & 35)', 'icon': 'bi-scissors'},
                    {'label': 'Herbicide (Opt)', 'value': 'Quizalofop-ethyl 5% EC', 'icon': 'bi-droplet'},
                    {'label': 'Yield Saved', 'value': '+30% to +40%', 'icon': 'bi-graph-up-arrow'},
                ],
                'actions': [
                    'Perform first hand weeding or hoeing at 20 days after sowing to destroy early weed flushes.',
                    'Perform second light weeding at 35 days before canopy closure.',
                    'If grassy weeds dominate, spray Quizalofop-ethyl @ 400 ml/acre at 20 days with flat-fan nozzle.',
                    'Keep inter-row soil loose and aerated to facilitate oxygen diffusion to Rhizobium nodules.'
                ],
                'pro_tip': 'Keep pulse fields completely weed-free during the first 30 days; once plants branch, the canopy naturally suppresses new weeds.',
                'tool_shortcut': {'name': 'Weed Decision Support', 'url': '/crops/weeding/'},
            },
            {
                'step_number': 5,
                'title': 'Critical Irrigation & Foliar Nutrition',
                'hindi_title': 'क्रांतिक अवस्था में सिंचाई व पोषक तत्व छिड़काव',
                'timeline': 'Day 35 – Day 55',
                'phase': 'Irrigation',
                'image': 'images/cultivation/plantix/irrigation-drip-sprinkler.jpg',
                'image_caption': 'Light sprinkler/furrow irrigation at critical flowering stage',
                'metrics': [
                    {'label': 'Critical Stages', 'value': 'Flowering & Pod Filling', 'icon': 'bi-flower1'},
                    {'label': 'Foliar Spray', 'value': 'DAP 2% or 13:0:45 @ 1%', 'icon': 'bi-capsule'},
                    {'label': 'Water Mode', 'value': 'Furrow / Sprinkler', 'icon': 'bi-droplet-half'},
                    {'label': 'Avoid', 'value': 'Waterlogging > 24 hrs', 'icon': 'bi-exclamation-triangle'},
                ],
                'actions': [
                    'Irrigate at branching stage (25 days) and pod initiation stage (45–50 days).',
                    'Spray 2% DAP solution (4 kg DAP soaked overnight in 200 L water) at early flowering.',
                    'Add 1% Potassium Nitrate (13:0:45) at pod filling stage to maximize seed boldness.',
                    'Never flood fields during peak noon heat or allow water to stagnate around stems.'
                ],
                'pro_tip': 'A single 2% DAP foliar spray at flowering increases pod retention by 25% and seed test weight by 12%.',
                'tool_shortcut': {'name': 'Fertigation Dose Calculator', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 6,
                'title': 'Pod Borer & Whitefly IPM Defense',
                'hindi_title': 'फली छेदक व सफेद मक्खी कीट नियंत्रण',
                'timeline': 'Day 40 – Day 60',
                'phase': 'Crop Protection',
                'image': 'images/cultivation/plantix/knapsack-crop-protection.jpg',
                'image_caption': 'Knapsack spraying with hollow cone nozzle for pod borer defense',
                'metrics': [
                    {'label': 'Key Pests', 'value': 'Spotted Pod Borer, Whitefly', 'icon': 'bi-bug'},
                    {'label': 'Key Disease', 'value': 'Yellow Mosaic Virus (YMV)', 'icon': 'bi-virus'},
                    {'label': 'Bio-Spray', 'value': 'Neem Oil 10,000 ppm (3 ml/L)', 'icon': 'bi-shield-check'},
                    {'label': 'Target Chemistry', 'value': 'Emamectin Benzoate 5% SG', 'icon': 'bi-radioactive'},
                ],
                'actions': [
                    'Monitor for whitefly vectors of Yellow Mosaic Virus; install yellow sticky traps (10/acre).',
                    'At flower initiation, spray Neem oil 10,000 ppm @ 3 ml/L as repellent against borers.',
                    'If pod borer larvae exceed ETL (1 larva/meter row), spray Emamectin Benzoate 5% SG @ 80 g/acre.',
                    'Spray during late afternoon using hollow-cone nozzle knapsack sprayer covering all pods.'
                ],
                'pro_tip': 'Controlling whiteflies in the first 25 days is the only effective prevention against incurable Yellow Mosaic Virus.',
                'tool_shortcut': {'name': 'Check Leaf Disease Symptoms', 'url': '/disease/'},
            },
            {
                'step_number': 7,
                'title': 'Harvesting, Threshing & APMC Mandi Sale',
                'hindi_title': 'फसल कटाई, गहाई एवं मंडी विपणन',
                'timeline': 'Day 65 – Day 75',
                'phase': 'Harvesting & Market',
                'image': 'images/cultivation/plantix/crop-harvest-sickle.jpg',
                'image_caption': 'Harvesting mature black gram pods when 80% turn blackish-brown',
                'metrics': [
                    {'label': 'Maturity Sign', 'value': '80% Pods Black/Brown', 'icon': 'bi-check2-circle'},
                    {'label': 'Safe Moisture', 'value': '8 – 9% Moisture', 'icon': 'bi-moisture'},
                    {'label': 'Storage Pack', 'value': '50 kg Gunny Bags', 'icon': 'bi-box-seam'},
                    {'label': 'MSP Support', 'value': 'Govt. NAFED Procurement', 'icon': 'bi-shop'},
                ],
                'actions': [
                    'Harvest when 80–85% of pods turn dark brown or black. Cut plants close to the ground.',
                    'Dry harvested bundles on clean tarpaulin for 2–3 days in the sun.',
                    'Thresh by beating with sticks or through a multi-crop pulse thresher at low RPM.',
                    'Winnow and clean grain; dry to 8–9% moisture before bagging in clean HDPE or jute sacks.',
                    'Check live APMC mandi modal rates on KrishiMitra and sell at peak wholesale prices or NAFED centers.'
                ],
                'pro_tip': 'Moisture above 10% in stored pulse grains attracts pulse beetle (bruchid) infestations; store only bone-dry grain with dry neem leaves.',
                'tool_shortcut': {'name': 'Check Live Mandi Prices', 'url': '/market/prices/'},
            }
        ]
    }


def _attach_plantix_data(guide, crop_name, crop_data=None):
    """Enrich guide with 12 Plantix tasks, 6 stages, and grouped timeline cards with custom illustrations."""
    c_lower = crop_name.lower()
    is_pulse = any(p in c_lower for p in ['gram', 'mung', 'urad', 'pulse', 'soybean', 'pigeon', 'bean', 'chickpea'])
    is_cereal = any(p in c_lower for p in ['wheat', 'rice', 'paddy', 'maize', 'corn', 'barley', 'millet', 'sorghum', 'bajra', 'jowar'])

    # Timeline Group 1: 2 weeks before seedling
    if is_pulse:
        c1_title = f"Use the right Rhizobium for your {crop_name.lower()} crop"
        c1_sum = f"Inoculate seeds with specific Rhizobium strain (200 g / 10 kg seeds) to fix up to 45 kg of atmospheric nitrogen per hectare."
        c1_why = "Rhizobium root nodules synthesize bio-nitrogen, boosting vegetative vigor while cutting chemical urea costs by 25%."
        c1_mat = ["Certified Rhizobium culture (200 g/10 kg seed)", "Jaggery (50 g)", "Clean lukewarm water (250 ml)"]
    elif is_cereal:
        c1_title = f"Certified seed grading & variety selection for {crop_name}"
        c1_sum = f"Select certified high-germination seed (>85%) graded for uniform size and test weight."
        c1_why = "Uniform seed caliber guarantees synchronized emergence and resilient root anchoring."
        c1_mat = ["Certified seed lot", "Seed grading sieve", "Clean tarpaulin"]
    else:
        c1_title = f"Seed & variety selection for {crop_name}"
        c1_sum = f"Choose high-yielding disease-tolerant certified varieties suited for your agro-climatic zone."
        c1_why = "Certified seeds provide 15–20% higher yield potential and resistance to soil-borne damping-off."
        c1_mat = ["Certified hybrid/open-pollinated seed", "Sterilized nursery substrate or seedbed", "Clean containers"]

    card1 = {
        'id': 'tip-variety-selection',
        'task_id': 'planting',
        'task_name': 'Planting',
        'stage_id': 'sowing_nursery',
        'tag': 'Planting',
        'title': c1_title,
        'image': 'images/cultivation/plantix/farmer-field-planting.jpg',
        'summary': c1_sum,
        'why': c1_why,
        'materials': c1_mat,
        'steps': [
            'Inspect seeds for purity, removing broken, discolored, or insect-damaged grains.',
            'Conduct a quick germination float test in clean water to discard hollow seeds.',
            'Store seeds in dry, cool conditions away from direct sunlight until treatment day.',
            'Prepare required bio-inoculants and fungicides as per recommended regional package of practices.',
            'Confirm planting calendar with local monsoon or irrigation water release schedule.'
        ],
        'pro_tip': 'Always check seed germination percentage before sowing; if below 80%, increase seed rate by 15%.',
        'tool_url': '/crops/spacing/',
        'tool_name': 'Seed Rate & Spacing Calculator'
    }

    card2 = {
        'id': 'tip-chemical-seed-treatment',
        'task_id': 'planting',
        'task_name': 'Planting',
        'stage_id': 'sowing_nursery',
        'tag': 'Planting',
        'title': 'Seed chemical treatments',
        'image': 'images/cultivation/plantix/hands-holding-sapling.jpg',
        'summary': 'Proactive chemical seed dressing with systemic fungicides to stop damping-off, collar rot, and root rots.',
        'why': 'Protects young germinating seedlings during their most vulnerable 14-day emergence window.',
        'materials': ['Carbendazim 12% + Mancozeb 63% WP (Saaf) @ 2 g/kg seed OR Thiram 75% WP @ 3 g/kg', 'Seed dressing drum or plastic bucket', 'Protective gloves and dust mask'],
        'steps': [
            'Wear rubber gloves and dust mask before handling chemical fungicides.',
            'Place measured seed lot into a seed-treating drum or durable plastic container.',
            'Add 2 g Carbendazim + Mancozeb per 1 kg of seed.',
            'Rotate the drum gently for 5 minutes until powder forms an even, smooth coating over each seed.',
            'Spread treated seeds in shade for 2 hours to dry before bio-fertilizer inoculation.'
        ],
        'pro_tip': 'Strictly follow the FIR rule: Fungicide first, Insecticide second, and Rhizobium/Bio-agent LAST with a 24-hour interval.',
        'tool_url': '/crops/pesticides/',
        'tool_name': 'Pesticide & Fungicide Calculator'
    }

    card3 = {
        'id': 'tip-biological-seed-treatment',
        'task_id': 'planting',
        'task_name': 'Planting',
        'stage_id': 'sowing_nursery',
        'tag': 'Planting',
        'title': 'Seed biological treatments',
        'image': 'images/cultivation/plantix/seed-biological-treatment.jpg',
        'summary': 'Antagonistic biological seed coating with Trichoderma viride or Pseudomonas fluorescens.',
        'why': 'Bio-control agents colonize the root zone, secreting natural antibiotics that destroy soil pathogen mycelia.',
        'materials': ['Trichoderma viride 1% WP @ 4–5 g/kg seed OR Pseudomonas fluorescens @ 10 g/kg', 'Clean spray mister bottle'],
        'steps': [
            'Lightly mist chemical-treated, dried seeds with clean water to produce slight surface moisture.',
            'Sprinkle Trichoderma viride powder @ 4 g/kg seed evenly over the seed lot.',
            'Tumble seeds gently so the green biological powder adheres across every seed coat.',
            'Keep in shade for 30 minutes to allow fungal spores to firmly bind.',
            'Sow into moist soil within 24 hours of treatment.'
        ],
        'pro_tip': 'Never mix chemical copper fungicides or antibiotics directly with Trichoderma; copper destroys beneficial bio-fungi.',
        'tool_url': '/disease/',
        'tool_name': 'Disease Symptoms & Control'
    }

    # Timeline Group 2: 1 week before seedling
    if is_pulse:
        c4_title = "Rhizobium seed treatment"
        c4_sum = "High-potency bio-inoculation using jaggery sticky slurry for maximum nodule development."
        c4_why = "Ensures billions of active live nitrogen-fixing bacteria enter the rhizosphere right at germination."
    else:
        c4_title = "Bio-fertilizer liquid & slurry preparation"
        c4_sum = "Inoculate seeds with Azotobacter and PSB (Phosphate Solubilizing Bacteria) for nitrogen and phosphorus mobilization."
        c4_why = "Mobilizes 20–30 kg of fixed soil phosphorus and fixes atmospheric nitrogen organically."

    card4 = {
        'id': 'tip-rhizobium-measuring',
        'task_id': 'planting',
        'task_name': 'Planting',
        'stage_id': 'sowing_nursery',
        'tag': 'Planting',
        'title': c4_title,
        'image': 'images/cultivation/plantix/rhizobium-measuring-beaker.jpg',
        'summary': c4_sum,
        'why': c4_why,
        'materials': ['Bio-fertilizer culture @ 200 g/10 kg seed OR Liquid culture @ 50 ml/10 kg', 'Jaggery 50 g', 'Graduated measuring beaker / cup', 'Lukewarm non-chlorinated water (250 ml)'],
        'steps': [
            'Boil 50 g jaggery in 250 ml water for 10–15 minutes to prepare a sticky sugar solution.',
            'Cool the jaggery syrup completely to room temperature (heat kills live bacterial cultures).',
            'Measure exact bio-fertilizer dose in graduated beaker and stir into the cooled syrup.',
            'Sprinkle slurry over the seed lot on a clean plastic sheet and rub gently with hands.',
            'Dry seeds in shade for 30 minutes. Protect completely from direct sunlight.'
        ],
        'pro_tip': 'Always use unchlorinated well or rainwater; chlorinated municipal tap water degrades live bio-fertilizer counts.',
        'tool_url': '/crops/fertilizer/',
        'tool_name': 'Fertilizer & Nutrition Planner'
    }

    card5 = {
        'id': 'tip-kick-start-seedling',
        'task_id': 'planting',
        'task_name': 'Planting',
        'stage_id': 'sowing_nursery',
        'tag': 'Planting',
        'title': 'Here are some tips to give plants a kick-start',
        'image': 'images/cultivation/plantix/furrow-seed-sowing.jpg',
        'summary': 'Optimal seed depth, precision furrow opening, and starter band phosphorus placement for rapid emergence.',
        'why': 'Correct sowing depth prevents seed drying, bird scavenging, and ensures uniform 4-day seedling emergence.',
        'materials': ['Calibrated furrow opener or seed drill', 'Starter Single Super Phosphate (SSP) or DAP', 'Soil moisture meter'],
        'steps': [
            'Verify seedbed moisture before drilling: top 5 cm soil must be at field capacity.',
            'Maintain ideal furrow depth: 3 to 4 cm for small legume/vegetable seeds; 4 to 5 cm for cereals.',
            'Ensure calibrated row-to-row and plant-to-plant spacing according to variety guidelines.',
            'Place starter phosphorus 5 cm beside and 3 cm below seed row to feed emerging primary roots.',
            'Cover furrows with loose, well-aerated soil and lightly press for firm seed-to-soil contact.'
        ],
        'pro_tip': 'Never sow deeper than 5 cm—deep-sown seeds exhaust their endosperm food reserves before breaking through the soil crust.',
        'tool_url': '/crops/spacing/',
        'tool_name': 'Check Spacing Geometry'
    }

    # Timeline Group 3: At Sowing & Field Emergence
    card6 = {
        'id': 'tip-field-prep-fine-tilth',
        'task_id': 'field_prep',
        'task_name': 'Field Preparation',
        'stage_id': 'pre_sowing',
        'tag': 'Field Preparation',
        'title': 'Deep Summer Plowing & Fine Seedbed Preparation',
        'image': 'images/cultivation/plantix/weeding-hoe-field.jpg',
        'summary': 'Primary deep tillage to pulverize clods, break hard pans, and solarize against weed seeds and soil pests.',
        'why': 'Deep plowing exposes pupae of soil insects and perennial weed rhizomes to scorching solar heat.',
        'materials': ['Disc or moldboard plow', 'Secondary rotavator or cultivator', 'Wooden plank for leveling'],
        'steps': [
            'Perform 1 deep summer plowing (20–25 cm depth) using a disc or moldboard plow.',
            'Leave land exposed to summer sun for 10–14 days for natural soil solarization.',
            'Follow with 2 cross-harrowings to shatter clods into friable soil aggregates.',
            'Pass a rotavator once for fine tilth required for rapid root penetration.',
            'Level the plot with a wooden plank to prevent irrigation water stagnation in low patches.'
        ],
        'pro_tip': 'Laser land leveling saves up to 25% irrigation water and improves crop stand uniformity across the entire field.',
        'tool_url': '/crops/soil/',
        'tool_name': 'Soil Health & Tilth Analysis'
    }

    card7 = {
        'id': 'tip-organic-manure-incorporation',
        'task_id': 'fert_organic',
        'task_name': 'Fertilization Organic',
        'stage_id': 'pre_sowing',
        'tag': 'Fertilization Organic',
        'title': 'Basal Organic Manure & Vermicompost Application',
        'image': 'images/cultivation/plantix/fertilizer-organic-compost.jpg',
        'summary': 'Incorporate mature farmyard manure (FYM) or vermicompost fortified with neem cake during final harrowing.',
        'why': 'Supplies balanced secondary micronutrients, enhances cation exchange capacity (CEC), and feeds soil microflora.',
        'materials': ['Decomposed FYM @ 4–6 tonnes/acre OR Vermicompost @ 1.5–2 tonnes/acre', 'Neem cake @ 100 kg/acre'],
        'steps': [
            'Broadcast mature decomposed FYM uniformly over the plowed field 15 days before sowing.',
            'Add 100 kg neem cake per acre to repel subterranean termites and root-knot nematodes.',
            'Incorporate immediately into the top 15 cm soil using a cultivator or disc harrow.',
            'Avoid fresh, hot animal manure which releases toxic ammonia and attracts white grubs.'
        ],
        'pro_tip': 'Fortify FYM with Trichoderma viride (1 kg per 100 kg manure) 7 days before broadcasting to inoculate beneficial bio-agents.',
        'tool_url': '/crops/fertilizer/',
        'tool_name': 'Organic Manure Planner'
    }

    # Timeline Group 4: Vegetative & Intercultural Operations (15–35 Days)
    card8 = {
        'id': 'tip-critical-irrigation',
        'task_id': 'irrigation',
        'task_name': 'Irrigation',
        'stage_id': 'vegetative',
        'tag': 'Irrigation',
        'title': 'Critical Stage Irrigation & Moisture Management',
        'image': 'images/cultivation/plantix/irrigation-drip-sprinkler.jpg',
        'summary': 'Provide precision water at critical physiological milestones: branching, flowering, and pod/grain development.',
        'why': 'Moisture stress during branching or flowering triggers massive bud drop and cuts harvest yield by up to 35%.',
        'materials': ['Drip laterals (16 mm) OR well-graded furrow channels', 'Tensiometer or soil moisture probe'],
        'steps': [
            'Deliver light pre-sowing irrigation (paleva) to achieve field-capacity moisture for germination.',
            'First post-emergence irrigation at 20–25 days after sowing (branching/tillering stage).',
            'Second irrigation at 45–50 days (flowering initiation stage). Avoid waterlogging during bloom.',
            'Third irrigation at 65–70 days (grain development / pod filling stage).',
            'Ensure drainage channels are clear: standing water for >24 hrs causes root hypoxia and wilt.'
        ],
        'pro_tip': 'Operate drip irrigation early in the morning so the crop canopy stays dry overnight, preventing foliar blights.',
        'tool_url': '/crops/irrigation/',
        'tool_name': 'Irrigation Schedule Calculator'
    }

    card9 = {
        'id': 'tip-mechanical-weeding',
        'task_id': 'weeding',
        'task_name': 'Weeding',
        'stage_id': 'vegetative',
        'tag': 'Weeding',
        'title': 'Critical Period Weed Management (First 35 Days)',
        'image': 'images/cultivation/plantix/weeding-hoe-field.jpg',
        'summary': 'Manual weeding or wheel-hoe hoeing at 20 and 35 days after sowing to eliminate competition for sunlight and nutrients.',
        'why': 'Uncontrolled weeds rob up to 40% of applied N-P-K fertilizer and harbor early viral vector pests.',
        'materials': ['Twin-wheel hoe / peg weeder', 'Hand khurpi / weeding sickle'],
        'steps': [
            'Execute first hand weeding or wheel hoeing at 18–22 days when weeds are at 2–3 leaf stage.',
            'Loosen soil crust between crop rows to aerate root zone and conserve capillary moisture.',
            'Carry out second light weeding at 35 days prior to complete canopy closure.',
            'If grassy weeds dominate, apply recommended selective post-emergence herbicide under expert guidance.'
        ],
        'pro_tip': 'Keep the crop completely weed-free during the first 35 days—once the canopy closes, it naturally suppresses 90% of weed germination.',
        'tool_url': '/crops/weeding/',
        'tool_name': 'Weed Decision Support'
    }

    # Timeline Group 5: Flowering & Pest Protection (35–70 Days)
    card10 = {
        'id': 'tip-integrated-pest-management',
        'task_id': 'plant_protection',
        'task_name': 'Plant Protection Chemical',
        'stage_id': 'flowering',
        'tag': 'Plant Protection Chemical',
        'title': 'IPM & Safe Knapsack Spraying for Pests & Diseases',
        'image': 'images/cultivation/plantix/knapsack-crop-protection.jpg',
        'summary': 'Scout fields weekly and apply threshold-based bio-pesticides or recommended chemistries with calibrated knapsack sprayer.',
        'why': 'Targeting early instar larvae and sucking vectors before they multiply prevents economic damage without chemical over-reliance.',
        'materials': ['Yellow sticky traps (10/acre)', 'Neem oil 10,000 ppm (3 ml/L)', 'Calibrated hollow-cone knapsack sprayer', 'Safety goggles, mask and gloves'],
        'steps': [
            'Install yellow sticky traps for whiteflies/aphids and pheromone traps for caterpillar/borer moths.',
            'At early vegetative stage, spray Azadirachtin (Neem oil) 10,000 ppm @ 3 ml/L as an anti-feedant repellent.',
            'If insect count crosses Economic Threshold Level (ETL), spray recommended targeted chemistry.',
            'Calibrate knapsack hollow-cone nozzle to produce fine mist droplets covering the undersides of leaves.',
            'Spray during calm morning (7–10 AM) or late afternoon (4–6 PM) to safeguard pollinating bees.'
        ],
        'pro_tip': 'Always observe pre-harvest interval (PHI) of at least 7 to 10 days between last chemical spray and harvesting.',
        'tool_url': '/disease/',
        'tool_name': 'Leaf Disease & Spray Advisor'
    }

    card11 = {
        'id': 'tip-foliar-nutrition',
        'task_id': 'fert_chemical',
        'task_name': 'Fertilization Chemical',
        'stage_id': 'flowering',
        'tag': 'Fertilization Chemical',
        'title': 'Foliar Nutrient Booster & Flower Drop Prevention',
        'image': 'images/cultivation/plantix/fertilizer-organic-compost.jpg',
        'summary': 'Foliar spray of 13:0:45 (Potassium Nitrate) and Boron 20% to prevent flower drop and boost pod/fruit setting.',
        'why': 'Boron improves pollen tube germination while potassium accelerates carbohydrate translocation to developing grains/fruits.',
        'materials': ['Water soluble 13:0:45 @ 10 g/L (2 kg/acre)', 'Boron 20% (Disodium Octaborate) @ 1 g/L (200 g/acre)'],
        'steps': [
            'Dissolve 2 kg of 13:0:45 and 200 g Boron in 200 liters of water per acre.',
            'Spray evenly over crop canopy at flower bud initiation.',
            'Repeat second spray 15 days later during peak pod filling / fruit sizing.',
            'Avoid excessive high-nitrogen foliar sprays during flowering to prevent bud abortion.'
        ],
        'pro_tip': 'Never exceed 1 g/L for Boron—excess boron causes marginal leaf scorch and phytotoxicity.',
        'tool_url': '/crops/fertilizer/',
        'tool_name': 'Calculate Foliar Sprays'
    }

    # Timeline Group 6: Maturity, Harvesting & Mandi Selling
    card12 = {
        'id': 'tip-optimal-harvesting',
        'task_id': 'harvesting',
        'task_name': 'Harvesting',
        'stage_id': 'maturity_harvest',
        'tag': 'Harvesting',
        'title': 'Maturity Indices & Sickle Harvesting Technique',
        'image': 'images/cultivation/plantix/crop-harvest-sickle.jpg',
        'summary': 'Harvest when 80–85% pods/heads turn mature brown and grain moisture drops to field maturity.',
        'why': 'Harvesting at right physiological maturity prevents pod shattering in field and ensures bold, unwrinkled grain.',
        'materials': ['Sharp serrated sickles', 'Clean tarpaulin sheets', 'Clean threshing floor'],
        'steps': [
            'Harvest in early morning hours when dew moisture prevents pod shattering.',
            'Cut crop close to the ground using sharp serrated sickles.',
            'Stack harvested plants in small upright bundles on a clean tarpaulin for 2–3 days sun drying.',
            'Thresh dried bundles manually by gentle beating or through a multi-crop mechanical thresher.',
            'Winnow thoroughly to eliminate dust, chaff, and unfilled seeds.'
        ],
        'pro_tip': 'Set thresher cylinder speed to 400–500 RPM for pulse crops to avoid grain splitting and seed coat cracking.',
        'tool_url': '/crops/yield/',
        'tool_name': 'Yield & BCR Calculator'
    }

    card13 = {
        'id': 'tip-post-harvest-mandi',
        'task_id': 'post_harvest',
        'task_name': 'Post Harvest',
        'stage_id': 'post_harvest',
        'tag': 'Post Harvest',
        'title': 'Grading, Moisture Testing & APMC Mandi Realization',
        'image': 'images/cultivation/plantix/post-harvest-crates.jpg',
        'summary': 'Dry grain to 9% moisture, sort into Grade A lots, and compare live mandi prices on e-NAM.',
        'why': 'Graded produce with certified moisture level attracts ₹300–₹500 higher modal rate per quintal in wholesale auctions.',
        'materials': ['Grain moisture meter (target ≤ 9.5%)', 'Grading sieves', 'New HDPE / gunny bags with liners'],
        'steps': [
            'Sun-dry threshed produce until grain bites with a crisp snap (moisture ≤ 9%).',
            'Pass grain through grading sieves to separate Grade A (uniform bold grain) from Grade B.',
            'Pack graded lots into 50 kg gunny bags and label with crop name, grade, and harvest date.',
            'Check live prices and arrival volumes on e-NAM and KrishiMitra Market tool before dispatching vehicle.',
            'Deliver to APMC mandi early in the morning (4:30–6:00 AM) to catch primary auction bidding.'
        ],
        'pro_tip': 'Never store moist grain (>11%) in airtight bags; damp conditions trigger Aspergillus mold and aflatoxin contamination.',
        'tool_url': '/market/prices/',
        'tool_name': 'Live APMC Mandi Prices'
    }

    all_cards = [card1, card2, card3, card4, card5, card6, card7, card8, card9, card10, card11, card12, card13]

    # 12 Tasks definition matching Plantix Photo 1
    tasks_def = [
        {'id': 'monitoring', 'name': 'Monitoring', 'icon': 'bi-search', 'badge_color': '#2563eb', 'bg_color': '#eff6ff'},
        {'id': 'site_selection', 'name': 'Site Selection', 'icon': 'bi-geo-alt-fill', 'badge_color': '#059669', 'bg_color': '#ecfdf5'},
        {'id': 'field_prep', 'name': 'Field Preparation', 'icon': 'bi-hammer', 'badge_color': '#d97706', 'bg_color': '#fffbeb'},
        {'id': 'planting', 'name': 'Planting', 'icon': 'bi-sprout', 'badge_color': '#16a34a', 'bg_color': '#f0fdf4'},
        {'id': 'weeding', 'name': 'Weeding', 'icon': 'bi-scissors', 'badge_color': '#9333ea', 'bg_color': '#faf5ff'},
        {'id': 'irrigation', 'name': 'Irrigation', 'icon': 'bi-droplet-fill', 'badge_color': '#0284c7', 'bg_color': '#f0f9ff'},
        {'id': 'fert_organic', 'name': 'Fertilization Organic', 'icon': 'bi-recycle', 'badge_color': '#059669', 'bg_color': '#ecfdf5'},
        {'id': 'fert_chemical', 'name': 'Fertilization Chemical', 'icon': 'bi-bag-fill', 'badge_color': '#4f46e5', 'bg_color': '#eef2ff'},
        {'id': 'preventive', 'name': 'Preventive Measure', 'icon': 'bi-shield-check', 'badge_color': '#dc2626', 'bg_color': '#fef2f2'},
        {'id': 'plant_protection', 'name': 'Plant Protection Chemical', 'icon': 'bi-radioactive', 'badge_color': '#ea580c', 'bg_color': '#fff7ed'},
        {'id': 'harvesting', 'name': 'Harvesting', 'icon': 'bi-hand-index-thumb-fill', 'badge_color': '#ca8a04', 'bg_color': '#fefce8'},
        {'id': 'post_harvest', 'name': 'Post Harvest', 'icon': 'bi-box-seam-fill', 'badge_color': '#0891b2', 'bg_color': '#ecfeff'},
    ]

    task_cards_map = {t['id']: [] for t in tasks_def}
    for c in all_cards:
        if c['task_id'] in task_cards_map:
            task_cards_map[c['task_id']].append(c)
    if not task_cards_map['monitoring']:
        task_cards_map['monitoring'] = [card10]
    if not task_cards_map['site_selection']:
        task_cards_map['site_selection'] = [card6]
    if not task_cards_map['preventive']:
        task_cards_map['preventive'] = [card3]

    tasks = []
    for t in tasks_def:
        cards_for_task = task_cards_map[t['id']]
        tasks.append({
            'id': t['id'],
            'name': t['name'],
            'icon': t['icon'],
            'badge_color': t['badge_color'],
            'bg_color': t['bg_color'],
            'tip_count': len(cards_for_task),
            'cards': cards_for_task
        })

    # 6 Stages definition
    stages_def = [
        {'id': 'pre_sowing', 'name': 'Pre-Sowing & Land Prep', 'timeline': '2 to 4 weeks before seedling', 'icon': 'bi-calendar3'},
        {'id': 'sowing_nursery', 'name': 'Planting & Sowing', 'timeline': '1 to 2 weeks before / at seedling', 'icon': 'bi-sprout'},
        {'id': 'vegetative', 'name': 'Vegetative Growth & Weeding', 'timeline': '15 – 35 Days after planting', 'icon': 'bi-tree-fill'},
        {'id': 'flowering', 'name': 'Flowering & Fruit/Pod Setting', 'timeline': '35 – 70 Days', 'icon': 'bi-flower1'},
        {'id': 'maturity_harvest', 'name': 'Maturity & Harvesting', 'timeline': '70 – 110 Days', 'icon': 'bi-check2-circle'},
        {'id': 'post_harvest', 'name': 'Post-Harvest & Mandi Realization', 'timeline': 'Post-Harvest', 'icon': 'bi-shop'},
    ]

    stages_list = []
    for s in stages_def:
        cards_for_stage = [c for c in all_cards if c['stage_id'] == s['id']]
        stages_list.append({
            'id': s['id'],
            'name': s['name'],
            'timeline': s['timeline'],
            'icon': s['icon'],
            'cards': cards_for_stage
        })

    # Timeline groups matching Photo 2
    timeline_groups = [
        {
            'title': '2 weeks before seedling',
            'cards': [card1, card2, card3]
        },
        {
            'title': '1 week before seedling',
            'cards': [card4, card5]
        },
        {
            'title': 'At Sowing & Field Emergence',
            'cards': [card6, card7]
        },
        {
            'title': 'Vegetative & Intercultural Operations (15–35 Days)',
            'cards': [card8, card9]
        },
        {
            'title': 'Flowering & Pest Protection (35–70 Days)',
            'cards': [card10, card11]
        },
        {
            'title': 'Maturity, Harvesting & Mandi Realization',
            'cards': [card12, card13]
        }
    ]

    guide['tasks'] = tasks
    guide['stages_list'] = stages_list
    guide['timeline_groups'] = timeline_groups
    guide['all_cards'] = all_cards
    return guide


# ─────────────────────────────────────────────────────────────────────────────
# 1. TOMATO GUIDE (Sowing to Selling)
# ─────────────────────────────────────────────────────────────────────────────
def _tomato_guide(crop_data):
    return {
        'crop_name': 'Tomato',
        'hindi_name': 'टमाटर की वैज्ञानिक खेती एवं मंडी विपणन',
        'botanical_name': 'Solanum lycopersicum',
        'total_duration': '115 – 135 Days',
        'ideal_season': 'Kharif (Jun–Jul), Rabi (Oct–Nov), Zaid (Jan–Feb)',
        'expected_yield': '28 – 36 Tonnes / Acre (Hybrids)',
        'market_channel': 'APMC Vegetable Mandi, Ketchup/Puree Processors, e-NAM',
        'stages': [
            {
                'step_number': 1,
                'title': 'Seed Selection & Pro-Tray Nursery Raising',
                'hindi_title': 'बीज चयन, बीजोपचार एवं प्रो-ट्रे नर्सरी',
                'timeline': 'Day 0 – Day 25',
                'phase': 'Nursery Phase',
                'image': 'images/cultivation/universal-sowing.jpg',
                'image_caption': 'Healthy hybrid tomato seedlings in 98-cell pro-trays with sterilized coco-peat',
                'metrics': [
                    {'label': 'Seed Rate', 'value': '100 – 150 g / Acre', 'icon': 'bi-box-seam'},
                    {'label': 'Top Hybrids', 'value': 'Abhinav, US-440, Shivam', 'icon': 'bi-stars'},
                    {'label': 'Germination Temp', 'value': '22 – 28 °C', 'icon': 'bi-thermometer-half'},
                    {'label': 'Seedling Age', 'value': '21 – 25 Days', 'icon': 'bi-calendar-check'},
                ],
                'actions': [
                    'Choose high-yielding indeterminate or determinate hybrid varieties suited to your target market season (heat-tolerant for summer, blight-resistant for monsoon).',
                    'Treat seeds with Trichoderma viride @ 4 g/kg or Thiram @ 2 g/kg to eliminate damping-off and seed-borne pathogens.',
                    'Use 98-cell plastic pro-trays filled with a mixture of sterilized coco-peat, vermicompost, and perlite (ratio 3:1:1). Sow 1 seed per cell at 0.5 cm depth.',
                    'Keep trays in a shade-net house (50% shade) and irrigate using a fine-rose cane twice daily. Seedlings emerge in 4–6 days.',
                    'Four days before transplanting, harden seedlings by reducing watering and exposing them to partial direct sunlight.',
                ],
                'pro_tip': 'Drench nursery trays with Copper Oxychloride (2 g/L) 2 days prior to transplanting to eliminate fungal collar rot shock.',
                'tool_shortcut': {'name': 'Calculate Seeds & Fertilizer', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 2,
                'title': 'Main Field Preparation, Raised Beds & Drip Laying',
                'hindi_title': 'खेत की गहरी जुताई, मेड़ निर्माण व ड्रिप मल्चिंग',
                'timeline': 'Day 15 – Day 25',
                'phase': 'Land Preparation',
                'image': 'images/cultivation/universal-landprep.jpg',
                'image_caption': 'Laser-levelled field with raised beds, inline drip lateral lines, and silver-black mulch',
                'metrics': [
                    {'label': 'Ploughing', 'value': '2 Deep + 2 Rotavator', 'icon': 'bi-gear-wide-connected'},
                    {'label': 'Organic FYM', 'value': '8 – 10 Tonnes / Acre', 'icon': 'bi-flower1'},
                    {'label': 'Bed Height', 'value': '30 cm, Width 90 cm', 'icon': 'bi-arrows-expand'},
                    {'label': 'Mulch Film', 'value': '25–30 Micron Silver-Black', 'icon': 'bi-layers'},
                ],
                'actions': [
                    'Plough the land deeply (25–30 cm) with a mould-board plough, followed by 2 passes of rotavator to achieve a fine crumbly tilth.',
                    'Incorporate 8–10 tonnes of well-decomposed FYM mixed with Trichoderma and Pseudomonas (2 kg each) during final harrowing.',
                    'Form raised beds: top width 90 cm, height 30 cm, furrow width 50 cm. Raised beds prevent waterlogging and root asphyxiation during heavy rain.',
                    'Lay 16 mm inline drip laterals with 40 cm dripper spacing (2–4 LPH discharge) at the center of each bed.',
                    'Cover beds with 25–30 micron silver-black UV-stabilized mulch film. Punch transplanting holes at 45–60 cm staggered spacing.',
                ],
                'pro_tip': 'Silver mulch reflects sunlight to repel aphids and whiteflies, lowers root-zone soil temperature by 3–5°C, and suppresses 95% of weed growth.',
                'tool_shortcut': {'name': 'Check Soil Health Parameters', 'url': '/crops/'},
            },
            {
                'step_number': 3,
                'title': 'Field Transplanting & Establishment Drenching',
                'hindi_title': 'पौध रोपाई, कतार दूरी एवं शुरुआती ड्रेंचिंग',
                'timeline': 'Day 25 – Day 35',
                'phase': 'Transplanting',
                'image': 'images/cultivation/tomato-transplant.jpg',
                'image_caption': 'Transplanting sturdy 25-day tomato saplings into mulch holes during cool late afternoon',
                'metrics': [
                    {'label': 'Plant Spacing', 'value': '60 cm × 45 cm (Staggered)', 'icon': 'bi-rulers'},
                    {'label': 'Plant Density', 'value': '6,500 – 7,200 Plants/Acre', 'icon': 'bi-grid-3x3'},
                    {'label': 'Best Time', 'value': 'Late Afternoon (3 PM – 6 PM)', 'icon': 'bi-clock'},
                    {'label': 'Root Drenching', 'value': 'Humic Acid + Starter Fungicide', 'icon': 'bi-droplet-half'},
                ],
                'actions': [
                    'Select only stocky seedlings (12–15 cm height with 4–5 true leaves) with healthy white fibrous root balls.',
                    'Pre-irrigate beds through drip for 2 hours before planting so the root-zone soil has optimal field-capacity moisture.',
                    'Transplant in the late afternoon or cloudy weather to prevent transplant shock and heat desiccation.',
                    'Firm the soil gently around the collar region without burying the stem too deep. Immediately give 15 minutes of light drip watering.',
                    'On Day 3, drench each plant collar with Humic Acid (2 ml/L) + Carbendazim (1.5 g/L) to encourage vigorous root establishment.',
                ],
                'pro_tip': 'Replace any dead or stunted plants within 5–7 days of transplanting to maintain uniform plant population across the entire acre.',
                'tool_shortcut': {'name': 'Field Decision & Net Margin', 'url': '/crops/yield/'},
            },
            {
                'step_number': 4,
                'title': 'Drip Irrigation & Stage-Specific Fertigation',
                'hindi_title': 'ड्रिप सिंचाई एवं अवस्था अनुसार घुलनशील खाद प्रबंधन',
                'timeline': 'Day 30 – Day 110',
                'phase': 'Vegetative Care',
                'image': 'images/cultivation/tomato-irrigation.jpg',
                'image_caption': 'Inline drip emitters delivering precision water and dissolved NPK nutrients directly to root zone',
                'metrics': [
                    {'label': 'Water Frequency', 'value': 'Daily 1.5 – 2.5 hrs (by season)', 'icon': 'bi-droplet'},
                    {'label': 'Vegetative NPK', 'value': '19:19:19 @ 3 kg/acre/week', 'icon': 'bi-capsule'},
                    {'label': 'Flowering NPK', 'value': '12:61:00 & 0:52:34', 'icon': 'bi-flower2'},
                    {'label': 'Fruiting NPK', 'value': '13:00:45 (Potassium Nitrate)', 'icon': 'bi-gem'},
                ],
                'actions': [
                    'Operate drip irrigation early morning to keep foliage dry during nights, minimizing fungal foliar infection risks.',
                    'Vegetative Stage (Days 30–50): Apply 19:19:19 @ 3 kg/acre twice a week to foster strong stem caliber and lush canopy development.',
                    'Flowering & Fruit Set (Days 50–75): Switch to 12:61:00 (Mono Ammonium Phosphate) and 0:52:34 to promote abundant flower clusters and prevent bud drop.',
                    'Fruit Enlargement (Days 75–115): Supply Potassium Nitrate (13:0:45) @ 4 kg/acre along with Calcium Nitrate (2.5 kg/acre) + Boron (250 g/acre).',
                    'Avoid sudden fluctuations in soil moisture during fruit development; irregular watering causes blossom-end rot and fruit skin cracking.',
                ],
                'pro_tip': 'Calcium + Boron foliar spray at 60 and 80 days increases tomato skin thickness, preventing sun-scald and doubling transit shelf-life.',
                'tool_shortcut': {'name': 'Calculate Precise Fertigation Dose', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 5,
                'title': 'Staking, Trellising & Canopy De-Suckering',
                'hindi_title': 'बांस स्टेकिंग, सहारा बांधना व कटाई-छंटाई',
                'timeline': 'Day 35 – Day 55',
                'phase': 'Canopy Management',
                'image': 'images/cultivation/tomato-staking.jpg',
                'image_caption': 'Trellised tomato vines trained upward on bamboo stakes and polypropylene twine with heavy green fruit clusters',
                'metrics': [
                    {'label': 'Staking Material', 'value': 'Bamboo Poles (2m) + GI Wire', 'icon': 'bi-tree'},
                    {'label': 'Twine', 'value': 'UV Polypropylene Twine', 'icon': 'bi-link-45deg'},
                    {'label': 'Pruning System', 'value': '2-Leader or 3-Leader Stem', 'icon': 'bi-scissors'},
                    {'label': 'Yield Increase', 'value': '+35% to +45% Grade-A Fruit', 'icon': 'bi-graph-up-arrow'},
                ],
                'actions': [
                    'Erect sturdy bamboo or eucalyptus poles (2–2.5 m length) every 3 meters along the bed rows when plants reach 30 cm height.',
                    'Run 16-gauge GI wire horizontally at heights of 60 cm, 120 cm, and 180 cm above the beds.',
                    'Train plants vertically using soft UV twine tied loosely below leaf nodes, guiding stems upward as they grow.',
                    'Prune side suckers (axillary shoots) emerging from leaf axils up to 30 cm from the ground; maintain 2 main productive leader branches.',
                    'Remove older, yellowing bottom leaves touching the ground to promote cross-canopy airflow and prevent soil-borne spore splash.',
                ],
                'pro_tip': 'Staked tomatoes produce clean, uniform, disease-free fruits that fetch ₹4–₹7 per kg higher price in wholesale mandis than ground-crawling crops.',
                'tool_shortcut': {'name': 'Check Weather & Wind Advisory', 'url': '/weather/'},
            },
            {
                'step_number': 6,
                'title': 'Integrated Pest & Disease Defense (IPM)',
                'hindi_title': 'एकीकृत कीट व रोग प्रबंधन (फल छेदक, झुलसा व वायरस)',
                'timeline': 'Day 40 – Day 120',
                'phase': 'Crop Protection',
                'image': 'images/cultivation/universal-pest.jpg',
                'image_caption': 'Pheromone traps and yellow sticky sheets deployed in tomato field for biological pest suppression',
                'metrics': [
                    {'label': 'Yellow Sticky Traps', 'value': '20 – 25 Traps / Acre', 'icon': 'bi-shield-check'},
                    {'label': 'Pheromone Traps', 'value': 'Helicoverpa Lures (8/Acre)', 'icon': 'bi-radar'},
                    {'label': 'Key Pests', 'value': 'Fruit Borer, Whitefly, Thrips', 'icon': 'bi-bug'},
                    {'label': 'Key Diseases', 'value': 'Early Blight, Leaf Curl, Canker', 'icon': 'bi-virus'},
                ],
                'actions': [
                    'Install yellow sticky traps (for whiteflies) and blue sticky traps (for thrips) at canopy height to halt Tomato Leaf Curl Virus transmission.',
                    'Hang 8 pheromone traps per acre with Helilure septa to monitor and trap adult Helicoverpa armigera fruit borer moths.',
                    'Spray Neem Oil 10,000 ppm (2.5 ml/L) or Beauveria bassiana (5 g/L) preventively every 12–15 days to suppress sucking pest nymphs.',
                    'At first sight of early blight spots: spray Azoxystrobin 18.2% + Difenoconazole 11.4% SC (1 ml/L) or Mancozeb 75% WP (2.5 g/L).',
                    'For fruit borer caterpillars: apply Chlorantraniliprole 18.5% SC (Coragen) @ 0.3 ml/L or Emamectin Benzoate 5% SG @ 0.4 g/L during evening hours.',
                ],
                'pro_tip': 'Always observe a 3–5 day Waiting Period (Pre-Harvest Interval) after any synthetic spray before picking ripe fruit for the mandi.',
                'tool_shortcut': {'name': 'Identify Disease via Photo Scan', 'url': '/disease/'},
            },
            {
                'step_number': 7,
                'title': 'Harvesting at Target Market Maturity Stage',
                'hindi_title': 'बाजार अनुसार वैज्ञानिक तुड़ाई (ब्रेकर व लाल अवस्था)',
                'timeline': 'Day 65 – Day 130',
                'phase': 'Harvesting',
                'image': 'images/cultivation/tomato-harvest.jpg',
                'image_caption': 'Farmers harvesting blemish-free tomatoes with retained calyx during cool morning hours',
                'metrics': [
                    {'label': 'Picking Interval', 'value': 'Every 3 – 4 Days', 'icon': 'bi-hourglass-split'},
                    {'label': 'Distant Market', 'value': 'Breaker / Turning Stage (10-20% Pink)', 'icon': 'bi-truck'},
                    {'label': 'Local Mandi', 'value': 'Pink / Light Red Stage', 'icon': 'bi-shop'},
                    {'label': 'Total Pickings', 'value': '12 – 18 Flushes', 'icon': 'bi-repeat'},
                ],
                'actions': [
                    'Harvest fruit strictly in the early morning (6 AM – 10 AM) or late afternoon after field heat dissipates to retain turgidity and shelf freshness.',
                    'For Distant Markets & Export (>200 km): Pick at the "Breaker Stage" (when fruit tip shows a pink-yellow break). They ripen naturally in transit without bruising.',
                    'For Local APMC Mandi (<50 km): Harvest at "Pink to Light Red Stage" with firm flesh for immediate auction.',
                    'Gently twist and snap the fruit stalk keeping the green star calyx intact; this preserves fruit freshness and confirms freshness to buyers.',
                    'Place harvested fruits gently into clean plastic harvest crates lined with newspaper or foam; never throw fruit into gunny sacks.',
                ],
                'pro_tip': 'Never wash freshly picked tomatoes with cold water immediately in the field; field heat contrast creates hydrostatic pressure that draws bacterial rot spores inside.',
                'tool_shortcut': {'name': 'Harvest Forecast & Weather', 'url': '/weather/'},
            },
            {
                'step_number': 8,
                'title': 'Post-Harvest Sorting, Grading & Crating',
                'hindi_title': 'सफाई, ग्रेडिंग (A/B/C) एवं 25 किलो क्रेट पैकिंग',
                'timeline': 'Immediately Post-Harvest',
                'phase': 'Post-Harvest',
                'image': 'images/cultivation/tomato-crates.jpg',
                'image_caption': 'Uniformly graded A-grade round tomatoes packed neatly in standard 25 kg plastic crates',
                'metrics': [
                    {'label': 'Grade A (Premium)', 'value': 'Firm, 80–110g, Uniform Red', 'icon': 'bi-award'},
                    {'label': 'Grade B (Local)', 'value': 'Medium Size, Minor Scratches', 'icon': 'bi-check-circle'},
                    {'label': 'Grade C (Processing)', 'value': 'Odd Shape / Ketchup Unit', 'icon': 'bi-cup-hot'},
                    {'label': 'Standard Pack', 'value': '22 – 25 kg Plastic Crates', 'icon': 'bi-box'},
                ],
                'actions': [
                    'Move harvested crates immediately to a clean, well-ventilated farm shed or shady tree canopy to remove residual field heat.',
                    'Sort and discard sun-scalded, cracked, or pest-bored fruit into a separate compost bin.',
                    'Grade into Grade A (large, smooth, flawless, uniform shape), Grade B (medium size, good quality), and Grade C (over-ripe / small).',
                    'Pack strictly in sanitized plastic ventilated crates holding 22–25 kg per crate. Stack crates maximum 5 layers high in transport vehicles.',
                    'Affix a lot label with Variety, Grade, Weight, and Date of Harvest to attract institutional buyers and supermarket aggregators.',
                ],
                'pro_tip': 'Grading your harvest into separate A and B grade crates increases total gross revenue by 20–25% compared to selling un-sorted mixed batches.',
                'tool_shortcut': {'name': 'Track Current Mandi Prices', 'url': '/market/'},
            },
            {
                'step_number': 9,
                'title': 'APMC Mandi Selling, Logistics & Profit Maximization',
                'hindi_title': 'मंडी नीलामी, ई-नाम विपणन, परिवहन व शुद्ध मुनाफा',
                'timeline': 'Market Days (Morning 5 AM – 10 AM)',
                'phase': 'Commercial & Selling',
                'image': 'images/cultivation/universal-mandi.jpg',
                'image_caption': 'Bustling APMC wholesale market auction with competitive bidding for graded tomato lots',
                'metrics': [
                    {'label': 'Wholesale Mandis', 'value': 'Azadpur, Vashi, Kolar, Madanapalle', 'icon': 'bi-geo-alt'},
                    {'label': 'Logistics', 'value': 'Open-mesh / Tarpaulin Pickup', 'icon': 'bi-truck'},
                    {'label': 'e-NAM Portal', 'value': 'Online Single-Window Auction', 'icon': 'bi-globe2'},
                    {'label': 'Net Margin Target', 'value': '₹1,20,000 – ₹1,80,000 / Acre', 'icon': 'bi-cash-coin'},
                ],
                'actions': [
                    'Track live modal prices on the KrishiMitra Market Price tracker and e-NAM portal across nearby mandis before loading the truck.',
                    'Dispatch transport vehicles in the evening so produce arrives at the APMC yard between 3:00 AM – 5:00 AM before wholesale bidding begins.',
                    'Cover crates with clean canvas or ventilated mesh sheets to prevent wind-drying and road dust contamination during transport.',
                    'Engage with licensed Commission Agents (Aadathiya) or FPO collective marketing to secure instant transparent electronic weighment.',
                    'Explore direct contracts with local hotel chains, food processing companies, and modern retail chains (Reliance, Blinkit, Zepto, BigBasket) to bypass intermediary margins.',
                ],
                'pro_tip': 'During market gluts when prices fall below ₹8/kg, utilize low-cost solar dehydration to produce sun-dried tomato flakes or sell to puree processors.',
                'tool_shortcut': {'name': 'Explore Live Mandi Prices', 'url': '/market/'},
            },
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. WHEAT GUIDE (Sowing to Selling)
# ─────────────────────────────────────────────────────────────────────────────
def _wheat_guide(crop_data):
    return {
        'crop_name': 'Wheat',
        'hindi_name': 'गेहूं की उन्नत खेती एवं एमएसपी (MSP) मंडी विपणन',
        'botanical_name': 'Triticum aestivum',
        'total_duration': '120 – 140 Days',
        'ideal_season': 'Rabi (November 1 – November 25)',
        'expected_yield': '20 – 26 Quintals / Acre (50–65 Qtl/Ha)',
        'market_channel': 'FCI / State Procurement at MSP, Flour Millers, APMC Mandi',
        'stages': [
            {
                'step_number': 1,
                'title': 'Certified Seed Selection & Fungicidal Treatment',
                'hindi_title': 'प्रमाणित बीज चयन एवं बीजोपचार',
                'timeline': 'October 25 – November 15',
                'phase': 'Seed & Sowing',
                'image': 'images/cultivation/wheat-sowing.jpg',
                'image_caption': 'Certified high-yielding wheat seed treated with bio-fungicide and seed-drill loaded',
                'metrics': [
                    {'label': 'Seed Rate', 'value': '40 – 45 kg / Acre', 'icon': 'bi-box-seam'},
                    {'label': 'Top Varieties', 'value': 'HD-2967, DBW-187, PBW-343', 'icon': 'bi-stars'},
                    {'label': 'Sowing Window', 'value': '1 Nov – 20 Nov (Timely)', 'icon': 'bi-calendar-check'},
                    {'label': 'Seed Depth', 'value': '4 – 5 cm Depth', 'icon': 'bi-rulers'},
                ],
                'actions': [
                    'Procure certified high-yielding rust-resistant varieties recommended by ICAR-IIWBR (e.g., HD-3086, DBW-187 Karan Vandana, PBW-550, Shriram Super).',
                    'Seed Treatment: Treat seed with Carbendazim 50 WP (2 g/kg) or Trichoderma viride (4 g/kg) to prevent loose smut and flag smut.',
                    'For termite-prone soils: Mix Chlorpyrifos 20 EC @ 4 ml/kg seed with 20 ml water and coat seeds evenly on clean tarpaulin.',
                    'Air-dry treated seeds in shade for 2 hours before loading into the seed drill box.',
                ],
                'pro_tip': 'Sowing between November 5–15 gives maximum tillering and avoids terminal heat stress during grain-filling in March.',
                'tool_shortcut': {'name': 'Calculate Wheat Seed & Basal Nutrients', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 2,
                'title': 'Rotavator / Zero-Tillage Sowing & Basal Nutrients',
                'hindi_title': 'जीरो टिलेज / हैप्पी सीडर बुवाई व बेसल खाद',
                'timeline': 'Day 0 – Day 5',
                'phase': 'Land Preparation',
                'image': 'images/cultivation/wheat-sowing.jpg',
                'image_caption': 'Tractor-drawn seed-cum-fertilizer drill placing seeds and fertilizer simultaneously in moist soil',
                'metrics': [
                    {'label': 'Row Spacing', 'value': '20 – 22.5 cm Row-to-Row', 'icon': 'bi-rulers'},
                    {'label': 'DAP Basal', 'value': '50 kg / Acre (1 Bag)', 'icon': 'bi-box'},
                    {'label': 'MOP (Potash)', 'value': '20 – 25 kg / Acre', 'icon': 'bi-gem'},
                    {'label': 'Zinc Sulphate', 'value': '10 kg / Acre (21% Zn)', 'icon': 'bi-capsule'},
                ],
                'actions': [
                    'Adopt Happy Seeder or Zero-Till Drill directly into paddy residue to preserve soil organic carbon, save ₹2,000/acre in fuel, and conserve moisture.',
                    'In conventionally prepared fields: Plough twice with disc harrow and 1 pass with planker (patela) to conserve underground moisture.',
                    'Apply entire Phosphorus (50 kg DAP), Potassium (20 kg MOP), and Zinc Sulphate (10 kg) at sowing time through fertilizer drill below the seed zone.',
                    'Maintain seed sowing depth at 4–5 cm. Sowing deeper than 6 cm severely delays emergence and reduces tillers.',
                ],
                'pro_tip': 'Never broadcast DAP on topsoil; placing it 2 cm below seed level increases phosphorus uptake efficiency by 40%.',
                'tool_shortcut': {'name': 'Check Fertilizer Combination', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 3,
                'title': 'Crown Root Irrigation (CRI) & First Top Dressing',
                'hindi_title': 'क्राउन रूट (CRI) प्रथम सिंचाई एवं यूरिया टॉप ड्रेसिंग',
                'timeline': 'Day 20 – Day 25',
                'phase': 'Critical Irrigation',
                'image': 'images/cultivation/wheat-tillering.jpg',
                'image_caption': 'Lush green wheat field at crown root initiation stage showing active root anchorage and first tillers',
                'metrics': [
                    {'label': 'Critical Stage', 'value': 'Crown Root Initiation (CRI)', 'icon': 'bi-water'},
                    {'label': 'Urea Top-Dress', 'value': '45 kg / Acre (1 Bag Neem Urea)', 'icon': 'bi-capsule'},
                    {'label': 'Water Depth', 'value': '5 – 6 cm Light Irrigation', 'icon': 'bi-droplet-half'},
                    {'label': 'Weed Status', 'value': 'Scout for Phalaris minor', 'icon': 'bi-search'},
                ],
                'actions': [
                    'The Crown Root Initiation (CRI) stage at 20–25 days after sowing is the single most critical irrigation of wheat. Missing it drops yield by 25–30%.',
                    'Provide a light, uniform irrigation (5–6 cm depth). Waterlogging at this stage turns young seedlings yellow.',
                    'Apply first split dose of Nitrogen: 45 kg Neem-Coated Urea per acre when the soil reaches field capacity (vattar condition).',
                    'Scout for young weed seedlings: Canary grass (Gullidanda / Mandusi) and Chenopodium (Bathua).',
                ],
                'pro_tip': 'Apply Sulfosulfuron 75% + Metsulfuron 5% WG (Leader/Total) @ 16 g/acre at 30–35 days to control both broadleaf and grass weeds in one spray.',
                'tool_shortcut': {'name': 'Check Weather & Irrigation Window', 'url': '/weather/'},
            },
            {
                'step_number': 4,
                'title': 'Tillering, Jointing & 6-Stage Irrigation Scheduling',
                'hindi_title': 'फुटाव, गांठ बनने की अवस्था व 6 क्रांतिकालीन सिंचाई',
                'timeline': 'Day 30 – Day 90',
                'phase': 'Vegetative Care',
                'image': 'images/cultivation/wheat-tillering.jpg',
                'image_caption': 'Dense tillering canopy with 4 to 6 vigorous tillers per plant forming a continuous green carpet',
                'metrics': [
                    {'label': 'Total Irrigations', 'value': '5 – 6 Timely Irrigations', 'icon': 'bi-droplet'},
                    {'label': 'Stage 2 (40-45d)', 'value': 'Tillering Stage Irrigation', 'icon': 'bi-calendar3'},
                    {'label': 'Stage 3 (60-65d)', 'value': 'Late Jointing Stage', 'icon': 'bi-calendar3'},
                    {'label': 'Stage 4 (80-85d)', 'value': 'Flowering / Boot Stage', 'icon': 'bi-calendar3'},
                ],
                'actions': [
                    'Apply 2nd top-dressing of Urea (45 kg/acre) before second irrigation at tillering stage (40–45 days). Complete all nitrogen by 50 days.',
                    'Stage 3 Irrigation at Jointing (60–65 days) ensures elongation of productive stems and supports large earhead formation.',
                    'Stage 4 Irrigation at Boot / Flowering stage (80–85 days) prevents floret sterility and ensures 40–50 grains per earhead.',
                    'Foliar nutrition: Spray 13:0:45 (Potassium Nitrate) @ 1 kg/100 L water at boot stage to enhance cold tolerance and grain filling.',
                ],
                'pro_tip': 'Never irrigate on windy days during flowering and grain filling to prevent severe crop lodging (falling down).',
                'tool_shortcut': {'name': 'Scout for Rust & Blight', 'url': '/disease/'},
            },
            {
                'step_number': 5,
                'title': 'Yellow Rust Defense & Grain Milking Protection',
                'hindi_title': 'पीला रतुआ रोकथाम एवं दुग्धिया अवस्था सुरक्षा',
                'timeline': 'Day 90 – Day 115',
                'phase': 'Crop Protection',
                'image': 'images/cultivation/wheat-ripening.jpg',
                'image_caption': 'Healthy, rust-free golden wheat earheads filling with plump grains under clear sunny skies',
                'metrics': [
                    {'label': 'Key Disease', 'value': 'Yellow / Stripe Rust (Puccinia)', 'icon': 'bi-virus'},
                    {'label': 'Key Pest', 'value': 'Wheat Aphids (Mahua)', 'icon': 'bi-bug'},
                    {'label': 'Fungicide', 'value': 'Propiconazole 25 EC (Tilt)', 'icon': 'bi-shield-shaded'},
                    {'label': 'Milking Stage', 'value': '100 – 105 Days After Sowing', 'icon': 'bi-clock'},
                ],
                'actions': [
                    'Regularly inspect fields for yellow stripes on leaves (Yellow Rust / Peeli Kungi). If observed, immediately spray Propiconazole 25 EC (Tilt) @ 200 ml in 200 L water/acre.',
                    'Monitor for Wheat Aphids clustering on earheads during cloudy, humid weather. If population exceeds 10–15 aphids/earhead, spray Thiamethoxam 25 WG @ 50 g/acre.',
                    'Stage 5 Irrigation at Milk Stage (100–105 days) ensures plump, heavy grains with high test weight (1000-grain weight > 42g).',
                    'Stage 6 Light Irrigation at Dough Stage (115–120 days) prevents early shrivelling of grain under rising March temperatures.',
                ],
                'pro_tip': 'Terminal heat mitigation: Spray 0.5% Potassium Chloride (5 g/L) or 0.2% Boron at grain filling to safeguard yield against sudden heat waves.',
                'tool_shortcut': {'name': 'Scan Leaf for Rust', 'url': '/disease/'},
            },
            {
                'step_number': 6,
                'title': 'Combine Harvesting at Optimal Grain Moisture',
                'hindi_title': 'कंबाइन हार्वेस्टर से वैज्ञानिक कटाई (नमी < 12%)',
                'timeline': 'Day 125 – Day 140 (April)',
                'phase': 'Harvesting',
                'image': 'images/cultivation/wheat-harvest.jpg',
                'image_caption': 'Modern combine harvester harvesting mature golden wheat field and unloading golden grain',
                'metrics': [
                    {'label': 'Harvest Moisture', 'value': '10% – 12% Grain Moisture', 'icon': 'bi-moisture'},
                    {'label': 'Maturity Sign', 'value': 'Golden Straw & Hard Grain', 'icon': 'bi-check2-circle'},
                    {'label': 'Average Yield', 'value': '20 – 26 Quintals / Acre', 'icon': 'bi-trophy'},
                    {'label': 'Combine Speed', 'value': '3 – 4 km/hr for Zero Loss', 'icon': 'bi-speedometer2'},
                ],
                'actions': [
                    'Harvest when grains become hard, crack with a clear sound between teeth, and straw turns completely dry golden-yellow.',
                    'Ensure combine harvester reel speed and concave clearance are calibrated to avoid grain breakage (<1.5% broken grains).',
                    'Collect straw using a Straw Reaper to recover 1.5–2.0 tonnes of valuable cattle fodder (Bhoosa / Turi) per acre worth ₹8,000–₹12,000.',
                    'Never burn wheat stubble; incorporate remnants into soil using a reversible MB plough to enhance organic carbon.',
                ],
                'pro_tip': 'Harvesting when grain moisture is above 14% invites fungal heating in storage; below 10% causes shattering loss during cutting.',
                'tool_shortcut': {'name': 'Calculate Crop Harvest Margin', 'url': '/crops/yield/'},
            },
            {
                'step_number': 7,
                'title': 'Grain Cleaning, Jute Bag Packing & APMC Mandi MSP Selling',
                'hindi_title': 'दाना सफाई, बोरी पैकिंग व सरकारी एमएसपी (MSP) पर बिक्री',
                'timeline': 'April – May (Harvest Season)',
                'phase': 'Commercial & Selling',
                'image': 'images/cultivation/wheat-selling.jpg',
                'image_caption': 'Standard 50 kg jute gunny bags of wheat stacked at APMC Mandi procurement center for FCI auction',
                'metrics': [
                    {'label': 'Govt MSP', 'value': 'Official Minimum Support Price', 'icon': 'bi-award'},
                    {'label': 'Procurement', 'value': 'FCI / NAFED / State Mandi Board', 'icon': 'bi-building'},
                    {'label': 'Standard Bag', 'value': '50 kg Clean Jute Gunny Bag', 'icon': 'bi-bag'},
                    {'label': 'Storage Rule', 'value': 'Moisture < 12%, Aluminum Phosphide', 'icon': 'bi-shield-lock'},
                ],
                'actions': [
                    'Winnow and clean grain to remove chaff, weed seeds, and broken kernels to satisfy FCI Fair Average Quality (FAQ) norms (foreign matter <0.75%).',
                    'Pack in standard 50 kg new B-Twill jute gunny bags. Stencil lot number and farmer registration details.',
                    'Register beforehand on the state government procurement portal (e-Uparjan / Meri Fasal Mera Byora / e-Kharid) with Aadhaar and bank details.',
                    'Book your procurement slot online to deliver wheat directly to the designated FCI/Mandi center, avoiding long mandi queues.',
                    'Payment is credited directly to the farmer’s bank account via DBT within 48–72 hours of electronic weightment receipt (J-Form).',
                ],
                'pro_tip': 'For private storage: Place 1 tablet of Aluminum Phosphide (3g) per tonne in airtight silos to keep wheat insect-free for 12 months.',
                'tool_shortcut': {'name': 'Check Live Wheat Mandi & MSP Prices', 'url': '/market/'},
            },
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. RICE / PADDY GUIDE
# ─────────────────────────────────────────────────────────────────────────────
def _rice_guide(crop_data):
    return {
        'crop_name': 'Rice (Paddy)',
        'hindi_name': 'धान की उन्नत खेती, नर्सरी से चावल मिल/मंडी बिक्री',
        'botanical_name': 'Oryza sativa',
        'total_duration': '125 – 145 Days',
        'ideal_season': 'Kharif (June–July Nursery, July Transplanting)',
        'expected_yield': '24 – 32 Quintals / Acre (Paddy)',
        'market_channel': 'Govt MSP Mandi Procurement, Rice Millers, Basmati Exporters',
        'stages': [
            {
                'step_number': 1,
                'title': 'Seed Selection, Salt Water Soaking & Wet Nursery',
                'hindi_title': 'बीज शोधन, नमक पानी घोल व गीली नर्सरी',
                'timeline': 'Day 0 – Day 25',
                'phase': 'Nursery Phase',
                'image': 'images/cultivation/universal-sowing.jpg',
                'image_caption': 'Lush green mat nursery of healthy paddy seedlings ready for transplanting',
                'metrics': [
                    {'label': 'Seed Rate', 'value': '15 – 18 kg/Acre (Hybrids: 6 kg)', 'icon': 'bi-box-seam'},
                    {'label': 'Varieties', 'value': 'PR-126, Pusa-44, Basmati 1509', 'icon': 'bi-stars'},
                    {'label': 'Salt Test', 'value': '10% Brine (Egg floats)', 'icon': 'bi-water'},
                    {'label': 'Seedling Age', 'value': '21 – 25 Days', 'icon': 'bi-calendar-check'},
                ],
                'actions': [
                    'Immerse seeds in 10% brine water solution (1 kg common salt in 10 L water); reject lightweight floating seeds and retain dense sunken seeds.',
                    'Wash seeds thoroughly with fresh water twice, then treat with Carbendazim 50 WP (2 g/kg) + Streptocycline (1 g/10 kg seed) to prevent bacterial leaf blight.',
                    'Sprout seeds by soaking in clean water for 24 hours, then keep in moist gunny bags in shade for 24–36 hours until white radicles emerge.',
                    'Sow sprouted seeds uniformly on raised wet nursery beds (1 meter wide with drainage channels). Apply 5 kg Urea + 10 kg SSP per 100 sq. meter nursery area.',
                ],
                'pro_tip': 'For machine transplanting (SRI or transplanter), raise mat seedlings in plastic trays (60x30 cm) with sieved soil and vermicompost.',
                'tool_shortcut': {'name': 'Calculate Nursery & Basal Fertilizer', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 2,
                'title': 'Puddle Land Preparation & Basal Nutrient Incorporation',
                'hindi_title': 'खेत की कद्दू (लेव/पडलिंग) जुताई व बेसल खाद',
                'timeline': 'Day 20 – Day 25',
                'phase': 'Land Preparation',
                'image': 'images/cultivation/universal-landprep.jpg',
                'image_caption': 'Tractor with cage wheels puddling flooded field and planking to create an impermeable hard pan',
                'metrics': [
                    {'label': 'Puddling', 'value': '2 Cross Puddlings with Water', 'icon': 'bi-gear'},
                    {'label': 'DAP Basal', 'value': '35 kg / Acre', 'icon': 'bi-box'},
                    {'label': 'MOP (Potash)', 'value': '20 kg / Acre', 'icon': 'bi-gem'},
                    {'label': 'Zinc Sulphate', 'value': '10 kg / Acre (Zinc deficiency cure)', 'icon': 'bi-capsule'},
                ],
                'actions': [
                    'Flood the field with 5–7 cm water 2 days before puddling. Run tractor with cage wheels twice to churn soil into a smooth slurry.',
                    'Puddling destroys soil macropores to create an impermeable subsurface pan, cutting water percolation loss by 60%.',
                    'Level perfectly using a wooden plank (patela / sohaga). Uneven fields lead to patchy weed infestation and uneven fertilizer distribution.',
                    'Broadcast basal fertilizer: 35 kg DAP + 20 kg MOP + 10 kg Zinc Sulphate (21%) per acre and incorporate into puddle during planking.',
                ],
                'pro_tip': 'Never mix Zinc Sulphate with DAP or SSP in the same bag; zinc and phosphate react to form insoluble zinc phosphate which plants cannot absorb.',
                'tool_shortcut': {'name': 'Check Zinc & Fertilizer Compatibility', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 3,
                'title': 'Transplanting & Optimum Hill Spacing',
                'hindi_title': 'धान रोपाई, पौधे प्रति हिल व कतार दूरी',
                'timeline': 'Day 25 – Day 30',
                'phase': 'Transplanting',
                'image': 'images/cultivation/rice-transplant.jpg',
                'image_caption': 'Transplanting 2-3 sturdy green paddy saplings per hill in standing water at 20x15 cm grid',
                'metrics': [
                    {'label': 'Spacing', 'value': '20 cm × 15 cm Grid', 'icon': 'bi-rulers'},
                    {'label': 'Hill Density', 'value': '33 Hills / sq. meter', 'icon': 'bi-grid-3x3'},
                    {'label': 'Seedlings/Hill', 'value': '2 – 3 Seedlings per Hill', 'icon': 'bi-tree'},
                    {'label': 'Depth', 'value': '2 – 3 cm Shallow Planting', 'icon': 'bi-arrow-down-circle'},
                ],
                'actions': [
                    'Uproot 21–25 day old nursery seedlings gently after flooding nursery beds to prevent root tip tearing.',
                    'Transplant at shallow depth (2–3 cm). Deep planting (>4 cm) retards tillering and delays maturity by 10–14 days.',
                    'Maintain 2–3 seedlings per hill at 20x15 cm spacing (33 hills/sq.m). For hybrids, plant 1–2 seedlings per hill.',
                    'Within 2–3 days of transplanting, apply pre-emergence herbicide Pretilachlor 50 EC @ 600 ml/acre in 2–3 cm standing water to prevent weed emergence.',
                ],
                'pro_tip': 'Maintain 2 cm standing water for the first 7 days after transplanting to facilitate quick root establishment and prevent weed germination.',
                'tool_shortcut': {'name': 'Evaluate Field Decision Margin', 'url': '/crops/yield/'},
            },
            {
                'step_number': 4,
                'title': 'Alternate Wetting & Drying (AWD) & Split Top-Dressing',
                'hindi_title': 'बारी-बारी सूखा-गीला (AWD) सिंचाई व यूरिया खुराक',
                'timeline': 'Day 35 – Day 85',
                'phase': 'Vegetative Care',
                'image': 'images/cultivation/universal-irrigation.jpg',
                'image_caption': 'Alternate wetting and drying field tube monitoring water table to reduce water use and prevent methane emission',
                'metrics': [
                    {'label': 'AWD Saving', 'value': '30% Water Saved, Zero Yield Loss', 'icon': 'bi-droplet-half'},
                    {'label': 'Split 1 (21d)', 'value': '35 kg Neem Urea at Active Tillering', 'icon': 'bi-capsule'},
                    {'label': 'Split 2 (45d)', 'value': '35 kg Neem Urea at Panicle Initiation', 'icon': 'bi-capsule'},
                    {'label': 'Critical Water', 'value': 'Flowering & Milking Stages', 'icon': 'bi-water'},
                ],
                'actions': [
                    'Adopt Alternate Wetting and Drying (AWD): re-irrigate only when standing water disappears and hairline cracks appear on soil surface.',
                    'Apply 1st top dressing of Nitrogen (35 kg Neem Urea) at active tillering (21–25 days after transplanting).',
                    'Apply 2nd top dressing of Nitrogen (35 kg Neem Urea) at panicle initiation stage (45–50 days). Complete all urea before flag leaf stage.',
                    'Crucial rule: Maintain 5 cm standing water continuously during flowering and milk stages; moisture stress now results in chaffy unfilled grains.',
                ],
                'pro_tip': 'AWD aeration increases root oxygenation, strengthens root depth, prevents iron toxicity, and reduces greenhouse methane emissions by 40%.',
                'tool_shortcut': {'name': 'Check Real-Time Weather Forecast', 'url': '/weather/'},
            },
            {
                'step_number': 5,
                'title': 'Stem Borer, Leaf Folder & Blast Disease Defense',
                'hindi_title': 'तना छेदक, पत्ता लपेटक व ब्लास्ट (झोंका) रोग नियंत्रण',
                'timeline': 'Day 45 – Day 105',
                'phase': 'Crop Protection',
                'image': 'images/cultivation/universal-pest.jpg',
                'image_caption': 'Scouting for leaf folder rolls and stem borer dead hearts with pheromone traps in paddy',
                'metrics': [
                    {'label': 'Key Pests', 'value': 'Yellow Stem Borer, BPH, Leaf Folder', 'icon': 'bi-bug'},
                    {'label': 'Key Diseases', 'value': 'Neck Blast, Sheath Blight, BLB', 'icon': 'bi-virus'},
                    {'label': 'BPH Trap', 'value': 'Alleyway gaps every 2 meters', 'icon': 'bi-compass'},
                    {'label': 'Biocontrol', 'value': 'Trichogramma egg cards @ 2/acre', 'icon': 'bi-shield-check'},
                ],
                'actions': [
                    'Install Scirpophaga incertulas pheromone traps (8/acre) to monitor yellow stem borer adult moth flight activity.',
                    'For Yellow Stem Borer & Leaf Folder: Apply Chlorantraniliprole 0.4% GR (Ferterra) @ 4 kg/acre or Cartap Hydrochloride 4G @ 7.5 kg/acre in standing water.',
                    'For Brown Planthopper (BPH / Mahla): Inspect lower stem base near water level. If population > 10–15 hoppers/hill, spray Pymetrozine 50 WDG @ 120 g/acre directly at stem base.',
                    'For Neck Blast & Sheath Blight: Spray Tricyclazole 75% WP @ 120 g/acre or Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 200 ml/acre at 5% panicle emergence.',
                ],
                'pro_tip': 'Leave 30 cm alleyways (pathways) every 2 meters during transplanting to allow sunlight and airflow, which naturally deters Brown Planthopper build-up.',
                'tool_shortcut': {'name': 'Scan Leaf for Blast or Sheath Blight', 'url': '/disease/'},
            },
            {
                'step_number': 6,
                'title': 'Harvesting at 80% Golden Grain & Threshing',
                'hindi_title': 'कंबाइन हार्वेस्टर कटाई, गहाई व ओसाई (80-85% सुनहरी बाली)',
                'timeline': 'Day 120 – Day 140',
                'phase': 'Harvesting',
                'image': 'images/cultivation/universal-harvest.jpg',
                'image_caption': 'Combine harvester threshing ripe golden paddy field and transferring clean grain to trailer',
                'metrics': [
                    {'label': 'Harvest Stage', 'value': '80–85% Grains Turn Golden Yellow', 'icon': 'bi-check2-circle'},
                    {'label': 'Field Drainage', 'value': 'Drain Water 10 Days Before Cutting', 'icon': 'bi-water'},
                    {'label': 'Moisture at Harvest', 'value': '20% – 22% Moisture', 'icon': 'bi-moisture'},
                    {'label': 'Average Yield', 'value': '24 – 32 Quintals / Acre', 'icon': 'bi-trophy'},
                ],
                'actions': [
                    'Drain standing water completely from the field 10–12 days prior to expected harvest to allow soil drying and facilitate machine movement.',
                    'Harvest when upper 80–85% grains in panicles turn straw golden while lower few grains are still in hard dough stage.',
                    'Thresh immediately using mechanical threshers or combine harvesters to avoid lodging and field shattering losses from late rainfall.',
                    'Collect clean golden paddy free from straw and stone contaminants. Retain paddy straw for livestock dry fodder or mushroom compost.',
                ],
                'pro_tip': 'Never let paddy over-dry on standing stalks below 16% moisture in the field; over-dry grain develops internal cracks that shatter into broken rice during milling.',
                'tool_shortcut': {'name': 'Track Harvest Forecast & Rain', 'url': '/weather/'},
            },
            {
                'step_number': 7,
                'title': 'Sun-Drying to 14% Moisture & APMC Mandi MSP Procurement',
                'hindi_title': 'धूप में सुखाना (14% नमी), बोरी पैकिंग व सरकारी धान खरीद',
                'timeline': 'October – December (Kharif Marketing Season)',
                'phase': 'Commercial & Selling',
                'image': 'images/cultivation/universal-mandi.jpg',
                'image_caption': 'Inspected paddy sacks stacked at FCI procurement center after electronic moisture testing',
                'metrics': [
                    {'label': 'Safe Moisture', 'value': 'Strictly <= 14% for MSP', 'icon': 'bi-moisture'},
                    {'label': 'Govt MSP', 'value': 'Official Common / Grade-A Rate', 'icon': 'bi-award'},
                    {'label': 'Bag Weight', 'value': 'Standard 37.5 / 50 kg Sacks', 'icon': 'bi-bag'},
                    {'label': 'DBT Payment', 'value': 'Direct to Bank in 48-72 Hours', 'icon': 'bi-credit-card'},
                ],
                'actions': [
                    'Sun-dry harvested paddy on clean cement threshed floor or tarpaulin for 2–3 sunny days until moisture drops to 13–14%.',
                    'Check moisture using a digital moisture meter. Government procurement centers reject paddy above 17% moisture or levy severe deductions.',
                    'Clean grain by winnowing (fan) to keep refractions (dust, stones, empty husks) below 1% to meet FCI Fair Average Quality (FAQ) standards.',
                    'Deliver paddy to designated APMC Mandi / PACS procurement center after generating the gate pass through the state farmer portal.',
                    'For Basmati varieties (1121, 1509, 1718): Compare private miller quotes across major basmati mandis (Karnal, Amritsar, Narela) before selling.',
                ],
                'pro_tip': 'Selling Basmati rice directly to certified export millers with clean pesticide-residue certificates fetches a premium of ₹300–₹500 per quintal.',
                'tool_shortcut': {'name': 'Check Live Paddy & Basmati Prices', 'url': '/market/'},
            },
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4. COTTON GUIDE
# ─────────────────────────────────────────────────────────────────────────────
def _cotton_guide(crop_data):
    return {
        'crop_name': 'Cotton',
        'hindi_name': 'कपास (सफेद सोना) की उन्नत खेती, चुगाई व मंडी बिक्री',
        'botanical_name': 'Gossypium hirsutum',
        'total_duration': '150 – 175 Days',
        'ideal_season': 'Kharif (May–June Sowing)',
        'expected_yield': '10 – 14 Quintals / Acre (Kapas)',
        'market_channel': 'Cotton Corporation of India (CCI) at MSP, APMC Ginning Mills',
        'stages': [
            {
                'step_number': 1,
                'title': 'Bt Hybrid Selection, Seed Dibbling & Spacing',
                'hindi_title': 'बीज चयन, डिबलिंग बुवाई व कतार दूरी',
                'timeline': 'May 15 – June 15',
                'phase': 'Seed & Sowing',
                'image': 'images/cultivation/cotton-sowing.jpg',
                'image_caption': 'Young cotton seedlings emerging in uniformly spaced ridge-and-furrow rows',
                'metrics': [
                    {'label': 'Seed Rate', 'value': '1.5 – 2.0 kg / Acre (Bt Hybrids)', 'icon': 'bi-box-seam'},
                    {'label': 'Top Hybrids', 'value': 'RCH-659, Ajeet-155, Jaadoo', 'icon': 'bi-stars'},
                    {'label': 'Spacing', 'value': '90 cm × 60 cm (or 120 × 45 cm)', 'icon': 'bi-rulers'},
                    {'label': 'Sowing Depth', 'value': '3 – 4 cm in Moist Soil', 'icon': 'bi-arrow-down-circle'},
                ],
                'actions': [
                    'Select BG-II Bt cotton hybrids approved by the Central Variety Release Committee for your state agro-climatic zone.',
                    'Dibble 1–2 seeds per hill at 3–4 cm depth on the side of ridges formed 90 cm apart.',
                    'Pre-irrigate furrows before dibbling so seeds germinate vigorously within 4–6 days.',
                    'Thin excess seedlings at 15–18 days to retain 1 healthy, vigorous plant per hill (density ~7,400 plants/acre).',
                ],
                'pro_tip': 'Sow non-Bt refuge seeds in 5 boundary border rows around the field to delay pest resistance against Bt toxins.',
                'tool_shortcut': {'name': 'Calculate Cotton Nutrients', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 2,
                'title': 'Ridge & Furrow Irrigation, Weeding & Split Nitrogen',
                'hindi_title': 'मेड़-नाली सिंचाई, निराई-गुड़ाई व यूरिया टॉप ड्रेसिंग',
                'timeline': 'Day 20 – Day 70',
                'phase': 'Vegetative Care',
                'image': 'images/cultivation/cotton-flowering.jpg',
                'image_caption': 'Vigorous cotton plants at square formation stage with dense green foliage and healthy branches',
                'metrics': [
                    {'label': 'Drip Laterals', 'value': 'Alternate Row Drip Laterals', 'icon': 'bi-droplet'},
                    {'label': 'Weed Window', 'value': 'Critical First 45 Days', 'icon': 'bi-clock'},
                    {'label': 'Urea Splits', 'value': '3 Equal Splits (30, 60, 90 Days)', 'icon': 'bi-capsule'},
                    {'label': 'Earthing Up', 'value': 'At 45 Days along Plant Base', 'icon': 'bi-triangle'},
                ],
                'actions': [
                    'Keep the crop weed-free for the first 60 days using tractor inter-cultivator or hand weeding.',
                    'Apply 1st split of Urea (35 kg/acre) at square formation (35–40 days) followed by earthing-up soil around plant stems.',
                    'Apply 2nd split of Urea (35 kg/acre) along with MOP (20 kg/acre) at peak flowering (60–65 days).',
                    'Drip irrigation: Run drip every 3–4 days; avoid water stress during square formation which leads to massive flower shedding.',
                ],
                'pro_tip': 'Spray Planofix (NAA 4.5 SL) @ 4 ml in 15 L water at peak flowering to arrest hormonal flower and square drop by 30%.',
                'tool_shortcut': {'name': 'Weather & Evaporation Forecast', 'url': '/weather/'},
            },
            {
                'step_number': 3,
                'title': 'Pink Bollworm & Sucking Pest Integrated Management',
                'hindi_title': 'गुलाबी सुंडी (PBW) व रस चूसक कीटों की रोकथाम',
                'timeline': 'Day 60 – Day 130',
                'phase': 'Crop Protection',
                'image': 'images/cultivation/universal-pest.jpg',
                'image_caption': 'Pheromone traps installed at canopy height for pink bollworm moth surveillance',
                'metrics': [
                    {'label': 'Pheromone Traps', 'value': '8 Pectino-Lure Traps / Acre', 'icon': 'bi-radar'},
                    {'label': 'ETL for PBW', 'value': '8 Moths/Trap/Day for 3 Days', 'icon': 'bi-exclamation-triangle'},
                    {'label': 'Whitefly & Thrips', 'value': 'Yellow & Blue Sticky Sheets', 'icon': 'bi-shield-check'},
                    {'label': 'Key Spray', 'value': 'Chlorpyrifos or Emamectin Benzoate', 'icon': 'bi-spray'},
                ],
                'actions': [
                    'Install 8 Pheromone traps per acre with Pectinophora gossypiella lures at 45 days after sowing and replace lures every 3 weeks.',
                    'Deploy 20 yellow sticky traps per acre to capture whiteflies and curb Cotton Leaf Curl Virus (CLCuV).',
                    'Sample 20 green bolls randomly across field weekly; if more than 2 bolls show entry holes, initiate chemical intervention.',
                    'For PBW control: Spray Profenofos 50 EC @ 2 ml/L or Emamectin Benzoate 5% SG @ 0.5 g/L in the evening.',
                ],
                'pro_tip': 'Never extend the cotton crop into late ratoon flushes; terminating by December breaks the pink bollworm hibernation cycle.',
                'tool_shortcut': {'name': 'Scan Leaf for Pest Damage', 'url': '/disease/'},
            },
            {
                'step_number': 4,
                'title': 'Manual Picking of Clean Fluffy White Bolls',
                'hindi_title': 'साफ कपास की चुगाई (ओस सूखने के बाद)',
                'timeline': 'Day 120 – Day 170 (Multiple Pickings)',
                'phase': 'Harvesting',
                'image': 'images/cultivation/cotton-picking.jpg',
                'image_caption': 'Manual picking of clean, spotless white cotton bolls into clean cotton bags under bright sun',
                'metrics': [
                    {'label': 'Picking Time', 'value': 'After 10 AM (Dew Evaporated)', 'icon': 'bi-sun'},
                    {'label': 'Pickings', 'value': '3 – 4 Pickings at 15-Day Intervals', 'icon': 'bi-repeat'},
                    {'label': 'Collection Bag', 'value': '100% Cotton Cloth Bags', 'icon': 'bi-bag'},
                    {'label': 'Moisture Level', 'value': 'Dry < 8% Moisture', 'icon': 'bi-moisture'},
                ],
                'actions': [
                    'Start picking strictly after morning dew has completely evaporated (after 10:00 AM) to keep fiber dry and unstained.',
                    'Pick only fully burst, fluffy white bolls; do not pick unopened, stained, or insect-damaged bolls with good lot.',
                    'Use 100% cotton cloth collection bags tied around waist. STRICTLY BAN plastic or poly-feed bags which contaminate lint with synthetic threads.',
                    'Keep first 2 pickings (which contain superior staple length and micronaire value) separate from late-season pickings.',
                ],
                'pro_tip': 'Ginning mills pay ₹200–₹400/quintal higher for contamination-free cotton with low trash content (<3%).',
                'tool_shortcut': {'name': 'Field Yield Evaluation', 'url': '/crops/yield/'},
            },
            {
                'step_number': 5,
                'title': 'Drying, Grading & APMC Mandi / CCI Procurement',
                'hindi_title': 'सुखाना, ग्रेडिंग व भारतीय कपास निगम (CCI) मंडी बिक्री',
                'timeline': 'November – February',
                'phase': 'Commercial & Selling',
                'image': 'images/cultivation/universal-mandi.jpg',
                'image_caption': 'Graded seed cotton (kapas) unloaded at APMC ginning market for auction and pressing into bales',
                'metrics': [
                    {'label': 'CCI MSP', 'value': 'Official Long / Medium Staple MSP', 'icon': 'bi-award'},
                    {'label': 'Permissible Moisture', 'value': '8% – 12% Moisture Content', 'icon': 'bi-moisture'},
                    {'label': 'Major Mandis', 'value': 'Rajkot, Warangal, Adilabad, Sirsa', 'icon': 'bi-geo-alt'},
                    {'label': 'Net Profit/Acre', 'value': '₹45,000 – ₹70,000 / Acre', 'icon': 'bi-cash-coin'},
                ],
                'actions': [
                    'Sun-dry seed cotton (kapas) on clean tarpaulins for 1–2 days to bring moisture below 8–10%.',
                    'Remove leaf bracts, dry leaves, and yellow stained locks manually before loading.',
                    'Check whether the Cotton Corporation of India (CCI) procurement center is operational in your nearest APMC mandi.',
                    'Transport in clean covered trailers to prevent moisture pickup or road dust contamination.',
                    'Participate in open auction at APMC or sell directly to CCI if private trade offers below the Government MSP.',
                ],
                'pro_tip': 'Moisture above 12% attracts heavy price penalties at CCI procurement; sun-drying for 4 hours saves up to ₹300 per quintal.',
                'tool_shortcut': {'name': 'Track Live Cotton Mandi Prices', 'url': '/market/'},
            },
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. POTATO GUIDE
# ─────────────────────────────────────────────────────────────────────────────
def _potato_guide(crop_data):
    return {
        'crop_name': 'Potato',
        'hindi_name': 'आलू की उन्नत खेती, कंद विकास व शीतगृह/मंडी विपणन',
        'botanical_name': 'Solanum tuberosum',
        'total_duration': '90 – 110 Days',
        'ideal_season': 'Rabi (October 15 – November 10)',
        'expected_yield': '120 – 160 Quintals / Acre (12–16 Tonnes)',
        'market_channel': 'Cold Storage (Aloo Mandi), Chips Processors (Lays/Balaji), APMC',
        'stages': [
            {
                'step_number': 1,
                'title': 'Certified Seed Tuber Sprouting & Fungicidal Treatment',
                'hindi_title': 'प्रमाणित बीज आलू का चयन, अंकुरण व उपचार',
                'timeline': 'October 1 – October 25',
                'phase': 'Seed & Sowing',
                'image': 'images/cultivation/potato-sowing.jpg',
                'image_caption': 'Healthy seed tubers with sturdy sprouts emerging under diffused daylight in chitting trays',
                'metrics': [
                    {'label': 'Seed Tuber Rate', 'value': '12 – 15 Quintals / Acre', 'icon': 'bi-box-seam'},
                    {'label': 'Tuber Size', 'value': '40 – 50 g (Golf Ball Size)', 'icon': 'bi-circle'},
                    {'label': 'Top Varieties', 'value': 'Kufri Jyoti, Pukhraj, Chipsona', 'icon': 'bi-stars'},
                    {'label': 'Chitting Period', 'value': '10 – 14 Days in Diffused Light', 'icon': 'bi-sun'},
                ],
                'actions': [
                    'Procure disease-free seed tubers from certified cold stores or government seed centers (CPRI varieties).',
                    'Remove seed tubers from cold storage 10–14 days before planting; spread them in thin layers under shade to sprout sturdy green eyes (chitting).',
                    'Treat tubers with Mancozeb 75 WP @ 2.5 g/L or Trichoderma viride @ 5 g/L for 10 minutes to prevent black scurf and seed decay.',
                    'Plant whole tubers wherever possible. If cutting large tubers, ensure at least 2–3 viable eyes per piece and allow cut surfaces to suberize for 24 hours.',
                ],
                'pro_tip': 'Chipsona-1, Chipsona-3, and Lady Rosetta varieties command ₹200/quintal premium from wafer and chips processing companies.',
                'tool_shortcut': {'name': 'Calculate Potato Fertilizers', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 2,
                'title': 'Ridge & Furrow Planting with Basal NPK',
                'hindi_title': 'मेड़-कूड़ बुवाई व बेसल खाद प्रबंधन',
                'timeline': 'Day 0 – Day 5',
                'phase': 'Land Preparation',
                'image': 'images/cultivation/potato-sowing.jpg',
                'image_caption': 'Tractor potato planter placing seed tubers at 20 cm spacing and covering with uniform soil ridges',
                'metrics': [
                    {'label': 'Ridge Spacing', 'value': '60 cm Row-to-Row', 'icon': 'bi-rulers'},
                    {'label': 'Tuber Spacing', 'value': '20 cm Plant-to-Plant', 'icon': 'bi-arrows-expand'},
                    {'label': 'Depth', 'value': '7 – 8 cm Depth in Ridge', 'icon': 'bi-arrow-down-circle'},
                    {'label': 'DAP + MOP', 'value': '100 kg DAP + 60 kg MOP / Acre', 'icon': 'bi-box'},
                ],
                'actions': [
                    'Plough land thoroughly to a depth of 20–25 cm to create a loose, friable, clod-free seedbed essential for tuber expansion.',
                    'Apply 10 tonnes of decomposed FYM per acre 3 weeks before planting.',
                    'Apply full doses of Phosphorus (100 kg DAP), Potassium (60 kg MOP), and 1/3rd Nitrogen (35 kg Urea) in furrows before planting.',
                    'Place sprouted tubers at 20 cm spacing with eyes facing upward and immediately form 15–20 cm high ridges over them.',
                ],
                'pro_tip': 'Avoid heavy, compacted clay soils; loose, aerated sandy loam soil produces smooth, blemish-free tubers with no deformities.',
                'tool_shortcut': {'name': 'Check Soil Reaction & pH', 'url': '/crops/'},
            },
            {
                'step_number': 3,
                'title': 'Earthing Up & Tuber Bulking Irrigation',
                'hindi_title': 'मिट्टी चढ़ाना (Earthing-up) व कंद फुलाव सिंचाई',
                'timeline': 'Day 25 – Day 60',
                'phase': 'Vegetative Care',
                'image': 'images/cultivation/universal-irrigation.jpg',
                'image_caption': 'High earth ridges completely shielding growing potato tubers from sunlight to avoid greening',
                'metrics': [
                    {'label': 'Earthing Up', 'value': 'At 25 – 30 Days (15 cm plant height)', 'icon': 'bi-triangle'},
                    {'label': 'Urea Top-Dress', 'value': '45 kg Urea during Earthing-up', 'icon': 'bi-capsule'},
                    {'label': 'Irrigation Level', 'value': '2/3rd Furrow Height (Never Over-Top)', 'icon': 'bi-water'},
                    {'label': 'Frequency', 'value': 'Every 8 – 10 Days', 'icon': 'bi-calendar3'},
                ],
                'actions': [
                    'Perform earthing-up when plants reach 15–20 cm height. Pull soil up to create broad, high ridges that completely bury developing stolons.',
                    'Top-dress remaining Nitrogen (45 kg Urea/acre) and incorporate into ridges during earthing-up.',
                    'Irrigate carefully through furrows up to 2/3rd of ridge height; NEVER submerge ridge tops, as standing water over ridges rots tubers.',
                    'Maintain consistent soil moisture during tuber initiation (30–45 days) and bulking (50–75 days) to avoid knobby, cracked tubers.',
                ],
                'pro_tip': 'Exposing tubers to sunlight turns them green with toxic solanine; thorough earthing-up completely eliminates greening losses.',
                'tool_shortcut': {'name': 'Weather & Frost Alerts', 'url': '/weather/'},
            },
            {
                'step_number': 4,
                'title': 'Late Blight Prevention & De-Haulming (Vine Cutting)',
                'hindi_title': 'पछेती झुलसा (Late Blight) रोकथाम व बेल कटाई (डी-हॉमिंग)',
                'timeline': 'Day 60 – Day 95',
                'phase': 'Protection & Maturation',
                'image': 'images/cultivation/universal-pest.jpg',
                'image_caption': 'Inspecting underside of potato leaves for water-soaked late blight lesions during foggy mornings',
                'metrics': [
                    {'label': 'Major Disease', 'value': 'Late Blight (Phytophthora)', 'icon': 'bi-virus'},
                    {'label': 'Preventive Spray', 'value': 'Mancozeb 75 WP (2.5 g/L)', 'icon': 'bi-shield-check'},
                    {'label': 'Curative Spray', 'value': 'Cymoxanil + Mancozeb (2 g/L)', 'icon': 'bi-capsule'},
                    {'label': 'De-Haulming', 'value': 'Cut Vines 10–12 Days Before Digging', 'icon': 'bi-scissors'},
                ],
                'actions': [
                    'During cold, foggy, humid weather (temp 10–20°C, humidity >80%), spray Mancozeb 75 WP @ 2.5 g/L preventively every 10 days.',
                    'If late blight lesions appear: immediately spray Cymoxanil 8% + Mancozeb 64% WP (Curzate) @ 2 g/L or Dimethomorph @ 1 g/L.',
                    'Stop all irrigation 12–15 days before harvest to allow tuber skins to firm up.',
                    'De-Haulming: Cut the green vines at ground level 10–12 days before harvest. This hardens tuber skin, stops blight spores reaching tubers, and prevents skin peeling during harvest.',
                ],
                'pro_tip': 'De-haulming is mandatory for cold storage potatoes; hardened skins prevent 90% of storage rotting and weight-loss shrink.',
                'tool_shortcut': {'name': 'Scan Leaf for Late Blight', 'url': '/disease/'},
            },
            {
                'step_number': 5,
                'title': 'Mechanical Potato Digging, Curing & Cold Storage Selling',
                'hindi_title': 'आलू खुदाई, क्योरिंग व शीतगृह (Cold Storage) / मंडी विपणन',
                'timeline': 'Day 95 – Day 110 (Harvest & Sales)',
                'phase': 'Harvesting & Selling',
                'image': 'images/cultivation/potato-harvest.jpg',
                'image_caption': 'Tractor potato digger lifting smooth, firm tubers onto dry soil surface for sorting into mesh bags',
                'metrics': [
                    {'label': 'Digging Time', 'value': 'Dry Soil Days (Bright Sun)', 'icon': 'bi-sun'},
                    {'label': 'Curing Period', 'value': '10 – 14 Days under Shade at Farm', 'icon': 'bi-shield'},
                    {'label': 'Cold Storage', 'value': '2 – 4 °C at 90–95% RH', 'icon': 'bi-snow'},
                    {'label': 'Standard Pack', 'value': '50 kg Breathable Red Mesh Bags', 'icon': 'bi-bag'},
                ],
                'actions': [
                    'Operate tractor-drawn potato digger on sunny days when soil has dried enough to separate cleanly from tubers without clod bruising.',
                    'Collect tubers and spread in 1-meter high heaps under a shaded, ventilated shed for 10–12 days for "curing" (healing small cuts and thickening skin).',
                    'Grade into Seed Size (30–45 mm), Table Medium (45–65 mm), Table Large (>65 mm), and reject cut or rotten tubers.',
                    'Pack in 50 kg red leno mesh bags; never use airtight plastic bags.',
                    'Market Strategy: Sell 30–40% fresh harvest at peak local prices in February; store remaining 60% in licensed cold storage for sale during high-price months (July–October).',
                ],
                'pro_tip': 'Cold-stored potatoes must be kept for 3–5 days at room temperature before dispatch to re-convert accumulated sugars back to starch.',
                'tool_shortcut': {'name': 'Track Live Potato Mandi Prices', 'url': '/market/'},
            },
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. ONION GUIDE
# ─────────────────────────────────────────────────────────────────────────────
def _onion_guide(crop_data):
    return {
        'crop_name': 'Onion',
        'hindi_name': 'प्याज की वैज्ञानिक खेती, कंद सुखाना व नासिक/मंडी विपणन',
        'botanical_name': 'Allium cepa',
        'total_duration': '120 – 140 Days',
        'ideal_season': 'Rabi (Nov Nursery, Jan Transplant) & Kharif (Jul Nursery)',
        'expected_yield': '100 – 140 Quintals / Acre (10–14 Tonnes)',
        'market_channel': 'APMC Onion Mandis (Lasalgaon, Pimpalgaon), NAFED Buffer Stock',
        'stages': [
            {
                'step_number': 1,
                'title': 'Raised Bed Nursery Raising & Seed Treatment',
                'hindi_title': 'उठी हुई क्यारियों पर नर्सरी व बीजोपचार',
                'timeline': 'Day 0 – Day 45',
                'phase': 'Nursery Phase',
                'image': 'images/cultivation/onion-sowing.jpg',
                'image_caption': 'Lush, thin needle-like onion seedlings thriving on raised nursery beds with micro-sprinklers',
                'metrics': [
                    {'label': 'Seed Rate', 'value': '4 – 5 kg / Acre', 'icon': 'bi-box-seam'},
                    {'label': 'Top Varieties', 'value': 'Bhima Super, N-53, Agrifound Dark Red', 'icon': 'bi-stars'},
                    {'label': 'Nursery Bed', 'value': 'Raised Beds (15 cm High, 1.2 m Wide)', 'icon': 'bi-layers'},
                    {'label': 'Seedling Age', 'value': '45 – 50 Days (Pencil Thick)', 'icon': 'bi-calendar-check'},
                ],
                'actions': [
                    'Select true-to-type certified seeds: Bhima Super/N-53 for Kharif, Agrifound Dark Red/Bhima Kiran for Rabi.',
                    'Treat seeds with Thiram or Captan @ 2.5 g/kg seed + Trichoderma viride @ 5 g/kg to eliminate damping-off.',
                    'Sow seeds in shallow lines 5–7 cm apart on raised nursery beds; cover lightly with sieved FYM and paddy straw mulch.',
                    'Irrigate daily with a fine-rose cane. Remove straw mulch as soon as needle-like green sprouts emerge (4–5 days).',
                ],
                'pro_tip': 'Trim top 1/3rd of seedling foliage at transplanting time to reduce transpiration water loss and accelerate root anchorage.',
                'tool_shortcut': {'name': 'Calculate Onion Fertilizer Doses', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 2,
                'title': 'Flat Bed Transplanting & Close Spacing',
                'hindi_title': 'सपाट क्यारियों में सघन रोपाई (15x10 सेमी)',
                'timeline': 'Day 45 – Day 55',
                'phase': 'Transplanting',
                'image': 'images/cultivation/universal-transplant.jpg',
                'image_caption': 'Transplanting pencil-thick onion seedlings at dense 15x10 cm grid in pre-irrigated flat beds',
                'metrics': [
                    {'label': 'Spacing', 'value': '15 cm × 10 cm Grid', 'icon': 'bi-rulers'},
                    {'label': 'Plant Population', 'value': '2,60,000 – 2,80,000 Plants/Acre', 'icon': 'bi-grid-3x3'},
                    {'label': 'Transplant Depth', 'value': '2 – 3 cm Shallow', 'icon': 'bi-arrow-down-circle'},
                    {'label': 'Basal Fertilizer', 'value': '50 kg DAP + 40 kg MOP + 15 kg Sulphur', 'icon': 'bi-box'},
                ],
                'actions': [
                    'Prepare flat beds (3m x 2m) or broad bed furrows (BBF) with micro-sprinklers/drip.',
                    'Apply 50 kg DAP + 40 kg MOP + 15 kg elemental Sulphur (90% WDG) per acre before final harrowing.',
                    'Transplant pencil-thick seedlings (45–50 days old) at shallow depth (2–3 cm). Deep transplanting produces elongated necked bulbs with low storage life.',
                    'Apply pre-emergence herbicide Oxyfluorfen 23.5% EC (Goal) @ 150 ml/acre within 72 hours of transplanting to prevent weed competition.',
                ],
                'pro_tip': 'Sulphur application (15 kg/acre) is essential for onion: it increases pungency (allyl propyl disulphide), bulb firmness, and market shelf-life by 60 days.',
                'tool_shortcut': {'name': 'Check Fertilizer Recommendations', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 3,
                'title': 'Bulb Enlargement, Thrips Defense & Purple Blotch',
                'hindi_title': 'कंद फुलाव, थ्रिप्स कीट व बैंगनी धब्बा (पर्पल ब्लॉच) नियंत्रण',
                'timeline': 'Day 60 – Day 105',
                'phase': 'Vegetative Care & Protection',
                'image': 'images/cultivation/universal-pest.jpg',
                'image_caption': 'Blue sticky sheets deployed in onion field to capture destructive Thrips tabaci insects',
                'metrics': [
                    {'label': 'Major Pest', 'value': 'Onion Thrips (Thrips tabaci)', 'icon': 'bi-bug'},
                    {'label': 'Major Disease', 'value': 'Purple Blotch (Alternaria porri)', 'icon': 'bi-virus'},
                    {'label': 'Blue Sticky Traps', 'value': '20 – 25 Traps / Acre', 'icon': 'bi-shield-check'},
                    {'label': 'Top Dressing', 'value': 'Urea 35 kg at 30d & 45d (Stop at 60d)', 'icon': 'bi-capsule'},
                ],
                'actions': [
                    'Top-dress Nitrogen in 2 equal splits (35 kg Urea at 30 days and 35 kg Urea at 45 days). NEVER apply nitrogen after 60 days, as late urea causes thick necks and rotting in storage.',
                    'Scout leaf axils for tiny yellow-brown thrips causing silvery white patches on leaves. If count > 15 thrips/plant, spray Fipronil 5% SC @ 2 ml/L or Spinetoram 11.7 SC @ 0.8 ml/L.',
                    'For Purple Blotch: Spray Tebuconazole 25.9% EC (Folicur) @ 1.5 ml/L or Mancozeb 75 WP @ 2.5 g/L with a sticking agent (spreader).',
                    'Maintain light, frequent irrigations during bulb enlargement. Water stress followed by heavy flooding causes split/double bulbs.',
                ],
                'pro_tip': 'Stop all irrigation 12–15 days before harvesting when tops begin to fall over; this cures the neck and prevents bacterial soft rot in storage.',
                'tool_shortcut': {'name': 'Scan Leaf for Purple Blotch', 'url': '/disease/'},
            },
            {
                'step_number': 4,
                'title': 'Neck-Fall Stage Harvesting & Field Curing',
                'hindi_title': 'गर्दन गिरने (50% नेक-फॉल) पर कटाई व खेत में क्योरिंग',
                'timeline': 'Day 115 – Day 130',
                'phase': 'Harvesting',
                'image': 'images/cultivation/universal-harvest.jpg',
                'image_caption': 'Mature onions harvested after natural neck fall, left in field windrows with foliage covering bulbs',
                'metrics': [
                    {'label': 'Harvest Trigger', 'value': '50% – 60% Top Neck Fall', 'icon': 'bi-check2-circle'},
                    {'label': 'Windrow Curing', 'value': '3 – 4 Days in Field Windrows', 'icon': 'bi-sun'},
                    {'label': 'Shade Curing', 'value': '10 – 12 Days in Aerated Shed', 'icon': 'bi-shield'},
                    {'label': 'Neck Cutting', 'value': 'Leave 2.5 cm Neck Attached', 'icon': 'bi-scissors'},
                ],
                'actions': [
                    'Harvest when 50–60% of the plant foliage naturally lodges and falls over (neck-fall stage). Harvesting earlier produces immature, soft bulbs.',
                    'Pull bulbs out carefully on dry sunny days. Arrange them in windrows where the leaves of one row cover the bulbs of the next row to prevent sun-scald.',
                    'Field cure for 3–4 days, then shift to a well-ventilated dry shed for 10–12 days of shade curing until the neck becomes completely papery thin and dry.',
                    'Trim dried roots cleanly and cut tops leaving a 2.5–3.0 cm neck stump attached to the bulb; cutting too close to the bulb allows fungal entrance.',
                ],
                'pro_tip': 'Never skip the 12-day shade curing: it develops deep red-bronze outer skin layers that protect bulbs during 6 months of storage.',
                'tool_shortcut': {'name': 'Harvest Weather & Sunshine Forecast', 'url': '/weather/'},
            },
            {
                'step_number': 5,
                'title': 'Grading, Leno Bag Packing & APMC Mandi / NAFED Selling',
                'hindi_title': 'ग्रेडिंग, लाल जालीदार बोरी पैकिंग व नासिक/मंडी नीलामी',
                'timeline': 'Post-Harvest Marketing Window',
                'phase': 'Commercial & Selling',
                'image': 'images/cultivation/universal-mandi.jpg',
                'image_caption': 'Bags of graded red onions stacked at Lasalgaon APMC wholesale auction yard',
                'metrics': [
                    {'label': 'Grade A (Big)', 'value': '55 – 75 mm Diameter, Firm Red', 'icon': 'bi-award'},
                    {'label': 'Grade B (Medium)', 'value': '45 – 55 mm Diameter', 'icon': 'bi-circle'},
                    {'label': 'Packing', 'value': '40 – 50 kg Red Leno Mesh Bags', 'icon': 'bi-bag'},
                    {'label': 'Top Mandis', 'value': 'Lasalgaon, Pimpalgaon, Yeola, Hubli', 'icon': 'bi-geo-alt'},
                ],
                'actions': [
                    'Grade into Grade A (55–75 mm for premium retail), Grade B (45–55 mm for local mandis), and Golta/Golti (<40 mm for export/pickles).',
                    'Discard thick-necked, bolted (flowered), double, or diseased bulbs.',
                    'Pack in 40–50 kg red open-mesh leno bags that ensure 360-degree ventilation and prevent heat build-up during transport.',
                    'For Storage: Store in traditional ventilated bamboo/mesh structures (Kanda Chawl) raised 60 cm above ground with bottom and side aeration.',
                    'Monitor price trends on the KrishiMitra Market tracker. Sell to APMC commission agents or participate in Government buffer procurement (NAFED / NCCF).',
                ],
                'pro_tip': 'NAFED/NCCF buffer stock procurement purchases FAQ quality onions directly at designated centers with zero mandi tax deductions.',
                'tool_shortcut': {'name': 'Track Live Onion Mandi Prices', 'url': '/market/'},
            },
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 7. MAIZE GUIDE
# ─────────────────────────────────────────────────────────────────────────────
def _maize_guide(crop_data):
    return {
        'crop_name': 'Maize (Corn)',
        'hindi_name': 'मक्का की संकर खेती, भुट्टा तुड़ाई व दाना मंडी विपणन',
        'botanical_name': 'Zea mays',
        'total_duration': '95 – 115 Days',
        'ideal_season': 'Kharif (June–July) & Rabi (Oct–Nov)',
        'expected_yield': '28 – 35 Quintals / Acre (Grain)',
        'market_channel': 'Poultry Feed Millers, Starch Industry, APMC Mandi at MSP',
        'stages': [
            {
                'step_number': 1,
                'title': 'Hybrid Seed Selection & Ridge Sowing',
                'hindi_title': 'संकर बीज चयन, बीजोपचार व मेड़ बुवाई',
                'timeline': 'Day 0 – Day 5',
                'phase': 'Seed & Sowing',
                'image': 'images/cultivation/universal-sowing.jpg',
                'image_caption': 'Single hybrid maize seed dibbled on the shoulder of ridges at 60x20 cm spacing',
                'metrics': [
                    {'label': 'Seed Rate', 'value': '7 – 8 kg / Acre (Hybrids)', 'icon': 'bi-box-seam'},
                    {'label': 'Top Hybrids', 'value': 'Pioneer 3396, Dekalb 9108, NK-6240', 'icon': 'bi-stars'},
                    {'label': 'Spacing', 'value': '60 cm × 20 cm', 'icon': 'bi-rulers'},
                    {'label': 'Seed Depth', 'value': '4 – 5 cm', 'icon': 'bi-arrow-down-circle'},
                ],
                'actions': [
                    'Select high-yielding single-cross hybrids adapted to your region (Pioneer, Syngenta, Bayer Dekalb, CP-818).',
                    'Treat seed with Thiram (2.5 g/kg) + Imidacloprid 600 FS (4 ml/kg) to protect against shoot fly and early seedling damping-off.',
                    'Dibble seeds on the shoulder of ridges spaced 60 cm apart, maintaining 20 cm distance between plants (density ~33,000 plants/acre).',
                    'Apply pre-emergence herbicide Atrazine 50% WP @ 500 g/acre within 48 hours of sowing in moist soil.',
                ],
                'pro_tip': 'Sowing on ridge shoulders ensures the seed zone does not suffer waterlogging during heavy monsoon cloudbursts.',
                'tool_shortcut': {'name': 'Calculate Maize NPK Fertilizer', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 2,
                'title': 'Fall Armyworm (FAW) Defense & Split Nitrogen',
                'hindi_title': 'फॉल आर्मीवर्म (सैनिक कीट) नियंत्रण व यूरिया प्रबंधन',
                'timeline': 'Day 15 – Day 55',
                'phase': 'Vegetative Care & Protection',
                'image': 'images/cultivation/universal-pest.jpg',
                'image_caption': 'Scouting the whorl of young maize plants for early pin-hole feeding by Fall Armyworm caterpillars',
                'metrics': [
                    {'label': 'Deadly Pest', 'value': 'Fall Armyworm (Spodoptera frugiperda)', 'icon': 'bi-bug'},
                    {'label': 'Pheromone Traps', 'value': '5 FAW Traps / Acre', 'icon': 'bi-radar'},
                    {'label': 'Critical Water', 'value': 'Tasseling & Silking Stage', 'icon': 'bi-water'},
                    {'label': 'Urea Splits', 'value': '3 Splits (Basal, Knee-High, Tasseling)', 'icon': 'bi-capsule'},
                ],
                'actions': [
                    'Scout plant central whorls weekly for sawdust-like frass and pin-hole windowing caused by Fall Armyworm (FAW).',
                    'Whorl Application: Drop a pinch of sand + lime mixture (9:1) or Metarhizium anisopliae (5 g/L) into whorls at early infestation.',
                    'Chemical defense: Spray Chlorantraniliprole 18.5% SC @ 0.4 ml/L or Emamectin Benzoate 5% SG @ 0.4 g/L directing nozzle right into the whorl.',
                    'Apply 2nd Nitrogen split (35 kg Urea) at knee-high stage (30–35 days) with earthing-up, and 3rd split (35 kg Urea) at tasseling.',
                ],
                'pro_tip': 'Drought at tasseling and silking (50–65 days) reduces pollination, resulting in half-empty cobs; never miss irrigation during silking.',
                'tool_shortcut': {'name': 'Scan Leaf for Pest & Blight', 'url': '/disease/'},
            },
            {
                'step_number': 3,
                'title': 'Cob Harvesting, Shelling & Poultry Mill / Mandi Sales',
                'hindi_title': 'भुट्टा तुड़ाई, थ्रेशिंग (शेलर) व पोल्ट्री फीड / मंडी बिक्री',
                'timeline': 'Day 95 – Day 115',
                'phase': 'Harvesting & Commercial',
                'image': 'images/cultivation/universal-harvest.jpg',
                'image_caption': 'Heavy golden cobs harvested with tightly filled grain kernels ready for mechanical shelling',
                'metrics': [
                    {'label': 'Maturity Sign', 'value': 'Husk Turns Paper Brown, Black Layer on Grain', 'icon': 'bi-check2-circle'},
                    {'label': 'Threshing', 'value': 'Tractor-Operated Maize Sheller', 'icon': 'bi-gear'},
                    {'label': 'Moisture Rule', 'value': 'Dry to < 14% for Poultry Millers', 'icon': 'bi-moisture'},
                    {'label': 'Average Yield', 'value': '28 – 35 Quintals / Acre', 'icon': 'bi-trophy'},
                ],
                'actions': [
                    'Harvest when outer cob husks turn papery pale brown and the "black layer" forms at the tip of grain attachment.',
                    'Snap cobs manually or use a combine with a corn head. De-husk cobs and sun-dry on clean ground for 2–3 days.',
                    'Shell dried cobs using a mechanical maize thresher/sheller (output 20–30 quintals/hr with <1% breakage).',
                    'Sun-dry kernels to 12–14% moisture before bagging. Poultry feed millers and starch manufacturers reject high-moisture corn due to aflatoxin risks.',
                    'Sell directly to poultry feed manufacturers, starch plants, or deliver to APMC mandis at Minimum Support Price (MSP).',
                ],
                'pro_tip': 'For Green Sweet Corn / Baby Corn: Harvest 70–75 days after sowing and sell directly to supermarket vendors at ₹15–₹25 per kg.',
                'tool_shortcut': {'name': 'Track Live Maize Mandi Prices', 'url': '/market/'},
            },
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 8. CHILLI / PEPPER GUIDE
# ─────────────────────────────────────────────────────────────────────────────
def _chilli_guide(crop_data):
    return {
        'crop_name': 'Chilli (Hot Pepper)',
        'hindi_name': 'हरी व सूखी मिर्च की उन्नत खेती, तुड़ाई व गुंटूर/मंडी विपणन',
        'botanical_name': 'Capsicum annuum',
        'total_duration': '140 – 170 Days',
        'ideal_season': 'Kharif (June–July Nursery) & Summer (Jan Nursery)',
        'expected_yield': '80 – 100 Qtl Green Chilli / 18 – 22 Qtl Dry Chilli / Acre',
        'market_channel': 'APMC Green Chilli Mandi, Guntur Dry Chilli Yard, Spices Board',
        'stages': [
            {
                'step_number': 1,
                'title': 'Pro-Tray Hybrid Nursery & Murda Disease Prevention',
                'hindi_title': 'प्रो-ट्रे पौधशाला व चुर्रा-मुर्रा (लीफ कर्ल) रोकथाम',
                'timeline': 'Day 0 – Day 35',
                'phase': 'Nursery Phase',
                'image': 'images/cultivation/universal-sowing.jpg',
                'image_caption': 'Healthy, virus-free hybrid chilli saplings raised under 40-mesh insect-proof net house',
                'metrics': [
                    {'label': 'Seed Rate', 'value': '80 – 100 g / Acre (Hybrids)', 'icon': 'bi-box-seam'},
                    {'label': 'Top Hybrids', 'value': 'Teja-4, Armoor, US-341, Sitara', 'icon': 'bi-stars'},
                    {'label': 'Nursery House', 'value': '40-Mesh Insect Net Protection', 'icon': 'bi-shield'},
                    {'label': 'Seedling Age', 'value': '30 – 35 Days (15 cm Height)', 'icon': 'bi-calendar-check'},
                ],
                'actions': [
                    'Chilli seeds must be grown strictly under a 40-mesh insect-proof net house to prevent whiteflies and thrips from infecting seedlings with Gemini virus (Murda rog).',
                    'Treat seeds with Imidacloprid 70 WS (5 g/kg) + Trichoderma viride (4 g/kg) before sowing in 98-cell pro-trays.',
                    'Use coco-peat + vermicompost substrate; irrigate twice daily with fine-rose can.',
                    'Drench seedlings with Copper Oxychloride (2 g/L) 2 days before transplanting.',
                ],
                'pro_tip': 'Raising chilli seedlings inside an insect-proof net house reduces field leaf curl virus incidence by over 80%.',
                'tool_shortcut': {'name': 'Calculate Chilli Nutrients', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 2,
                'title': 'Raised Bed Transplanting, Mulching & Drip System',
                'hindi_title': 'सिल्वर-ब्लैक मल्चिंग बेड रोपाई व ड्रिप फर्टिगेशन',
                'timeline': 'Day 35 – Day 45',
                'phase': 'Transplanting',
                'image': 'images/cultivation/universal-transplant.jpg',
                'image_caption': 'Transplanting sturdy chilli saplings into silver-black mulch on raised drip beds',
                'metrics': [
                    {'label': 'Bed Spacing', 'value': '120 cm Bed-to-Bed, 90 cm Top', 'icon': 'bi-rulers'},
                    {'label': 'Plant Spacing', 'value': '60 cm × 45 cm (Staggered)', 'icon': 'bi-arrows-expand'},
                    {'label': 'Mulch Film', 'value': '25-Micron Silver Black', 'icon': 'bi-layers'},
                    {'label': 'Plant Density', 'value': '7,000 – 7,500 Plants / Acre', 'icon': 'bi-grid-3x3'},
                ],
                'actions': [
                    'Prepare raised beds (90 cm wide, 30 cm height) with 50 cm pathways.',
                    'Incorporate 8 tonnes FYM + 50 kg DAP + 40 kg Potash + 10 kg Zinc + 10 kg Sulphur per acre as basal dose.',
                    'Lay inline drip lines and cover with 25-micron silver-black plastic mulch.',
                    'Transplant in late afternoon; drench root zone with 19:19:19 (3 g/L) on Day 4 to stimulate fast feeder root branching.',
                ],
                'pro_tip': 'Silver mulch deters thrips from landing on plants by reflecting UV light, drastically reducing viral vector pressure.',
                'tool_shortcut': {'name': 'Check Soil Health Card Parameters', 'url': '/crops/'},
            },
            {
                'step_number': 3,
                'title': 'Thrips, Mites & Anthracnose (Die-Back) Management',
                'hindi_title': 'थ्रिप्स, माइट्स (मकड़ी) व डाइबैक (उल्टा सूखा) नियंत्रण',
                'timeline': 'Day 50 – Day 130',
                'phase': 'Crop Protection & Nutrition',
                'image': 'images/cultivation/universal-pest.jpg',
                'image_caption': 'Blue sticky traps and preventive spray targeting black thrips and chilli fruit rot',
                'metrics': [
                    {'label': 'Black Thrips', 'value': 'Thrips parvispinus Defense', 'icon': 'bi-bug'},
                    {'label': 'Blue Sticky Traps', 'value': '25 – 30 Traps / Acre', 'icon': 'bi-shield-check'},
                    {'label': 'Die-Back Spray', 'value': 'Azoxystrobin + Difenoconazole', 'icon': 'bi-capsule'},
                    {'label': 'Foliar Booster', 'value': '0:52:34 + Micronutrients', 'icon': 'bi-flower1'},
                ],
                'actions': [
                    'Deploy 25 blue sticky traps per acre at canopy height to capture Invasive Black Thrips (Thrips parvispinus).',
                    'For Thrips & Mites: Alternate sprays of Spinetoram 11.7 SC @ 0.9 ml/L and Diafenthiuron 50 WP @ 1.25 g/L with thorough coverage under leaves.',
                    'For Anthracnose / Fruit Rot (Die-back): Spray Azoxystrobin 23 SC (1 ml/L) or Tebuconazole 25.9 EC (1.5 ml/L) at flowering and fruit set.',
                    'Fertigation: Supply 0:52:34 (3 kg/acre) during flowering, followed by 13:0:45 (4 kg/acre) during fruit development.',
                ],
                'pro_tip': 'Never let chilli beds stay saturated with excess water; root asphyxiation causes instant blossom drop and bacterial wilt.',
                'tool_shortcut': {'name': 'Scan Leaf for Chilli Anthracnose', 'url': '/disease/'},
            },
            {
                'step_number': 4,
                'title': 'Harvesting (Green vs Red Ripe) & Sun Drying',
                'hindi_title': 'तुड़ाई (हरी मिर्च या लाल सूखी मिर्च) व धूप में सुखाना',
                'timeline': 'Day 75 – Day 160',
                'phase': 'Harvesting',
                'image': 'images/cultivation/universal-harvest.jpg',
                'image_caption': 'Deep red ripe chillies harvested and spread uniformly on clean polythene sheets for sun curing',
                'metrics': [
                    {'label': 'Green Chilli Flushes', 'value': 'Every 8 – 10 Days (8–10 Pickings)', 'icon': 'bi-repeat'},
                    {'label': 'Red Chilli Harvest', 'value': 'When 100% Pods Turn Deep Red', 'icon': 'bi-check2-circle'},
                    {'label': 'Drying Ratio', 'value': '4 kg Fresh Red = 1 kg Dry Chilli', 'icon': 'bi-calculator'},
                    {'label': 'Moisture Level', 'value': 'Dry to 10% Moisture (Snap test)', 'icon': 'bi-moisture'},
                ],
                'actions': [
                    'For Fresh Green Chilli: Pick firm, mature, dark green pods every 8–10 days with intact stalks. Pack in 10 kg ventilated gunny/mesh bags.',
                    'For Dry Red Chilli: Allow fruits to turn 100% deep crimson red on the plant before picking.',
                    'Sun-dry red chillies on clean cement drying floors or black polythene tarpaulins; never dry on bare mud ground.',
                    'Turn pods 2–3 times daily for 8–10 days until dry. Moisture is right when pods rattle and break with a crisp snap sound.',
                ],
                'pro_tip': 'Cover drying chillies with tarpaulins at night to prevent morning dew from wetting pods, which causes black fungal discoloration.',
                'tool_shortcut': {'name': 'Field Yield Evaluation', 'url': '/crops/yield/'},
            },
            {
                'step_number': 5,
                'title': 'Grading, Jute Bag Packing & Guntur / Mandi Selling',
                'hindi_title': 'ग्रेडिंग, बोरी पैकिंग व गुंटूर/वारंगल/मंडी नीलामी',
                'timeline': 'Marketing Season (March – May)',
                'phase': 'Commercial & Selling',
                'image': 'images/cultivation/universal-mandi.jpg',
                'image_caption': 'Standard 40 kg jute bags of premium dry red chillies stacked at Guntur APMC yard',
                'metrics': [
                    {'label': 'Major Dry Mandis', 'value': 'Guntur (AP), Warangal, Byadgi (KA)', 'icon': 'bi-geo-alt'},
                    {'label': 'Standard Pack', 'value': '40 kg Clean Jute Gunny Bags', 'icon': 'bi-bag'},
                    {'label': 'Premium Criteria', 'value': 'High Color (ASTA), High Pungency', 'icon': 'bi-award'},
                    {'label': 'Net Profit/Acre', 'value': '₹80,000 – ₹1,50,000 / Acre', 'icon': 'bi-cash-coin'},
                ],
                'actions': [
                    'Sort out discolored, broken, and whitish pods (Talu chilli) from Grade-A uniform red pods.',
                    'Pack in 40 kg clean jute bags stitched tightly. Keep in a dry, ventilated warehouse or cold storage at 4–6°C.',
                    'Track live modal rates at Guntur and Byadgi mandis using the KrishiMitra Market tracker.',
                    'Selling Byadgi / Teja varieties to spice extraction plants (oleoresin companies) fetches high contract premiums for high ASTA color value.',
                ],
                'pro_tip': 'Cold-storing dry red chillies through summer allows selling in October–November at ₹3,000–₹5,000 per quintal higher rates.',
                'tool_shortcut': {'name': 'Track Live Chilli Mandi Prices', 'url': '/market/'},
            },
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 9. BANANA GUIDE
# ─────────────────────────────────────────────────────────────────────────────
def _banana_guide(crop_data):
    return {
        'crop_name': 'Banana',
        'hindi_name': 'केले (टिशू कल्चर G-9) की उच्च-तकनीक खेती व मंडी विपणन',
        'botanical_name': 'Musa acuminata',
        'total_duration': '11 – 13 Months',
        'ideal_season': 'June–July (Kharif) or Oct–Nov',
        'expected_yield': '35 – 45 Tonnes / Acre (Grand Naine G-9)',
        'market_channel': 'APMC Fruit Mandis, Exporters (Gulf/Iran), Cold Chain Ripening Chambers',
        'stages': [
            {
                'step_number': 1,
                'title': 'Certified Tissue Culture G-9 Plantlet Sourcing & Pit Prep',
                'hindi_title': 'प्रमाणित टिशू कल्चर (G-9) पौधे व गड्ढा तैयारी',
                'timeline': 'Month 1',
                'phase': 'Planting & Establishment',
                'image': 'images/cultivation/universal-sowing.jpg',
                'image_caption': 'Secondary-hardened tissue culture Grand Naine banana plantlets ready for pit planting',
                'metrics': [
                    {'label': 'Plant Material', 'value': 'Tissue Culture Grand Naine (G-9)', 'icon': 'bi-stars'},
                    {'label': 'Spacing', 'value': '1.8 m × 1.5 m (or 1.8 × 1.8 m)', 'icon': 'bi-rulers'},
                    {'label': 'Plant Population', 'value': '1,200 – 1,450 Plants / Acre', 'icon': 'bi-grid-3x3'},
                    {'label': 'Pit Dimension', 'value': '45 × 45 × 45 cm Dug & Refilled', 'icon': 'bi-box'},
                ],
                'actions': [
                    'Procure virus-indexed secondary-hardened tissue culture G-9 plantlets from DBT-accredited labs (height 30 cm with 5–6 green leaves).',
                    'Dig pits (45x45x45 cm) and expose to sunlight for 10 days to destroy soil-borne fungi and nematodes.',
                    'Refill pits with topsoil mixed with 10 kg decomposed FYM + 250 g Neem cake + 20 g Carbofuran + 50 g SSP.',
                    'Cut polybags carefully and plant plantlet at original nursery collar depth. Firm soil around root ball and irrigate immediately.',
                ],
                'pro_tip': 'Tissue culture plants ensure 98% uniformity, synchronous bunch emergence, and 30% higher bunch weight than traditional suckers.',
                'tool_shortcut': {'name': 'Calculate Banana Nutrition', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 2,
                'title': 'Drip Fertigation Schedule & De-Suckering',
                'hindi_title': 'ड्रिप फर्टिगेशन व सकर्स (अवांछित पुत्तियों) की कटाई',
                'timeline': 'Months 2 – 7',
                'phase': 'Vegetative Care',
                'image': 'images/cultivation/universal-irrigation.jpg',
                'image_caption': 'Lush, giant green banana canopy receiving daily drip fertigation directly at pseudostem base',
                'metrics': [
                    {'label': 'Water Demand', 'value': '15 – 25 Liters / Plant / Day', 'icon': 'bi-droplet'},
                    {'label': 'Total NPK/Plant', 'value': '200g N : 60g P : 300g K', 'icon': 'bi-capsule'},
                    {'label': 'De-Suckering', 'value': 'Remove All Suckers every 25 Days', 'icon': 'bi-scissors'},
                    {'label': 'Earthing Up', 'value': 'Build Broad Mounds at 3rd Month', 'icon': 'bi-triangle'},
                ],
                'actions': [
                    'Operate drip daily to maintain constant moisture without waterlogging (which induces Panama wilt).',
                    'Supply Nitrogen (Urea) and Potassium (MOP) in weekly fertigation splits from Month 2 through Month 8.',
                    'De-Suckering: Prune out all side suckers emerging around the mother stem up to shooting stage to direct all nutrition into main pseudostem.',
                    'Build a broad soil mound around the base at Month 3 to cover roots and anchor the heavy plant against wind toppling.',
                ],
                'pro_tip': 'Retain only 1 daughter sucker (follower) at shooting stage (Month 8) for the first ratoon crop; remove all other suckers ruthlessly.',
                'tool_shortcut': {'name': 'Evaluate Field Decision Margin', 'url': '/crops/yield/'},
            },
            {
                'step_number': 3,
                'title': 'Bunch Shooting, Propping & Blue Poly-Sleeve Bagging',
                'hindi_title': 'घार निकलना, बांस सहारा (प्रॉपिंग) व नीला बैग कवर',
                'timeline': 'Months 8 – 10',
                'phase': 'Bunch Management',
                'image': 'images/cultivation/universal-weeding.jpg',
                'image_caption': 'Heavy 30 kg banana bunch covered with blue ventilated poly-sleeve and supported by double bamboo props',
                'metrics': [
                    {'label': 'Propping', 'value': 'Double Bamboo Stakes per Tree', 'icon': 'bi-tree'},
                    {'label': 'Denavelling', 'value': 'Cut Male Bud after Last Hand Opens', 'icon': 'bi-scissors'},
                    {'label': 'Bagging', 'value': '6% Ventilated Blue Poly-Sleeve', 'icon': 'bi-layers'},
                    {'label': 'Bunch Weight Target', 'value': '28 – 35 kg per Bunch', 'icon': 'bi-trophy'},
                ],
                'actions': [
                    'Propping: Support every bearing pseudostem with 2 sturdy bamboo poles tied in a triangle to prevent toppling under 30 kg bunch weight.',
                    'Denavelling: Remove the purple terminal male flower bud (dil) 15 cm below the last fruit hand to conserve bunch carbohydrates.',
                    'Bunch Sleeve Bagging: Cover the emerging bunch with an 85x150 cm perforated blue polyethylene sleeve (6% aeration holes).',
                    'Sleeving prevents thrips scarring, sunburn, bird pecking, and dust, increasing export Grade-A bunch yield by 30%.',
                ],
                'pro_tip': 'Spray Potassium Sulphate (0:0:50) @ 5 g/L on bunches twice at 15-day intervals after shooting to produce plump, uniform fingers.',
                'tool_shortcut': {'name': 'Weather & Storm Alerts', 'url': '/weather/'},
            },
            {
                'step_number': 4,
                'title': 'Maturity Indices, Precision Cutting & Packhouse Export',
                'hindi_title': 'वैज्ञानिक कटाई (75-80% परिपक्वता), डी-हैंडिंग व मंडी बिक्री',
                'timeline': 'Months 11 – 13',
                'phase': 'Harvesting & Commercial',
                'image': 'images/cultivation/universal-harvest.jpg',
                'image_caption': 'Cut banana bunches carried on padded shoulder foam to farm packhouse for washing and crate packaging',
                'metrics': [
                    {'label': 'Maturity Index', 'value': 'Angles on Fingers Round Off (3/4th Full)', 'icon': 'bi-check2-circle'},
                    {'label': 'Export Markets', 'value': 'Dubai, Iran, Iraq, Saudi Arabia', 'icon': 'bi-globe2'},
                    {'label': 'Packhouse Steps', 'value': 'De-Handing, Alum Wash, CFB Box', 'icon': 'bi-box'},
                    {'label': 'Net Profit/Acre', 'value': '₹1,50,000 – ₹2,50,000 / Acre', 'icon': 'bi-cash-coin'},
                ],
                'actions': [
                    'Harvest when the angular ridges on banana fingers become rounded and fruit color turns light pale green.',
                    'Cut bunch leaving 30 cm peduncle handle; carry on foam-padded shoulders to farm packhouse to prevent finger bruising.',
                    'For Export & Modern Retail: De-hand bunches with curved knife, wash in clean water + 1% Alum tank to remove latex, treat crowns with fungicide, and pack in 13.5 kg CFB export cartons with plastic liner.',
                    'For Domestic Mandi: Load cushioned vehicles with whole bunches separated by banana leaf cushions; dispatch to ripening chambers.',
                    'Sell to institutional buyers, ripening unit aggregators, or export traders (Jalgaon, Solapur, Burhanpur, Anantapur).',
                ],
                'pro_tip': 'Bananas should never be allowed to ripen naturally on the tree; harvest green and ripen under controlled ethylene gas (100 ppm at 18°C) for uniform golden yellow color.',
                'tool_shortcut': {'name': 'Track Live Banana Mandi Prices', 'url': '/market/'},
            },
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 10. MUSTARD & RAPESEED GUIDE
# ─────────────────────────────────────────────────────────────────────────────
def _mustard_guide(crop_data):
    return {
        'crop_name': 'Mustard (Sarson)',
        'hindi_name': 'सरसों व तोरिया की उन्नत खेती, तेल प्रतिशत व मंडी विपणन',
        'botanical_name': 'Brassica juncea',
        'total_duration': '110 – 135 Days',
        'ideal_season': 'Rabi (October 1 – October 25)',
        'expected_yield': '8 – 12 Quintals / Acre (40–42% Oil)',
        'market_channel': 'Oil Expellers, Solvent Extractors, APMC Mandi at MSP',
        'stages': [
            {
                'step_number': 1,
                'title': 'Certified High-Oil Variety Sowing & Seed Treatment',
                'hindi_title': 'अधिक तेल वाली किस्मों का चयन व बीजोपचार',
                'timeline': 'October 5 – October 25',
                'phase': 'Seed & Sowing',
                'image': 'images/cultivation/universal-sowing.jpg',
                'image_caption': 'Healthy brassica seeds treated with fungicide and sown in fine moisture-conserved seedbed',
                'metrics': [
                    {'label': 'Seed Rate', 'value': '1.5 – 2.0 kg / Acre', 'icon': 'bi-box-seam'},
                    {'label': 'Top Varieties', 'value': 'Pusa Bold, Kranti, RH-749, Giriraj', 'icon': 'bi-stars'},
                    {'label': 'Spacing', 'value': '30 cm × 10 cm', 'icon': 'bi-rulers'},
                    {'label': 'Sowing Depth', 'value': '3 – 4 cm in Moist Soil', 'icon': 'bi-arrow-down-circle'},
                ],
                'actions': [
                    'Select high-oil, frost-tolerant certified varieties (RH-749, Giriraj, Pusa Mustard-25).',
                    'Treat seed with Apron 35 SD (6 g/kg) or Trichoderma viride (5 g/kg) to protect against White Rust and damping-off.',
                    'Sow using a seed drill or ridge maker at 30 cm line-to-line spacing at 3–4 cm depth in moist soil.',
                    'Thin excess plants at 15–18 days after sowing to maintain 10–12 cm between plants.',
                ],
                'pro_tip': 'Sowing between October 10–20 escapes peak mustard aphid infestation in December and maximizes grain oil content.',
                'tool_shortcut': {'name': 'Calculate Mustard Fertilizers', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 2,
                'title': 'Sulphur Basal Incorporation & Critical Irrigations',
                'hindi_title': 'सल्फर (गंधक) बेसल खाद व 2 महत्वपूर्ण सिंचाई',
                'timeline': 'Day 20 – Day 65',
                'phase': 'Vegetative Care',
                'image': 'images/cultivation/universal-irrigation.jpg',
                'image_caption': 'Vibrant yellow blooming mustard crop receiving flowering stage irrigation and sulphur nourishment',
                'metrics': [
                    {'label': 'Sulphur (90% WDG)', 'value': '15 kg / Acre (Boosts Oil +2%)', 'icon': 'bi-gem'},
                    {'label': 'Irrigation 1', 'value': 'Pre-Flowering Stage (30–35 Days)', 'icon': 'bi-droplet'},
                    {'label': 'Irrigation 2', 'value': 'Siliqua Pod Formation (60–65 Days)', 'icon': 'bi-water'},
                    {'label': 'Urea Top-Dress', 'value': '35 kg Urea with 1st Irrigation', 'icon': 'bi-capsule'},
                ],
                'actions': [
                    'Apply 15 kg Elemental Sulphur (90% WDG) or 200 kg Gypsum per acre as basal dose; sulphur directly increases seed oil concentration by 2–3%.',
                    'First irrigation at pre-flowering branch initiation (30–35 days); top-dress 35 kg Urea per acre immediately.',
                    'Second irrigation at siliquae (pod) filling stage (60–65 days) to ensure bold, heavyweight seeds.',
                    'Weed thoroughly before 30 days or apply Pendimethalin 30 EC (1 L/acre) as pre-emergence within 48 hours of sowing.',
                ],
                'pro_tip': 'Sulphur deficiency produces cupped yellow young leaves and lowers seed oil by up to 5%; never omit sulphur in oilseeds.',
                'tool_shortcut': {'name': 'Check Weather & Frost Warnings', 'url': '/weather/'},
            },
            {
                'step_number': 3,
                'title': 'Mustard Aphid & White Rust Integrated Control',
                'hindi_title': 'माहू (चेपा) कीट व सफेद रतुआ (व्हाइट रस्ट) रोकथाम',
                'timeline': 'Day 50 – Day 95',
                'phase': 'Crop Protection',
                'image': 'images/cultivation/universal-pest.jpg',
                'image_caption': 'Yellow sticky traps monitoring flying aphids on flowering mustard borders',
                'metrics': [
                    {'label': 'Key Insect', 'value': 'Mustard Aphid (Lipaphis erysimi)', 'icon': 'bi-bug'},
                    {'label': 'Key Disease', 'value': 'White Rust (Albugo candida)', 'icon': 'bi-virus'},
                    {'label': 'Yellow Traps', 'value': '20 Sheets / Acre on South Borders', 'icon': 'bi-shield-check'},
                    {'label': 'Safe Spray', 'value': 'Thiamethoxam 25 WG @ 50 g/Acre', 'icon': 'bi-spray'},
                ],
                'actions': [
                    'Install yellow sticky traps on field borders by mid-December to detect flying aphid colonies early.',
                    'If aphids cluster on 10% of plant central shoots: spray Dimethoate 30 EC @ 1.5 ml/L or Thiamethoxam 25 WG @ 0.25 g/L.',
                    'Spray late in the afternoon (after 3 PM) to avoid harming foraging honeybees, which are essential for 25% cross-pollination yield boost.',
                    'For White Rust & Alternaria Blight: Spray Mancozeb 75 WP @ 2.5 g/L at first appearance of white blisters on leaves.',
                ],
                'pro_tip': 'Placing 2–3 honeybee boxes per acre during blooming boosts mustard seed set by up to 25% and yields pure mustard honey.',
                'tool_shortcut': {'name': 'Scan Leaf for White Rust', 'url': '/disease/'},
            },
            {
                'step_number': 4,
                'title': 'Harvesting at 75% Yellow Pods & APMC Mandi MSP Sale',
                'hindi_title': '75% फली पीली होने पर कटाई, गहाई व सरकारी एमएसपी पर बिक्री',
                'timeline': 'Day 110 – Day 135',
                'phase': 'Harvesting & Commercial',
                'image': 'images/cultivation/universal-harvest.jpg',
                'image_caption': 'Threshing dried golden mustard pods and packing shiny black-brown seeds into clean bags',
                'metrics': [
                    {'label': 'Harvest Sign', 'value': '75% Pods Turn Golden Yellow', 'icon': 'bi-check2-circle'},
                    {'label': 'Moisture Target', 'value': 'Dry to < 8% Seed Moisture', 'icon': 'bi-moisture'},
                    {'label': 'Oil Standard', 'value': 'Minimum 38% – 42% Oil Content', 'icon': 'bi-award'},
                    {'label': 'Selling Channel', 'value': 'NAFED / State Mandi Procurement', 'icon': 'bi-shop'},
                ],
                'actions': [
                    'Harvest when 75–80% of siliquae (pods) turn golden yellow and seeds inside turn brown/black.',
                    'Harvest in early morning hours when pods are slightly moist with dew to avoid seed shattering losses.',
                    'Stack harvested bundles in field for 4–5 days to dry in the sun, then thresh with a tractor thresher.',
                    'Sun-dry clean seed on clean tarpaulins until moisture drops below 8% before bagging.',
                    'Deliver clean seed (foreign matter <2%) to government MSP procurement centers (NAFED) or private oil expeller units.',
                ],
                'pro_tip': 'Seed moisture above 9% triggers mold growth and rancidity in storage, reducing oil recovery rate dramatically.',
                'tool_shortcut': {'name': 'Check Live Mustard Mandi & MSP Rates', 'url': '/market/'},
            },
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 11. SOYBEAN GUIDE
# ─────────────────────────────────────────────────────────────────────────────
def _soybean_guide(crop_data):
    return {
        'crop_name': 'Soybean',
        'hindi_name': 'सोयाबीन की उन्नत खेती, बीजोपचार व मंडी विपणन',
        'botanical_name': 'Glycine max',
        'total_duration': '90 – 105 Days',
        'ideal_season': 'Kharif (June 20 – July 10 Monsoon Onset)',
        'expected_yield': '10 – 14 Quintals / Acre',
        'market_channel': 'Soybean Solvent Extractors (Indore/Nagpur), SOPA, APMC Mandi',
        'stages': [
            {
                'step_number': 1,
                'title': 'Seed Germination Test, Bio-Inoculation & BBF Sowing',
                'hindi_title': 'अंकुरण परीक्षण, राइजोबियम उपचार व ब्रॉड-बेड बुवाई',
                'timeline': 'Day 0 – Day 10',
                'phase': 'Seed & Sowing',
                'image': 'images/cultivation/universal-sowing.jpg',
                'image_caption': 'Rhizobium-inoculated soybean seeds sown on broad bed and furrows for perfect drainage',
                'metrics': [
                    {'label': 'Seed Rate', 'value': '25 – 30 kg / Acre (70% Germination)', 'icon': 'bi-box-seam'},
                    {'label': 'Top Varieties', 'value': 'JS-335, JS-9560, NRC-37, JS-2034', 'icon': 'bi-stars'},
                    {'label': 'Bio-Inoculant', 'value': 'Bradyrhizobium japonicum + PSB', 'icon': 'bi-capsule'},
                    {'label': 'Sowing Method', 'value': 'Broad Bed Furrow (BBF) 45 × 5 cm', 'icon': 'bi-rulers'},
                ],
                'actions': [
                    'Perform a seed germination test prior to sowing; use 25 kg/acre only if germination exceeds 70%.',
                    'Seed Treatment: Treat seed with Carboxin + Thiram (2 g/kg), followed by Bradyrhizobium japonicum culture (5 g/kg) and PSB (5 g/kg).',
                    'Sow using a Broad Bed Furrow (BBF) seed drill after 75–100 mm monsoon rain has thoroughly soaked the root zone.',
                    'Maintain seed sowing depth at 3–4 cm. Sowing deeper than 5 cm results in seedling mortality.',
                ],
                'pro_tip': 'BBF (Broad Bed Furrow) bed system acts as a lifeline: draining excess water during heavy deluge and conserving moisture during dry spells.',
                'tool_shortcut': {'name': 'Calculate Soybean Nutrients', 'url': '/crops/fertilizer/'},
            },
            {
                'step_number': 2,
                'title': 'Early Weed Management & Girdle Beetle Defense',
                'hindi_title': 'निराई-गुड़ाई, खरपतवार नियंत्रण व गर्डल बीटल रोकथाम',
                'timeline': 'Day 15 – Day 55',
                'phase': 'Vegetative Care & Protection',
                'image': 'images/cultivation/universal-pest.jpg',
                'image_caption': 'Inspecting soybean stem nodes for girdle beetle rings and leaf-eating caterpillar damage',
                'metrics': [
                    {'label': 'Post-Em Herbicide', 'value': 'Imazethapyr 10 SL @ 300 ml/Acre', 'icon': 'bi-shield-check'},
                    {'label': 'Key Pest', 'value': 'Girdle Beetle, Spodoptera, Semilooper', 'icon': 'bi-bug'},
                    {'label': 'Flowering Stage', 'value': 'Crucial Moisture Window (35–45 Days)', 'icon': 'bi-flower2'},
                    {'label': 'Foliar Spray', 'value': '0:52:34 @ 1 kg/Acre at Flowering', 'icon': 'bi-flower1'},
                ],
                'actions': [
                    'Apply post-emergence herbicide Imazethapyr 10% SL @ 300 ml/acre at 15–20 days when weeds have 2–3 leaves.',
                    'For Girdle Beetle (stem ring girdling): Spray Chlorantraniliprole 18.5 SC @ 60 ml/acre or Thiamethoxam + Lambda-cyhalothrin @ 80 ml/acre.',
                    'For Spodoptera & Semilooper caterpillars: Spray Emamectin Benzoate 5% SG @ 80 g/acre during evening hours.',
                    'Never let the field face severe water deficit during flowering and pod development; provide supplemental sprinkler irrigation if monsoon breaks.',
                ],
                'pro_tip': 'Install T-shaped bird perches (15/acre) across the field; insectivorous birds naturally devour thousands of defoliator caterpillars daily.',
                'tool_shortcut': {'name': 'Scan Leaf for Pest & Yellow Mosaic', 'url': '/disease/'},
            },
            {
                'step_number': 3,
                'title': 'Maturity Pod Rattle Harvesting & APMC / Solvent Mill Sales',
                'hindi_title': 'पत्तियों के झड़ने पर कटाई, दाना गहाई व सोयाबीन मिल/मंडी बिक्री',
                'timeline': 'Day 90 – Day 105',
                'phase': 'Harvesting & Commercial',
                'image': 'images/cultivation/universal-harvest.jpg',
                'image_caption': 'Mature soybean field harvested at leaf drop stage with golden rattling pods',
                'metrics': [
                    {'label': 'Harvest Indicator', 'value': 'Leaves Drop, Pods Rattle when Shaken', 'icon': 'bi-check2-circle'},
                    {'label': 'Moisture at Harvest', 'value': '13% – 14% Pod Moisture', 'icon': 'bi-moisture'},
                    {'label': 'Thresher Speed', 'value': 'Low Cylinder RPM (300-400) to Avoid Cracks', 'icon': 'bi-speedometer'},
                    {'label': 'Major Mandis', 'value': 'Indore, Ujjain, Latur, Kota, Akola', 'icon': 'bi-geo-alt'},
                ],
                'actions': [
                    'Harvest when 90% of the leaves have turned yellow and fallen off, and pods make a rattling sound when shaken.',
                    'Harvest with combine or sickles within 3–4 days of maturity to prevent pod shattering and seed loss.',
                    'Reduce thresher cylinder speed (350–400 RPM); high mechanical impact cracks the delicate soybean seed coat, destroying germination and oil viability.',
                    'Sun-dry seed to 10–12% moisture before packing in clean 50 kg gunny bags.',
                    'Compare Indore and Latur APMC modal rates on KrishiMitra; sell to licensed solvent extraction plants or government procurement centers.',
                ],
                'pro_tip': 'Seed soybean lots stored for next season must be kept strictly below 10% moisture in wooden pallet stacked bags in a cool, ventilated shed.',
                'tool_shortcut': {'name': 'Track Live Soybean Mandi Rates', 'url': '/market/'},
            },
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 12. MANGO GUIDE
# ─────────────────────────────────────────────────────────────────────────────
def _mango_guide(crop_data):
    return {
        'crop_name': 'Mango (King of Fruits)',
        'hindi_name': 'आम के बगीचे का प्रबंधन, पुष्पन, तुड़ाई व निर्यात मंडी विपणन',
        'botanical_name': 'Mangifera indica',
        'total_duration': 'Perennial Orchard (Harvest March–July)',
        'ideal_season': 'Flowering (Dec–Jan), Fruit Harvest (April–July)',
        'expected_yield': '6 – 10 Tonnes / Acre (Mature Orchard)',
        'market_channel': 'APMC Fruit Mandis, Pulp Processors (Maaza/Frooti), APEDA Export',
        'stages': [
            {
                'step_number': 1,
                'title': 'Canopy Pruning, Basin Cleaning & Paclobutrazol Drench',
                'hindi_title': 'कटाई-छंटाई, थाला सफाई व कल्टार (पैक्लोब्युट्राजोल) प्रयोग',
                'timeline': 'September – October',
                'phase': 'Canopy & Flowering Induction',
                'image': 'images/cultivation/universal-weeding.jpg',
                'image_caption': 'Mature grafted mango trees with opened center canopy and clean drip circular basin',
                'metrics': [
                    {'label': 'Canopy Type', 'value': 'Open Center Architecture (Airflow)', 'icon': 'bi-tree'},
                    {'label': 'Paclobutrazol', 'value': 'Cultar @ 3 ml per meter canopy diameter', 'icon': 'bi-capsule'},
                    {'label': 'Water Withholding', 'value': 'Stop Irrigation Oct–Dec (Stress)', 'icon': 'bi-droplet-slash'},
                    {'label': 'Organic FYM', 'value': '40 – 50 kg / Tree + 2 kg Neem Cake', 'icon': 'bi-flower1'},
                ],
                'actions': [
                    'Prune criss-cross, dead, diseased branches and water suckers immediately after previous harvest to allow sunlight penetration to lower tree skirts.',
                    'Clean the tree basin (ring 1.5 m around trunk); incorporate 40–50 kg decomposed FYM + 2 kg SSP + 1 kg MOP per mature tree.',
                    'In alternate-bearing varieties (Alphonso, Dasheri): Drench Paclobutrazol (Cultar) @ 3 ml per meter canopy diameter in tree basin in mid-September to induce heavy, uniform flowering.',
                    'Withhold all irrigation during October to December; slight drought stress triggers floral bud differentiation rather than vegetative flush.',
                ],
                'pro_tip': 'Applying paclobutrazol (Cultar) guarantees synchronous early flowering, advancing fruit maturity by 20 days to capture record high early-season market rates.',
                'tool_shortcut': {'name': 'Check Orchard Weather & Night Temps', 'url': '/weather/'},
            },
            {
                'step_number': 2,
                'title': 'Panicle Protection: Mango Hopper & Powdery Mildew',
                'hindi_title': 'बौर (पुष्पगुच्छ) सुरक्षा: भुनगा (हॉपर) व चूर्णिल आसिता',
                'timeline': 'January – February (Panicle Emergence)',
                'phase': 'Flower & Fruit Set',
                'image': 'images/cultivation/universal-pest.jpg',
                'image_caption': 'Dense mango panicle blooming with honeybee pollinators and zero hopper infestation',
                'metrics': [
                    {'label': 'Major Insect', 'value': 'Mango Hopper (Amritodus atkinsoni)', 'icon': 'bi-bug'},
                    {'label': 'Major Disease', 'value': 'Powdery Mildew (Oidium mangiferae)', 'icon': 'bi-virus'},
                    {'label': 'Spray 1 (Bud Break)', 'value': 'Imidacloprid 17.8 SL (0.3 ml/L) + Wettable Sulphur (2 g/L)', 'icon': 'bi-shield-check'},
                    {'label': 'Spray 2 (Fruitlet)', 'value': 'Thiamethoxam (0.3 g/L) + Hexaconazole (1 ml/L)', 'icon': 'bi-spray'},
                ],
                'actions': [
                    '1st Spray at panicle bud burst: Spray Imidacloprid 17.8% SL @ 0.3 ml/L + Wettable Sulphur @ 2 g/L to knock out overwintering hoppers and mildew spores.',
                    '2nd Spray at pea-size fruitlet stage: Apply Thiamethoxam 25 WG @ 0.3 g/L + Hexaconazole 5% SC @ 1 ml/L.',
                    'STRICT WARNING: Never spray synthetic insecticides during peak full bloom; allow honeybees and syrphid flies to complete cross-pollination.',
                    'Resume light circular basin irrigation once pea-sized fruitlets set (February); irrigate every 10–12 days to prevent fruit drop.',
                ],
                'pro_tip': 'Spray Potassium Nitrate (13:0:45) @ 10 g/L twice at marble-size stage to accelerate fruit bulking and prevent pre-harvest drop.',
                'tool_shortcut': {'name': 'Scan Panicle Leaf for Mildew', 'url': '/disease/'},
            },
            {
                'step_number': 3,
                'title': 'Fruit Fly Defense & Paper Sleeve Bagging',
                'hindi_title': 'फल मक्खी (फ्रूट फ्लाई) नियंत्रण व फल बैगिंग',
                'timeline': 'March – May',
                'phase': 'Fruit Maturation',
                'image': 'images/cultivation/universal-weeding.jpg',
                'image_caption': 'Two-ply breathable brown fruit bags protecting developing mangoes against fruit fly stings',
                'metrics': [
                    {'label': 'Deadly Pest', 'value': 'Oriental Fruit Fly (Bactrocera dorsalis)', 'icon': 'bi-bug'},
                    {'label': 'Pheromone Lures', 'value': 'Methyl Eugenol Traps (6 – 8 / Acre)', 'icon': 'bi-radar'},
                    {'label': 'Individual Bagging', 'value': 'Two-Ply Paper Bags at Marble Stage', 'icon': 'bi-bag'},
                    {'label': 'Export Eligibility', 'value': 'Vapour Heat Treatment (VHT) / Irradiation', 'icon': 'bi-award'},
                ],
                'actions': [
                    'Install 6–8 Methyl Eugenol pheromone traps per acre at tree canopy height by March to mass-trap male fruit flies.',
                    'Bag developing fruits individually at 45–50 days after fruit set using double-layered breathable brown paper bags.',
                    'Bagging completely eliminates fruit fly egg puncture, protects against anthracnose blemishes, and produces spotless golden skin.',
                    'Collect and deeply bury any dropped fruit daily to eradicate maggots from the orchard soil.',
                ],
                'pro_tip': 'Paper-bagged mangoes fetch ₹300–₹500 per carton premium in European and Gulf export markets due to zero pesticide residue on skin.',
                'tool_shortcut': {'name': 'Weather Forecast for Orchard', 'url': '/weather/'},
            },
            {
                'step_number': 4,
                'title': 'Harvesting with Calyx Stalk & APMC / Export Selling',
                'hindi_title': 'डंडी सहित वैज्ञानिक तुड़ाई (1 सेमी), ग्रेडिंग व मंडी/निर्यात',
                'timeline': 'April – July (Harvest Season)',
                'phase': 'Harvesting & Commercial',
                'image': 'images/cultivation/universal-harvest.jpg',
                'image_caption': 'Hand-harvested export grade mangoes with 1 cm pedicel stalk packed in CFB cartons with foam sleeves',
                'metrics': [
                    {'label': 'Maturity Sign', 'value': 'Shoulders Raised Above Stalk Cavity, Tapka', 'icon': 'bi-check2-circle'},
                    {'label': 'Harvest Tool', 'value': 'Pole Harvester with Net and Sharp Blade', 'icon': 'bi-scissors'},
                    {'label': 'Latex Prevention', 'value': 'Retain 1 – 2 cm Pedicel Stalk', 'icon': 'bi-hand-index'},
                    {'label': 'Export Cartons', 'value': '5 kg Corrugated Fiberboard (CFB) Boxes', 'icon': 'bi-box'},
                ],
                'actions': [
                    'Harvest when fruit shoulder rises above stem cavity and color turns light olive-green with a slight yellowish beak (specific gravity 1.01–1.02).',
                    'Always harvest using a pole harvester fitted with a net bag and sharp cutter; NEVER shake trees to drop fruits.',
                    'Keep 1.0–2.0 cm stalk attached to the fruit; harvesting without stalk causes burning black latex (chep) to squirt onto skin, triggering stem-end rot.',
                    'Wash fruits in warm water (48°C for 5 minutes) containing 500 ppm Carbendazim; dry under air fans and pack in 5 kg CFB export cartons lined with foam net sleeves.',
                    'Dispatch to regional APMC fruit mandis (Vashi, Azadpur, Ahmedabad, Lucknow) or APEDA packhouses for Vapour Heat Treatment (VHT).',
                ],
                'pro_tip': 'De-sapping mangoes by placing them inverted on perforated desapping conveyor racks for 4 hours prevents black latex burns completely.',
                'tool_shortcut': {'name': 'Track Live Mango Mandi Prices', 'url': '/market/'},
            },
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
# 13. GENERIC INTELLIGENT CROP GUIDE (FOR ALL OTHER 55+ CROPS)
# ─────────────────────────────────────────────────────────────────────────────
def _generic_crop_guide(crop_name, crop_data):
    """Dynamically generate a comprehensive 7-stage cultivation guide tailored to crop attributes."""
    crop_data = crop_data or {}
    group = crop_data.get('group', 'Vegetables')
    planting = crop_data.get('planting', 'Seeds')
    climate = crop_data.get('climate', 'Warm season')
    soil = crop_data.get('soil', 'Loamy soil')
    watering = crop_data.get('watering', 'Regular moisture')
    ph = crop_data.get('ph', '6.0 – 7.5')

    stages = [
        {
            'step_number': 1,
            'title': f'{crop_name} Planting Material Selection & Sowing',
            'hindi_title': f'{crop_name} का उत्तम बीज/पौध चयन एवं बुवाई विधि',
            'timeline': 'Stage 1 · Day 0 – Day 25',
            'phase': 'Foundation Phase',
            'image': 'images/cultivation/universal-sowing.jpg',
            'image_caption': f'Selected high-yielding certified {crop_name} planting material treated and prepared for establishment',
            'metrics': [
                {'label': 'Material', 'value': planting, 'icon': 'bi-box-seam'},
                {'label': 'Climate Fit', 'value': climate, 'icon': 'bi-sun'},
                {'label': 'Ideal pH', 'value': ph, 'icon': 'bi-speedometer2'},
                {'label': 'Soil Type', 'value': soil, 'icon': 'bi-layers'},
            ],
            'actions': [
                f'Select certified, high-yielding varieties of {crop_name} suited for your state agro-climatic region and local market demand.',
                f'Inspect planting material ({planting}): ensure free from fungal rot, viral symptoms, or mechanical injury.',
                'Perform prophylactic seed/root treatment using Trichoderma viride @ 5 g/kg or Carbendazim @ 2 g/kg.',
                'Prepare a fertile, well-drained nursery bed or direct sowing layout according to local seasonal recommendations.',
            ],
            'pro_tip': f'Always obtain certified seeds from ICAR/SAU institutes or licensed seed dealers; keep purchase receipts and lot numbers for traceability.',
            'tool_shortcut': {'name': 'Calculate Required Seed & Fertilizer', 'url': '/crops/fertilizer/'},
        },
        {
            'step_number': 2,
            'title': 'Land Preparation, Soil Tilth & Basal Nutrition',
            'hindi_title': 'खेत की गहरी जुताई, मेड़/क्यारी तैयारी व आधार खाद',
            'timeline': 'Stage 2 · Day 15 – Day 30',
            'phase': 'Land Preparation',
            'image': 'images/cultivation/universal-landprep.jpg',
            'image_caption': f'Deep ploughed and pulverized soil bed prepared for {crop_name} with organic manure',
            'metrics': [
                {'label': 'Soil Tilth', 'value': f'Well-pulverized {soil}', 'icon': 'bi-gear'},
                {'label': 'Organic FYM', 'value': '8 – 10 Tonnes / Acre', 'icon': 'bi-flower1'},
                {'label': 'Drainage', 'value': 'Essential (No Waterlogging)', 'icon': 'bi-droplet-half'},
                {'label': 'Bed System', 'value': 'Raised Beds or Ridges', 'icon': 'bi-rulers'},
            ],
            'actions': [
                'Plough the main field 2–3 times followed by harrowing to achieve a friable crumbly soil tilth.',
                'Incorporate 8–10 tonnes of well-rotted FYM or compost per acre during final ploughing to boost soil organic matter.',
                f'Form beds, ridges, or channels appropriate for {crop_name} to guarantee swift surface drainage after rain.',
                'Apply basal doses of Phosphorus and Potassium based on your Soil Health Card test values.',
            ],
            'pro_tip': 'Incorporate bio-fertilizers like Azotobacter / PSB @ 2 kg/acre mixed with 100 kg FYM to boost nutrient bioavailability by 25%.',
            'tool_shortcut': {'name': 'Review Soil Health Recommendations', 'url': '/crops/'},
        },
        {
            'step_number': 3,
            'title': f'{crop_name} Field Establishment & Proper Spacing',
            'hindi_title': f'{crop_name} खेत रोपाई/बुवाई एवं आदर्श कतार दूरी',
            'timeline': 'Stage 3 · Day 25 – Day 40',
            'phase': 'Crop Establishment',
            'image': 'images/cultivation/universal-transplant.jpg',
            'image_caption': f'Healthy {crop_name} seedlings established in rows with proper spatial canopy layout',
            'metrics': [
                {'label': 'Planting Type', 'value': planting, 'icon': 'bi-pin-map'},
                {'label': 'Timing', 'value': 'Late Afternoon or Cloudy Day', 'icon': 'bi-clock'},
                {'label': 'Irrigation', 'value': 'Immediate Light Watering', 'icon': 'bi-droplet'},
                {'label': 'Gap Filling', 'value': 'Within 7 Days', 'icon': 'bi-check2-circle'},
            ],
            'actions': [
                f'Establish {crop_name} at standard row-to-row and plant-to-plant spacing to maximize light interception and aeration.',
                'Avoid transplanting or sowing during scorching midday heat; late afternoon planting ensures minimal transpiration stress.',
                'Press soil gently around plant root collars and provide an immediate light establishment irrigation.',
                'Inspect the field on Day 5 and replace any failed planting spots to maintain 100% plant density.',
            ],
            'pro_tip': 'Maintaining optimal plant density per acre is the foundation of high yield; under-population cannot be compensated by extra fertilizer later.',
            'tool_shortcut': {'name': 'Field Yield & Spacing Decision', 'url': '/crops/yield/'},
        },
        {
            'step_number': 4,
            'title': 'Water Management & Irrigation Schedule',
            'hindi_title': 'सिंचाई प्रबंधन, ड्रिप/नाली विधि व जल संरक्षण',
            'timeline': 'Stage 4 · Day 30 – Day 90',
            'phase': 'Vegetative Care',
            'image': 'images/cultivation/universal-irrigation.jpg',
            'image_caption': f'Precision drip irrigation delivering moisture directly to root zone of {crop_name}',
            'metrics': [
                {'label': 'Water Regimen', 'value': watering, 'icon': 'bi-droplet'},
                {'label': 'Method', 'value': 'Drip or Furrow Irrigation', 'icon': 'bi-moisture'},
                {'label': 'Critical Stage', 'value': 'Flowering & Yield Formation', 'icon': 'bi-flower2'},
                {'label': 'Drainage', 'value': 'Clear Furrow Outlets', 'icon': 'bi-water'},
            ],
            'actions': [
                f'Irrigate {crop_name} according to soil moisture feel and critical growth stages (vegetative flush, flowering, product development).',
                'Adopt drip irrigation wherever feasible to save 40–50% water and enable uniform fertigation.',
                'Avoid over-watering or stagnant water around root collars which triggers phytophthora root rot and wilt.',
                'Mulch beds with organic straw or silver-black plastic film to conserve root-zone moisture during hot dry spells.',
            ],
            'pro_tip': 'Always irrigate early in the morning to keep plant foliage dry overnight, curbing bacterial and fungal leaf spots.',
            'tool_shortcut': {'name': 'Check Real-Time Weather & Rain Advisory', 'url': '/weather/'},
        },
        {
            'step_number': 5,
            'title': 'Integrated Pest & Disease Scouting (IPM)',
            'hindi_title': 'एकीकृत कीट व रोग प्रबंधन (आईपीएम एवं जैव सुरक्षा)',
            'timeline': 'Stage 5 · Continuous Scouting',
            'phase': 'Crop Protection',
            'image': 'images/cultivation/universal-pest.jpg',
            'image_caption': f'Monitoring {crop_name} canopy with eco-friendly traps and preventive biological sprays',
            'metrics': [
                {'label': 'Strategy', 'value': 'IPM (Biological + Cultural)', 'icon': 'bi-shield-check'},
                {'label': 'Traps', 'value': 'Yellow/Blue Traps & Pheromones', 'icon': 'bi-radar'},
                {'label': 'Bio-Spray', 'value': 'Neem Oil 10,000 ppm / Beauveria', 'icon': 'bi-flower1'},
                {'label': 'Safety', 'value': 'Respect Pre-Harvest Interval (PHI)', 'icon': 'bi-exclamation-octagon'},
            ],
            'actions': [
                f'Walk field rows twice a week to inspect {crop_name} leaves, stems, and growing tips for early pest signs.',
                'Install yellow sticky traps (15–20/acre) to monitor and trap whiteflies, aphids, and leafminers.',
                'Apply neem-based bio-pesticides or approved biological controls at early appearance of insect pests.',
                'If synthetic pesticides are required, use only CIBRC-registered products for this crop and follow exact label dosage and waiting periods.',
            ],
            'pro_tip': 'Rotate chemical pesticide groups with different Modes of Action (IRAC codes) to prevent insect pests developing chemical resistance.',
            'tool_shortcut': {'name': 'AI Leaf Photo Disease Detection', 'url': '/disease/'},
        },
        {
            'step_number': 6,
            'title': f'{crop_name} Scientific Harvesting & Maturity Signs',
            'hindi_title': f'{crop_name} की परिपक्वता पहचान, सही समय पर कटाई व तुड़ाई',
            'timeline': 'Stage 6 · Harvest Window',
            'phase': 'Harvesting',
            'image': 'images/cultivation/universal-harvest.jpg',
            'image_caption': f'Harvesting peak-quality {crop_name} produce during cool morning hours with clean farm crates',
            'metrics': [
                {'label': 'Harvest Timing', 'value': 'Early Morning (6 AM – 9 AM)', 'icon': 'bi-clock'},
                {'label': 'Maturity', 'value': 'Optimal Commercial Maturity', 'icon': 'bi-check2-circle'},
                {'label': 'Containers', 'value': 'Plastic Crates / Clean Bags', 'icon': 'bi-box'},
                {'label': 'Field Handling', 'value': 'Zero Bruising, Retain Calyx', 'icon': 'bi-hand-index'},
            ],
            'actions': [
                f'Harvest {crop_name} strictly when produce reaches commercial maturity standards (color, size, firmness, or seed moisture).',
                'Pick during cool early morning hours to dissipate field heat and prolong storage shelf life.',
                'Handle edible produce gently using clean sharp clippers or hand twists; discard damaged or diseased units.',
                'Move harvested produce immediately to shaded packing sheds; never leave harvest exposed to hot midday direct sunlight.',
            ],
            'pro_tip': 'Pre-cooling produce in a shaded, well-ventilated packing shed immediately after picking doubles freshness retention.',
            'tool_shortcut': {'name': 'Evaluate Net Harvest Economics', 'url': '/crops/yield/'},
        },
        {
            'step_number': 7,
            'title': 'Grading, Packaging & APMC Mandi Commercial Selling',
            'hindi_title': 'सफाई, ग्रेडिंग, पैकिंग व मंडी/ई-नाम पर उच्चतम भाव में बिक्री',
            'timeline': 'Stage 7 · Marketing & Revenue',
            'phase': 'Commercial & Selling',
            'image': 'images/cultivation/universal-mandi.jpg',
            'image_caption': f'Sorted and graded {crop_name} lots presented at wholesale APMC market for top price bidding',
            'metrics': [
                {'label': 'Grading', 'value': 'Grade A (Super) / Grade B (Local)', 'icon': 'bi-award'},
                {'label': 'Packaging', 'value': 'Ventilated Crates / Jute Sacks', 'icon': 'bi-bag'},
                {'label': 'Market Channels', 'value': 'APMC Mandi / e-NAM / FPO / Retail', 'icon': 'bi-shop'},
                {'label': 'Value Addition', 'value': '+20% Price via Sorting & Grading', 'icon': 'bi-graph-up-arrow'},
            ],
            'actions': [
                f'Clean and grade {crop_name} into Grade A (uniform size, flawless, premium color) and Grade B (standard quality).',
                'Pack in standardized ventilated plastic crates or clean jute gunny bags as demanded by wholesale buyers.',
                'Check live wholesale modal rates on the KrishiMitra Market Price Tracker and e-NAM portal before dispatching transport.',
                'Transport in evening or early morning hours using covered, well-ventilated vehicles to arrive before morning mandi auctions.',
                'Explore direct contract arrangements with Farmer Producer Organizations (FPOs), supermarket aggregators, or local processing units.',
            ],
            'pro_tip': 'Selling graded produce in standard weight packaging earns ₹3–₹8/kg higher auction prices than selling mixed, unsorted cartloads.',
            'tool_shortcut': {'name': 'Explore Live Mandi Prices for this Crop', 'url': '/market/'},
        },
    ]

    return {
        'crop_name': crop_name,
        'hindi_name': f'{crop_name} की सम्पूर्ण खेती व मंडी बिक्री मार्गदर्शिका',
        'botanical_name': crop_data.get('scientific_name', ''),
        'total_duration': 'Full Crop Cycle',
        'ideal_season': climate,
        'expected_yield': 'High Regional Benchmark',
        'market_channel': 'APMC Wholesale Mandi, e-NAM Portal, FPO Contracts',
        'stages': stages,
    }
