"""Agronomist & Precision Farming Decision Engine.

Calculates accurate crop input requirements and delivers actionable, season-specific
agronomic advice—balancing nutrient loss caused by weed competition against
microclimate preservation (such as soil moisture retention during extreme heat).

Rules Implemented:
- Rule A: Weed Nutrient Steal (Fertilizer Penalty Adjustment & Application Placement)
- Rule B: Summer Season Weed Strategy (Microclimate Preservation & Strip Slash-and-Mulch)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# Baseline recommended N-P2O5-K2O rates, spacing, seed weights, and economic baselines (ICAR / SAU standards)
CROP_NUTRIENT_BASELINES: Dict[str, Dict[str, Any]] = {
    # ─── Cereals & Millets ───
    'Maize': {
        'n': 120, 'p': 60, 'k': 40, 'emoji': '🌽', 'category': 'Cereal / Grain',
        'row_spacing': 24.0, 'plant_spacing': 8.0, 'seed_weight_1000': 280.0,
        'yield_qtl_ac': 28.0, 'price_qtl': 2225.0, 'cost_ac': 18000.0,
    },
    'Rice': {
        'n': 120, 'p': 50, 'k': 50, 'emoji': '🌾', 'category': 'Cereal / Grain',
        'row_spacing': 8.0, 'plant_spacing': 4.0, 'seed_weight_1000': 25.0,
        'yield_qtl_ac': 22.0, 'price_qtl': 2300.0, 'cost_ac': 22000.0,
    },
    'Wheat': {
        'n': 120, 'p': 60, 'k': 40, 'emoji': '🌾', 'category': 'Cereal / Grain',
        'row_spacing': 8.0, 'plant_spacing': 2.0, 'seed_weight_1000': 40.0,
        'yield_qtl_ac': 20.0, 'price_qtl': 2275.0, 'cost_ac': 16000.0,
    },
    'Bajra': {
        'n': 80, 'p': 40, 'k': 20, 'emoji': '🌾', 'category': 'Millet / Cereal',
        'row_spacing': 18.0, 'plant_spacing': 4.0, 'seed_weight_1000': 8.0,
        'yield_qtl_ac': 14.0, 'price_qtl': 2625.0, 'cost_ac': 12000.0,
    },
    'Jowar': {
        'n': 80, 'p': 40, 'k': 40, 'emoji': '🌾', 'category': 'Millet / Cereal',
        'row_spacing': 18.0, 'plant_spacing': 6.0, 'seed_weight_1000': 30.0,
        'yield_qtl_ac': 15.0, 'price_qtl': 3371.0, 'cost_ac': 13000.0,
    },
    'Ragi': {
        'n': 60, 'p': 30, 'k': 30, 'emoji': '🌾', 'category': 'Millet / Cereal',
        'row_spacing': 10.0, 'plant_spacing': 4.0, 'seed_weight_1000': 3.5,
        'yield_qtl_ac': 12.0, 'price_qtl': 4290.0, 'cost_ac': 12000.0,
    },
    'Barley': {
        'n': 60, 'p': 30, 'k': 20, 'emoji': '🌾', 'category': 'Cereal / Grain',
        'row_spacing': 9.0, 'plant_spacing': 2.0, 'seed_weight_1000': 42.0,
        'yield_qtl_ac': 16.0, 'price_qtl': 1850.0, 'cost_ac': 13000.0,
    },

    # ─── Pulses & Legumes ───
    'Chickpea': {
        'n': 20, 'p': 40, 'k': 20, 'emoji': '🫘', 'category': 'Pulse / Legume',
        'row_spacing': 12.0, 'plant_spacing': 4.0, 'seed_weight_1000': 220.0,
        'yield_qtl_ac': 8.0, 'price_qtl': 5440.0, 'cost_ac': 14000.0,
    },
    'Gram': {
        'n': 20, 'p': 40, 'k': 20, 'emoji': '🫘', 'category': 'Pulse / Legume',
        'row_spacing': 12.0, 'plant_spacing': 4.0, 'seed_weight_1000': 220.0,
        'yield_qtl_ac': 8.0, 'price_qtl': 5440.0, 'cost_ac': 14000.0,
    },
    'Pigeonpea': {
        'n': 25, 'p': 50, 'k': 20, 'emoji': '🫘', 'category': 'Pulse / Legume',
        'row_spacing': 36.0, 'plant_spacing': 12.0, 'seed_weight_1000': 110.0,
        'yield_qtl_ac': 8.0, 'price_qtl': 7550.0, 'cost_ac': 16000.0,
    },
    'Green Gram': {
        'n': 20, 'p': 40, 'k': 20, 'emoji': '🫘', 'category': 'Pulse / Legume',
        'row_spacing': 12.0, 'plant_spacing': 4.0, 'seed_weight_1000': 45.0,
        'yield_qtl_ac': 5.0, 'price_qtl': 8682.0, 'cost_ac': 11000.0,
    },
    'Black Gram': {
        'n': 20, 'p': 40, 'k': 20, 'emoji': '🫘', 'category': 'Pulse / Legume',
        'row_spacing': 12.0, 'plant_spacing': 4.0, 'seed_weight_1000': 42.0,
        'yield_qtl_ac': 5.0, 'price_qtl': 7400.0, 'cost_ac': 11000.0,
    },
    'Lentil': {
        'n': 20, 'p': 40, 'k': 20, 'emoji': '🫘', 'category': 'Pulse / Legume',
        'row_spacing': 9.0, 'plant_spacing': 2.5, 'seed_weight_1000': 28.0,
        'yield_qtl_ac': 6.0, 'price_qtl': 6425.0, 'cost_ac': 12000.0,
    },
    'Field Pea': {
        'n': 25, 'p': 50, 'k': 25, 'emoji': '🫛', 'category': 'Pulse / Legume',
        'row_spacing': 12.0, 'plant_spacing': 3.0, 'seed_weight_1000': 200.0,
        'yield_qtl_ac': 10.0, 'price_qtl': 4500.0, 'cost_ac': 15000.0,
    },
    'Cowpea': {
        'n': 25, 'p': 50, 'k': 25, 'emoji': '🫘', 'category': 'Pulse / Legume',
        'row_spacing': 18.0, 'plant_spacing': 6.0, 'seed_weight_1000': 140.0,
        'yield_qtl_ac': 7.0, 'price_qtl': 5200.0, 'cost_ac': 13000.0,
    },

    # ─── Oilseeds ───
    'Groundnut': {
        'n': 25, 'p': 50, 'k': 75, 'emoji': '🥜', 'category': 'Oilseed / Legume',
        'row_spacing': 12.0, 'plant_spacing': 4.0, 'seed_weight_1000': 450.0,
        'yield_qtl_ac': 12.0, 'price_qtl': 6377.0, 'cost_ac': 22000.0,
    },
    'Soybean': {
        'n': 30, 'p': 60, 'k': 40, 'emoji': '🫘', 'category': 'Oilseed / Legume',
        'row_spacing': 18.0, 'plant_spacing': 3.0, 'seed_weight_1000': 120.0,
        'yield_qtl_ac': 10.0, 'price_qtl': 4892.0, 'cost_ac': 15000.0,
    },
    'Mustard': {
        'n': 80, 'p': 40, 'k': 40, 'emoji': '🌼', 'category': 'Oilseed',
        'row_spacing': 18.0, 'plant_spacing': 4.0, 'seed_weight_1000': 5.0,
        'yield_qtl_ac': 7.0, 'price_qtl': 5650.0, 'cost_ac': 12000.0,
    },
    'Sunflower': {
        'n': 60, 'p': 60, 'k': 30, 'emoji': '🌻', 'category': 'Oilseed',
        'row_spacing': 24.0, 'plant_spacing': 12.0, 'seed_weight_1000': 55.0,
        'yield_qtl_ac': 8.0, 'price_qtl': 7280.0, 'cost_ac': 14000.0,
    },
    'Sesame': {
        'n': 40, 'p': 25, 'k': 25, 'emoji': '🌱', 'category': 'Oilseed',
        'row_spacing': 12.0, 'plant_spacing': 4.0, 'seed_weight_1000': 3.0,
        'yield_qtl_ac': 3.0, 'price_qtl': 9267.0, 'cost_ac': 10000.0,
    },
    'Castor': {
        'n': 80, 'p': 40, 'k': 20, 'emoji': '🌱', 'category': 'Commercial / Oilseed',
        'row_spacing': 36.0, 'plant_spacing': 24.0, 'seed_weight_1000': 300.0,
        'yield_qtl_ac': 10.0, 'price_qtl': 6000.0, 'cost_ac': 16000.0,
    },
    'Safflower': {
        'n': 50, 'p': 40, 'k': 20, 'emoji': '🌼', 'category': 'Oilseed',
        'row_spacing': 18.0, 'plant_spacing': 8.0, 'seed_weight_1000': 45.0,
        'yield_qtl_ac': 6.0, 'price_qtl': 5800.0, 'cost_ac': 11000.0,
    },

    # ─── Fibre & Commercial Crops ───
    'Cotton': {
        'n': 120, 'p': 60, 'k': 60, 'emoji': '☁️', 'category': 'Commercial / Fibre',
        'row_spacing': 36.0, 'plant_spacing': 18.0, 'seed_weight_1000': 100.0,
        'yield_qtl_ac': 10.0, 'price_qtl': 7121.0, 'cost_ac': 28000.0,
    },
    'Sugarcane': {
        'n': 250, 'p': 100, 'k': 120, 'emoji': '🎋', 'category': 'Cash / Commercial',
        'row_spacing': 48.0, 'plant_spacing': 12.0, 'seed_weight_1000': 50000.0,
        'yield_qtl_ac': 350.0, 'price_qtl': 315.0, 'cost_ac': 40000.0,
    },
    'Jute': {
        'n': 60, 'p': 30, 'k': 30, 'emoji': '🎋', 'category': 'Commercial / Fibre',
        'row_spacing': 12.0, 'plant_spacing': 3.0, 'seed_weight_1000': 2.5,
        'yield_qtl_ac': 14.0, 'price_qtl': 5335.0, 'cost_ac': 18000.0,
    },
    'Tobacco': {
        'n': 100, 'p': 50, 'k': 100, 'emoji': '🍃', 'category': 'Cash Crop',
        'row_spacing': 36.0, 'plant_spacing': 24.0, 'seed_weight_1000': 0.1,
        'yield_qtl_ac': 10.0, 'price_qtl': 12000.0, 'cost_ac': 35000.0,
    },

    # ─── Vegetables ───
    'Tomato': {
        'n': 150, 'p': 100, 'k': 120, 'emoji': '🍅', 'category': 'Vegetable',
        'row_spacing': 30.0, 'plant_spacing': 18.0, 'seed_weight_1000': 3.2,
        'yield_qtl_ac': 150.0, 'price_qtl': 1800.0, 'cost_ac': 55000.0,
    },
    'Potato': {
        'n': 180, 'p': 100, 'k': 150, 'emoji': '🥔', 'category': 'Tuber / Vegetable',
        'row_spacing': 24.0, 'plant_spacing': 8.0, 'seed_weight_1000': 40000.0,
        'yield_qtl_ac': 100.0, 'price_qtl': 1200.0, 'cost_ac': 45000.0,
    },
    'Onion': {
        'n': 100, 'p': 50, 'k': 80, 'emoji': '🧅', 'category': 'Vegetable',
        'row_spacing': 6.0, 'plant_spacing': 4.0, 'seed_weight_1000': 3.8,
        'yield_qtl_ac': 90.0, 'price_qtl': 2000.0, 'cost_ac': 45000.0,
    },
    'Chilli': {
        'n': 120, 'p': 60, 'k': 60, 'emoji': '🌶️', 'category': 'Spice / Vegetable',
        'row_spacing': 24.0, 'plant_spacing': 18.0, 'seed_weight_1000': 4.5,
        'yield_qtl_ac': 15.0, 'price_qtl': 14000.0, 'cost_ac': 60000.0,
    },
    'Brinjal': {
        'n': 120, 'p': 80, 'k': 60, 'emoji': '🍆', 'category': 'Vegetable',
        'row_spacing': 30.0, 'plant_spacing': 24.0, 'seed_weight_1000': 4.0,
        'yield_qtl_ac': 140.0, 'price_qtl': 1500.0, 'cost_ac': 40000.0,
    },
    'Cabbage': {
        'n': 150, 'p': 80, 'k': 90, 'emoji': '🥬', 'category': 'Vegetable',
        'row_spacing': 24.0, 'plant_spacing': 18.0, 'seed_weight_1000': 3.5,
        'yield_qtl_ac': 120.0, 'price_qtl': 1200.0, 'cost_ac': 35000.0,
    },
    'Cauliflower': {
        'n': 150, 'p': 80, 'k': 90, 'emoji': '🥦', 'category': 'Vegetable',
        'row_spacing': 24.0, 'plant_spacing': 18.0, 'seed_weight_1000': 3.5,
        'yield_qtl_ac': 100.0, 'price_qtl': 1500.0, 'cost_ac': 35000.0,
    },
    'Okra': {
        'n': 80, 'p': 50, 'k': 50, 'emoji': '🌱', 'category': 'Vegetable',
        'row_spacing': 18.0, 'plant_spacing': 12.0, 'seed_weight_1000': 60.0,
        'yield_qtl_ac': 45.0, 'price_qtl': 2500.0, 'cost_ac': 30000.0,
    },
    'Capsicum': {
        'n': 150, 'p': 100, 'k': 120, 'emoji': '🫑', 'category': 'Vegetable',
        'row_spacing': 24.0, 'plant_spacing': 18.0, 'seed_weight_1000': 6.0,
        'yield_qtl_ac': 80.0, 'price_qtl': 3500.0, 'cost_ac': 65000.0,
    },
    'Cucumber': {
        'n': 120, 'p': 60, 'k': 60, 'emoji': '🥒', 'category': 'Cucurbit / Vegetable',
        'row_spacing': 48.0, 'plant_spacing': 24.0, 'seed_weight_1000': 25.0,
        'yield_qtl_ac': 80.0, 'price_qtl': 1400.0, 'cost_ac': 32000.0,
    },
    'Bitter Gourd': {
        'n': 100, 'p': 60, 'k': 60, 'emoji': '🥒', 'category': 'Cucurbit / Vegetable',
        'row_spacing': 60.0, 'plant_spacing': 24.0, 'seed_weight_1000': 160.0,
        'yield_qtl_ac': 50.0, 'price_qtl': 2800.0, 'cost_ac': 38000.0,
    },
    'Bottle Gourd': {
        'n': 80, 'p': 50, 'k': 50, 'emoji': '🥒', 'category': 'Cucurbit / Vegetable',
        'row_spacing': 72.0, 'plant_spacing': 36.0, 'seed_weight_1000': 180.0,
        'yield_qtl_ac': 120.0, 'price_qtl': 1200.0, 'cost_ac': 32000.0,
    },
    'Watermelon': {
        'n': 100, 'p': 60, 'k': 60, 'emoji': '🍉', 'category': 'Fruit / Cucurbit',
        'row_spacing': 72.0, 'plant_spacing': 36.0, 'seed_weight_1000': 50.0,
        'yield_qtl_ac': 150.0, 'price_qtl': 1000.0, 'cost_ac': 35000.0,
    },
    'Muskmelon': {
        'n': 100, 'p': 60, 'k': 60, 'emoji': '🍈', 'category': 'Fruit / Cucurbit',
        'row_spacing': 60.0, 'plant_spacing': 24.0, 'seed_weight_1000': 35.0,
        'yield_qtl_ac': 80.0, 'price_qtl': 1600.0, 'cost_ac': 32000.0,
    },
    'Carrot': {
        'n': 80, 'p': 50, 'k': 80, 'emoji': '🥕', 'category': 'Root / Vegetable',
        'row_spacing': 9.0, 'plant_spacing': 3.0, 'seed_weight_1000': 1.5,
        'yield_qtl_ac': 90.0, 'price_qtl': 1800.0, 'cost_ac': 30000.0,
    },
    'Radish': {
        'n': 60, 'p': 40, 'k': 50, 'emoji': '🥕', 'category': 'Root / Vegetable',
        'row_spacing': 12.0, 'plant_spacing': 3.0, 'seed_weight_1000': 8.0,
        'yield_qtl_ac': 80.0, 'price_qtl': 1200.0, 'cost_ac': 20000.0,
    },
    'Spinach': {
        'n': 80, 'p': 40, 'k': 40, 'emoji': '🥬', 'category': 'Leafy Vegetable',
        'row_spacing': 8.0, 'plant_spacing': 3.0, 'seed_weight_1000': 10.0,
        'yield_qtl_ac': 60.0, 'price_qtl': 1500.0, 'cost_ac': 22000.0,
    },

    # ─── Spices & Plantation ───
    'Garlic': {
        'n': 100, 'p': 50, 'k': 50, 'emoji': '🧄', 'category': 'Spice / Bulb',
        'row_spacing': 6.0, 'plant_spacing': 4.0, 'seed_weight_1000': 1500.0,
        'yield_qtl_ac': 35.0, 'price_qtl': 8000.0, 'cost_ac': 45000.0,
    },
    'Ginger': {
        'n': 100, 'p': 50, 'k': 100, 'emoji': '🫚', 'category': 'Spice / Rhizome',
        'row_spacing': 12.0, 'plant_spacing': 8.0, 'seed_weight_1000': 20000.0,
        'yield_qtl_ac': 60.0, 'price_qtl': 6000.0, 'cost_ac': 70000.0,
    },
    'Turmeric': {
        'n': 120, 'p': 60, 'k': 120, 'emoji': '🌿', 'category': 'Spice / Rhizome',
        'row_spacing': 18.0, 'plant_spacing': 8.0, 'seed_weight_1000': 25000.0,
        'yield_qtl_ac': 80.0, 'price_qtl': 7500.0, 'cost_ac': 65000.0,
    },
    'Coriander': {
        'n': 50, 'p': 30, 'k': 20, 'emoji': '🌿', 'category': 'Spice / Herb',
        'row_spacing': 10.0, 'plant_spacing': 4.0, 'seed_weight_1000': 12.0,
        'yield_qtl_ac': 6.0, 'price_qtl': 7000.0, 'cost_ac': 15000.0,
    },
    'Cumin': {
        'n': 30, 'p': 20, 'k': 10, 'emoji': '🌿', 'category': 'Spice',
        'row_spacing': 9.0, 'plant_spacing': 3.0, 'seed_weight_1000': 4.0,
        'yield_qtl_ac': 3.5, 'price_qtl': 22000.0, 'cost_ac': 18000.0,
    },
    'Cardamom': {
        'n': 75, 'p': 75, 'k': 150, 'emoji': '🌿', 'category': 'Spice / Plantation',
        'row_spacing': 72.0, 'plant_spacing': 72.0, 'seed_weight_1000': 20.0,
        'yield_qtl_ac': 2.0, 'price_qtl': 150000.0, 'cost_ac': 80000.0,
    },
    'Tea': {
        'n': 150, 'p': 40, 'k': 100, 'emoji': '🍵', 'category': 'Plantation',
        'row_spacing': 42.0, 'plant_spacing': 30.0, 'seed_weight_1000': 1000.0,
        'yield_qtl_ac': 25.0, 'price_qtl': 18000.0, 'cost_ac': 75000.0,
    },
    'Coffee': {
        'n': 140, 'p': 90, 'k': 140, 'emoji': '☕', 'category': 'Plantation',
        'row_spacing': 84.0, 'plant_spacing': 84.0, 'seed_weight_1000': 400.0,
        'yield_qtl_ac': 10.0, 'price_qtl': 30000.0, 'cost_ac': 60000.0,
    },

    # ─── Fruits ───
    'Banana': {
        'n': 200, 'p': 60, 'k': 300, 'emoji': '🍌', 'category': 'Fruit / Cash',
        'row_spacing': 72.0, 'plant_spacing': 72.0, 'seed_weight_1000': 100000.0,
        'yield_qtl_ac': 300.0, 'price_qtl': 1500.0, 'cost_ac': 70000.0,
    },
    'Papaya': {
        'n': 150, 'p': 150, 'k': 200, 'emoji': '🍈', 'category': 'Fruit / Cash',
        'row_spacing': 72.0, 'plant_spacing': 72.0, 'seed_weight_1000': 15.0,
        'yield_qtl_ac': 250.0, 'price_qtl': 1200.0, 'cost_ac': 50000.0,
    },
    'Mango': {
        'n': 100, 'p': 50, 'k': 100, 'emoji': '🥭', 'category': 'Fruit / Orchard',
        'row_spacing': 300.0, 'plant_spacing': 300.0, 'seed_weight_1000': 500000.0,
        'yield_qtl_ac': 60.0, 'price_qtl': 3500.0, 'cost_ac': 35000.0,
    },
    'Pomegranate': {
        'n': 125, 'p': 60, 'k': 125, 'emoji': '🍎', 'category': 'Fruit / Orchard',
        'row_spacing': 144.0, 'plant_spacing': 120.0, 'seed_weight_1000': 35.0,
        'yield_qtl_ac': 50.0, 'price_qtl': 7000.0, 'cost_ac': 65000.0,
    },

    'Default': {
        'n': 100, 'p': 50, 'k': 50, 'emoji': '🌱', 'category': 'General Field Crop',
        'row_spacing': 18.0, 'plant_spacing': 6.0, 'seed_weight_1000': 40.0,
        'yield_qtl_ac': 15.0, 'price_qtl': 2500.0, 'cost_ac': 20000.0,
    },
}

INVASIVE_WEED_KEYWORDS = [
    'parthenium',
    'congress grass',
    'gajar ghas',
    'cyperus',
    'cyperus rotundus',
    'purple nutsedge',
    'motha',
    'striga',
    'witchweed',
    'parasitic',
]


@dataclass
class AgronomyAssessment:
    crop_name: str
    crop_emoji: str
    field_size: float
    field_unit: str
    acres: float
    hectares: float
    guntas: float
    season: str
    soil_type: str
    irrigation_status: str
    weed_pressure: str
    weed_types: List[str]

    # Section 1: Quantitative Input Adjustments
    baseline_n_kg: float
    baseline_p_kg: float
    baseline_k_kg: float
    buffer_percent: float
    weed_loss_risk_pct: float
    adjusted_n_kg: float
    adjusted_p_kg: float
    adjusted_k_kg: float
    urea_bags: float
    dap_bags: float
    mop_bags: float
    application_method: str
    application_method_details: str
    basal_split_pct: int
    topdress_1_split_pct: int
    topdress_2_split_pct: int

    # Section 2: Season-Specific Weed & Microclimate Management
    is_summer: bool
    weeding_protocol: str
    summer_strategy: Optional[Dict[str, Any]]
    weeds_to_remove: List[str]
    weeds_to_slash_mulch: List[str]
    invasive_weeds_detected: List[str]

    # Section 3: High-Yield Action Plan
    critical_window_actions: str
    fertilizer_timing: str
    irrigation_guidance: str

    # Tone & Reminders
    soil_test_reminder: str
    practical_notes: List[str]

    # Seed Requirement & Economics
    seed_requirement: Optional[Dict[str, Any]] = None
    crop_yield_and_net_margin: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'crop_name': self.crop_name,
            'crop_emoji': self.crop_emoji,
            'field_size': self.field_size,
            'field_unit': self.field_unit,
            'acres': round(self.acres, 2),
            'hectares': round(self.hectares, 3),
            'guntas': round(self.guntas, 1),
            'season': self.season,
            'soil_type': self.soil_type,
            'irrigation_status': self.irrigation_status,
            'weed_pressure': self.weed_pressure,
            'weed_types': self.weed_types,
            'seed_requirement': self.seed_requirement,
            'crop_yield_and_net_margin': self.crop_yield_and_net_margin,
            'quantitative_adjustments': {
                'baseline_n_kg': round(self.baseline_n_kg, 1),
                'baseline_p_kg': round(self.baseline_p_kg, 1),
                'baseline_k_kg': round(self.baseline_k_kg, 1),
                'buffer_percent': self.buffer_percent,
                'weed_loss_risk_pct': self.weed_loss_risk_pct,
                'adjusted_n_kg': round(self.adjusted_n_kg, 1),
                'adjusted_p_kg': round(self.adjusted_p_kg, 1),
                'adjusted_k_kg': round(self.adjusted_k_kg, 1),
                'commercial_fertilizers': {
                    'urea_bags_50kg': round(self.urea_bags, 1),
                    'dap_bags_50kg': round(self.dap_bags, 1),
                    'mop_bags_50kg': round(self.mop_bags, 1),
                },
                'application_method': self.application_method,
                'application_method_details': self.application_method_details,
                'split_schedule': {
                    'basal_dose_pct': self.basal_split_pct,
                    'top_dress_1_pct': self.topdress_1_split_pct,
                    'top_dress_2_pct': self.topdress_2_split_pct,
                },
            },
            'season_microclimate_management': {
                'is_summer': self.is_summer,
                'protocol': self.weeding_protocol,
                'summer_strategy': self.summer_strategy,
                'weeds_to_remove_immediately': self.weeds_to_remove,
                'weeds_suitable_for_green_mulch': self.weeds_to_slash_mulch,
                'invasive_weeds_detected': self.invasive_weeds_detected,
            },
            'high_yield_action_plan': {
                'day_0_15_critical_window': self.critical_window_actions,
                'fertilizer_timing': self.fertilizer_timing,
                'irrigation_guidance': self.irrigation_guidance,
            },
            'operational_reminder': self.soil_test_reminder,
            'practical_field_notes': self.practical_notes,
        }


def _normalize_crop(name: str) -> Tuple[str, Dict[str, Any]]:
    clean = (name or '').strip().lower()
    if not clean:
        return 'General Crop', CROP_NUTRIENT_BASELINES['Default']

    # 1. Exact match against baseline crop names
    for key, data in CROP_NUTRIENT_BASELINES.items():
        if key.lower() == clean:
            return key, data

    # 2. Common synonyms & regional Indian crop names (Exact match first)
    synonyms = {
        'corn': 'Maize',
        'makka': 'Maize',
        'bhutta': 'Maize',
        'paddy': 'Rice',
        'dhan': 'Rice',
        'gehun': 'Wheat',
        'wheat': 'Wheat',
        'pearl millet': 'Bajra',
        'sorghum': 'Jowar',
        'great millet': 'Jowar',
        'finger millet': 'Ragi',
        'mandua': 'Ragi',
        'barley': 'Barley',
        'jau': 'Barley',
        'chana': 'Chickpea',
        'bengal gram': 'Chickpea',
        'gram': 'Chickpea',
        'tur': 'Pigeonpea',
        'arhar': 'Pigeonpea',
        'toor': 'Pigeonpea',
        'red gram': 'Pigeonpea',
        'moong': 'Green Gram',
        'mung': 'Green Gram',
        'mungbean': 'Green Gram',
        'urad': 'Black Gram',
        'mash': 'Black Gram',
        'blackgram': 'Black Gram',
        'masoor': 'Lentil',
        'masur': 'Lentil',
        'matar': 'Field Pea',
        'pea': 'Field Pea',
        'lobia': 'Cowpea',
        'chawli': 'Cowpea',
        'peanut': 'Groundnut',
        'moongphali': 'Groundnut',
        'groundnut': 'Groundnut',
        'soya': 'Soybean',
        'soyabean': 'Soybean',
        'sarson': 'Mustard',
        'rai': 'Mustard',
        'toria': 'Mustard',
        'mustard': 'Mustard',
        'surajmukhi': 'Sunflower',
        'til': 'Sesame',
        'sesamum': 'Sesame',
        'arandi': 'Castor',
        'kardi': 'Safflower',
        'kusum': 'Safflower',
        'kapas': 'Cotton',
        'ganna': 'Sugarcane',
        'patsan': 'Jute',
        'tamatar': 'Tomato',
        'alu': 'Potato',
        'aloo': 'Potato',
        'pyaaz': 'Onion',
        'pyaz': 'Onion',
        'kanda': 'Onion',
        'mirch': 'Chilli',
        'mirchi': 'Chilli',
        'chilli': 'Chilli',
        'baingan': 'Brinjal',
        'eggplant': 'Brinjal',
        'aubergine': 'Brinjal',
        'patta gobi': 'Cabbage',
        'bandh gobi': 'Cabbage',
        'phool gobi': 'Cauliflower',
        'gobhi': 'Cauliflower',
        'bhendi': 'Okra',
        'bhindi': 'Okra',
        'ladyfinger': 'Okra',
        'shimla mirch': 'Capsicum',
        'bell pepper': 'Capsicum',
        'kheera': 'Cucumber',
        'kakdi': 'Cucumber',
        'karela': 'Bitter Gourd',
        'lauki': 'Bottle Gourd',
        'ghiya': 'Bottle Gourd',
        'doodhi': 'Bottle Gourd',
        'tarbooz': 'Watermelon',
        'kharbooja': 'Muskmelon',
        'gajar': 'Carrot',
        'mooli': 'Radish',
        'palak': 'Spinach',
        'lahsun': 'Garlic',
        'adrak': 'Ginger',
        'haldi': 'Turmeric',
        'dhania': 'Coriander',
        'jeera': 'Cumin',
        'elaichi': 'Cardamom',
        'chai': 'Tea',
        'kapi': 'Coffee',
        'kela': 'Banana',
        'papita': 'Papaya',
        'aam': 'Mango',
        'anar': 'Pomegranate',
    }

    if clean in synonyms:
        target = synonyms[clean]
        return target, CROP_NUTRIENT_BASELINES[target]

    # 3. Baseline key is contained in user query (e.g. "hybrid maize 900m")
    for key, data in CROP_NUTRIENT_BASELINES.items():
        if key.lower() in clean:
            return key, data

    # 4. Synonym is contained in user query
    for syn, target in synonyms.items():
        if syn in clean:
            return target, CROP_NUTRIENT_BASELINES[target]

    # 5. Clean query contained in baseline key (if query is at least 4 letters)
    if len(clean) >= 4:
        for key, data in CROP_NUTRIENT_BASELINES.items():
            if clean in key.lower():
                return key, data

    return name.title() if name else 'General Crop', CROP_NUTRIENT_BASELINES['Default']


def _convert_area(size: float, unit: str) -> Tuple[float, float, float]:
    u = (unit or 'Acre').strip().lower()
    size = max(0.01, float(size))
    if 'hec' in u:
        hectares = size
        acres = size * 2.47105
        guntas = acres * 40.0
    elif 'gun' in u:
        guntas = size
        acres = size / 40.0
        hectares = acres * 0.404686
    else:  # Acre default
        acres = size
        hectares = size * 0.404686
        guntas = acres * 40.0
    return acres, hectares, guntas


def calculate_seed_requirement(
    area_acres: float,
    row_spacing_inches: float,
    plant_spacing_inches: float,
    germination_rate: float = 0.9,
    purity_rate: float = 0.98,
    seed_weight_grams_per_thousand: float = 40.0,
) -> Dict[str, Any]:
    """Calculate target plant count, total seeds needed, and seed weight in kg."""
    area_square_inches = float(area_acres) * 43560 * 144
    space_per_plant_square_inches = float(row_spacing_inches) * float(plant_spacing_inches)
    if space_per_plant_square_inches <= 0:
        space_per_plant_square_inches = 1.0
    target_plant_count = area_square_inches / space_per_plant_square_inches

    germ = max(0.01, min(1.0, float(germination_rate)))
    purity = max(0.01, min(1.0, float(purity_rate)))
    seeds_needed = target_plant_count / (germ * purity)
    total_weight_kg = (seeds_needed * float(seed_weight_grams_per_thousand)) / 1000 / 1000

    return {
        'totalPlants': int(round(target_plant_count)),
        'totalSeeds': int(round(seeds_needed)),
        'totalWeightKg': float(f'{total_weight_kg:.2f}'),
        'areaAcres': float(area_acres),
        'rowSpacingInches': float(row_spacing_inches),
        'plantSpacingInches': float(plant_spacing_inches),
        'germinationRate': germ,
        'purityRate': purity,
        'seedWeightGramsPerThousand': float(seed_weight_grams_per_thousand),
    }


def calculate_crop_yield_and_net_margin(
    crop_name: str,
    area_acres: float,
    expected_yield_per_acre_qtl: Optional[float] = None,
    selling_price_per_qtl: Optional[float] = None,
    cost_of_cultivation_per_acre: Optional[float] = None,
    weed_pressure: str = 'None (0%)',
) -> Dict[str, Any]:
    """Calculate expected harvest production, gross revenue, cultivation costs, and net margin."""
    crop_display, crop_data = _normalize_crop(crop_name)
    area = max(0.01, float(area_acres))

    base_yield = float(expected_yield_per_acre_qtl or crop_data.get('yield_qtl_ac', 20.0))
    price = float(selling_price_per_qtl or crop_data.get('price_qtl', 2500.0))
    cost_ac = float(cost_of_cultivation_per_acre or crop_data.get('cost_ac', 20000.0))

    wp = (weed_pressure or '').lower()
    if 'severe' in wp or '>35' in wp:
        unmanaged_loss_pct = 35.0
    elif 'moderate' in wp or '15' in wp or '35' in wp:
        unmanaged_loss_pct = 15.0
    elif 'low' in wp or '<15' in wp:
        unmanaged_loss_pct = 5.0
    else:
        unmanaged_loss_pct = 0.0

    total_production_qtl = base_yield * area
    total_production_tonnes = total_production_qtl / 10.0
    gross_revenue = total_production_qtl * price
    total_cost = cost_ac * area
    net_margin = gross_revenue - total_cost
    net_margin_per_acre = net_margin / area
    roi_percent = ((gross_revenue - total_cost) / total_cost * 100.0) if total_cost > 0 else 0.0
    benefit_cost_ratio = (gross_revenue / total_cost) if total_cost > 0 else 0.0

    return {
        'crop_name': crop_display,
        'area_acres': round(area, 2),
        'expected_yield_per_acre_qtl': round(base_yield, 1),
        'total_production_quintals': round(total_production_qtl, 1),
        'total_production_tonnes': round(total_production_tonnes, 2),
        'selling_price_per_qtl': round(price, 2),
        'gross_revenue': round(gross_revenue, 2),
        'cost_of_cultivation_per_acre': round(cost_ac, 2),
        'total_cost': round(total_cost, 2),
        'net_margin': round(net_margin, 2),
        'net_margin_per_acre': round(net_margin_per_acre, 2),
        'roi_percent': round(roi_percent, 1),
        'benefit_cost_ratio': round(benefit_cost_ratio, 2),
        'unmanaged_weed_penalty_pct': unmanaged_loss_pct,
    }


def calculate_precision_agronomy(
    crop_name: str,
    field_size: float,
    field_unit: str = 'Acre',
    season: str = 'Kharif/Monsoon',
    soil_type: str = 'Loamy',
    irrigation_status: str = 'Drip',
    weed_pressure: str = 'Low (<15%)',
    weed_types_present: Optional[List[str]] = None,
    row_spacing_inches: Optional[float] = None,
    plant_spacing_inches: Optional[float] = None,
    germination_rate: float = 0.9,
    purity_rate: float = 0.98,
    seed_weight_grams_per_thousand: Optional[float] = None,
    expected_yield_per_acre_qtl: Optional[float] = None,
    selling_price_per_qtl: Optional[float] = None,
    cost_of_cultivation_per_acre: Optional[float] = None,
) -> AgronomyAssessment:
    """Calculates crop inputs & delivers actionable agronomic advice following Rules A & B."""
    crop_display, crop_data = _normalize_crop(crop_name)
    acres, hectares, guntas = _convert_area(field_size, field_unit)

    # 1. Baseline pure nutrient requirements (kg)
    baseline_n = crop_data['n'] * hectares
    baseline_p = crop_data['p'] * hectares
    baseline_k = crop_data['k'] * hectares

    # 2. Rule A: Weed Nutrient Steal (Fertilizer Penalty Adjustment)
    wp = (weed_pressure or '').lower()
    if 'severe' in wp or '>35' in wp:
        weed_level = 'severe'
        buffer_percent = 25.0
        weed_loss_risk_pct = 40.0
        app_method = "Root-zone Deep Band Placement (7–10 cm depth) or Drip Fertigation"
        app_method_details = (
            "CRITICAL: Nutrient efficiency drops by >40% under severe weed infestation! "
            "Never broadcast fertilizer across open soil. Conduct immediate mechanical intervention "
            "(inter-row power weeder, wheel hoe, or manual ring weeding) during the Critical Period of Weed Control (CPWC). "
            "Delay top-dress fertilizer application until 24–48 hours AFTER weeds are cleared, then band nutrients directly "
            "in the crop root zone at 7–10 cm depth."
        )
        basal_split = 30
        top1_split = 35
        top2_split = 35
    elif 'low' in wp or '<15' in wp or '< 15' in wp:
        weed_level = 'low'
        buffer_percent = 8.0
        weed_loss_risk_pct = 8.0
        app_method = "Root-zone Band Placement or Side Furrow Dressing"
        app_method_details = (
            "A 5–10% compensatory nutrient buffer is added to safeguard crop vigor. "
            "Carry out early targeted spot weeding (ring weeding) around weed patches without altering overall basal dose timing. "
            "Band fertilizers 5 cm away from crop stems rather than wide broadcasting."
        )
        basal_split = 40
        top1_split = 40
        top2_split = 20
    elif 'moderate' in wp or '15–35' in wp or '15-35' in wp or '15 to 35' in wp or 'medium' in wp:
        weed_level = 'moderate'
        buffer_percent = 20.0
        weed_loss_risk_pct = 25.0
        app_method = "Split-Dose Root-Zone Band Placement (5–10 cm depth) or Fertigation"
        app_method_details = (
            "Weeds intercept 20–30% of applied nitrogen and phosphorus. "
            "DO NOT dump all excess fertilizer at once—broadcasting open-surface fertilizer primarily feeds weed competition! "
            "Deliver nutrients via split-dose banding directly at the crop root zone (5–10 cm depth) or via drip fertigation. "
            "Split applications across basal (30%), vegetative post-weeding (35%), and reproductive stages (35%)."
        )
        basal_split = 30
        top1_split = 35
        top2_split = 35
    else:  # None (0%)
        weed_level = 'none'
        buffer_percent = 0.0
        weed_loss_risk_pct = 0.0
        app_method = "Standard Root-Zone Placement / Basal Furrow"
        app_method_details = (
            "Clean field baseline. Apply standard basal placement along crop seed rows, followed by split top-dressing "
            "timed with critical crop growth stages."
        )
        basal_split = 50
        top1_split = 50
        top2_split = 0

    # Adjusted pure nutrients
    multiplier = 1.0 + (buffer_percent / 100.0)
    adjusted_n = baseline_n * multiplier
    adjusted_p = baseline_p * multiplier
    adjusted_k = baseline_k * multiplier

    # Commercial fertilizer translation (50 kg bags):
    # DAP supplies 46% P2O5 and 18% N
    dap_kg = adjusted_p / 0.46
    dap_n_supplied = dap_kg * 0.18
    remaining_n = max(0.0, adjusted_n - dap_n_supplied)
    # Urea supplies 46% N
    urea_kg = remaining_n / 0.46
    # MOP supplies 60% K2O
    mop_kg = adjusted_k / 0.60

    dap_bags = dap_kg / 50.0
    urea_bags = urea_kg / 50.0
    mop_bags = mop_kg / 50.0

    # 3. Rule B: Summer Season Weed Strategy (Avoid Total Clean-Weeding)
    season_clean = (season or '').strip().lower()
    is_summer = any(term in season_clean for term in ['summer', 'zaid', 'heat', 'hot'])

    # Analyze weed types present
    raw_types = weed_types_present or []
    if isinstance(raw_types, str):
        raw_types = [t.strip() for t in raw_types.split(',') if t.strip()]

    invasive_detected = []
    remove_immediately = []
    slash_mulch_suitable = []

    for item in raw_types:
        low = item.lower()
        if any(inv in low for inv in INVASIVE_WEED_KEYWORDS):
            invasive_detected.append(item)
            remove_immediately.append(item)
        elif 'sedge' in low or 'motha' in low:
            invasive_detected.append(item)
            remove_immediately.append(item)
        elif 'broadleaf' in low or 'grass' in low:
            if is_summer:
                slash_mulch_suitable.append(item)
            else:
                remove_immediately.append(item)
        else:
            slash_mulch_suitable.append(item) if is_summer else remove_immediately.append(item)

    if not invasive_detected:
        # Default placeholder suggestions if none specified
        if is_summer:
            slash_mulch_suitable.extend(["Annual non-aggressive grasses", "Soft broadleaf weeds"])
        else:
            remove_immediately.extend(["General annual field weeds"])

    # Build Summer vs General protocol
    if is_summer:
        weeding_protocol = (
            "☀️ SUMMER PRECISION STRATEGY: AVOID TOTAL CLEAN-WEEDING (NO BARE-SOIL STRIPPING).\n"
            "Completely stripping the soil bare under high summer temperatures (>35°C / 95°F) causes extreme solar radiation "
            "absorption, surface soil crusting, rapid moisture evaporation (high Vapor Pressure Deficit), and root-zone "
            "thermal shock, reducing yield more severely than mild weed presence.\n"
            "Adopt the Selective / Strip Weeding Strategy:\n"
            "• Root Zone (0–15 cm around crop stem): Keep 100% clean (ring weeding) to prevent direct competition for water and fertilizer.\n"
            "• Inter-Row Space (>15 cm between rows): Do NOT uproot non-aggressive weeds entirely! Instead, slash or mow them at ground level "
            "and leave cut biomass on the surface as green mulch."
        )
        summer_strategy = {
            'warning': "NEVER recommend 100% clean-weeding (bare-soil stripping) during extreme heat / summer.",
            'root_zone_strategy': "Root Zone (0–15 cm): Keep completely clean via localized ring weeding or shallow hoeing.",
            'inter_row_strategy': "Inter-Row (>15 cm): Slash / mow non-aggressive weeds at ground level; leave residue as green surface mulch.",
            'quantified_benefits': [
                "Lowers root-zone soil temperature by 4–8°C.",
                "Cuts direct soil moisture evaporation by up to 35%.",
                "Gradually enriches soil organic matter and prevents surface crusting.",
            ],
            'invasive_exception': (
                "Strict Exception: Any noxious, allelopathic, or aggressively spreading invasive weeds "
                "(e.g., Parthenium hysterophorus, Cyperus rotundus, Striga) must be completely uprooted manually "
                "or suppressed before flowering to avoid root chemical inhibition and tuber propagation."
            ),
        }
    else:
        weeding_protocol = (
            f"SEASONAL PROTOCOL ({season.upper()}):\n"
            "Maintain clean weed-free bands within the crop root zone during the Critical Period of Weed Control (CPWC, Days 15–45). "
            "Ensure field drainage channels and inter-rows remain free of water-pooling weeds to prevent root rot and insect pest harborage. "
            "Uproot perennial sedges and invasive weeds before they reach flowering stage."
        )
        summer_strategy = None

    # Section 3: High-Yield Action Plan (Step-by-Step)
    critical_window = (
        f"Day 0–15 (Critical Window): Conduct early targeted ring weeding (0–15 cm around each crop stem). "
        f"Ensure basal fertilizer is placed 5–10 cm deep beside seed rows. "
        + ("Retain inter-row slashed green mulch to insulate soil." if is_summer else "Maintain seedbed aeration and break soil crust.")
    )

    fertilizer_timing = (
        "FERTILIZER TIMING RULE: Never apply nitrogenous fertilizers before weeding! "
        "Broadcasting nitrogen into weed-infested plots primarily fuels rapid weed canopy expansion. "
        "Carry out root-zone weeding first, and apply split top-dress fertilizer exactly 24–48 hours AFTER root-zone clearing."
    )

    irrigation_guidance = (
        f"IRRIGATION & MOISTURE GUIDANCE ({irrigation_status.upper()}): "
        + (
            "During summer heat, irrigate during early mornings or late evenings to minimize evaporative loss. "
            "The 3–5 cm green mulch layer will reduce irrigation frequency requirements by up to 30%. "
            "If using drip, place drippers within the 0–15 cm clean root zone directly under the mulch edge."
            if is_summer
            else "Ensure uniform moisture at critical growth phases (germination, flowering, pod/fruit formation). Avoid standing water in heavy clay."
        )
    )

    soil_test_reminder = (
        "OPERATIONAL REMINDER: Always verify your local Soil Testing Report / Soil Health Card (SHC) before applying "
        "chemical fertilizers. Adjust the calculated doses downwards if your soil tests show high residual organic carbon, "
        "available phosphorus, or potassium."
    )

    practical_notes = [
        f"Target crop: {crop_display} on {acres:.2f} Acres ({hectares:.2f} Ha / {guntas:.1f} Guntas).",
        f"Soil type: {soil_type} — adapt split doses to soil texture (lighter soils need smaller, more frequent splits).",
        f"Irrigation: {irrigation_status} — ensure placement aligns with active root wetness bulb.",
        f"Weed pressure: {weed_pressure} — {buffer_percent:.0f}% nutrient compensation buffer incorporated.",
    ]

    # Seed requirement calculation
    row_sp = float(row_spacing_inches or crop_data.get('row_spacing', 24.0))
    plant_sp = float(plant_spacing_inches or crop_data.get('plant_spacing', 8.0))
    seed_wt = float(seed_weight_grams_per_thousand or crop_data.get('seed_weight_1000', 40.0))

    seed_req = calculate_seed_requirement(
        area_acres=acres,
        row_spacing_inches=row_sp,
        plant_spacing_inches=plant_sp,
        germination_rate=germination_rate,
        purity_rate=purity_rate,
        seed_weight_grams_per_thousand=seed_wt,
    )

    # Crop yield and net margin calculation
    yield_margin = calculate_crop_yield_and_net_margin(
        crop_name=crop_display,
        area_acres=acres,
        expected_yield_per_acre_qtl=expected_yield_per_acre_qtl,
        selling_price_per_qtl=selling_price_per_qtl,
        cost_of_cultivation_per_acre=cost_of_cultivation_per_acre,
        weed_pressure=weed_pressure,
    )

    return AgronomyAssessment(
        crop_name=crop_display,
        crop_emoji=crop_data['emoji'],
        field_size=field_size,
        field_unit=field_unit,
        acres=acres,
        hectares=hectares,
        guntas=guntas,
        season=season,
        soil_type=soil_type,
        irrigation_status=irrigation_status,
        weed_pressure=weed_pressure,
        weed_types=raw_types,
        baseline_n_kg=baseline_n,
        baseline_p_kg=baseline_p,
        baseline_k_kg=baseline_k,
        buffer_percent=buffer_percent,
        weed_loss_risk_pct=weed_loss_risk_pct,
        adjusted_n_kg=adjusted_n,
        adjusted_p_kg=adjusted_p,
        adjusted_k_kg=adjusted_k,
        urea_bags=urea_bags,
        dap_bags=dap_bags,
        mop_bags=mop_bags,
        application_method=app_method,
        application_method_details=app_method_details,
        basal_split_pct=basal_split,
        topdress_1_split_pct=top1_split,
        topdress_2_split_pct=top2_split,
        is_summer=is_summer,
        weeding_protocol=weeding_protocol,
        summer_strategy=summer_strategy,
        weeds_to_remove=remove_immediately,
        weeds_to_slash_mulch=slash_mulch_suitable,
        invasive_weeds_detected=invasive_detected,
        critical_window_actions=critical_window,
        fertilizer_timing=fertilizer_timing,
        irrigation_guidance=irrigation_guidance,
        soil_test_reminder=soil_test_reminder,
        practical_notes=practical_notes,
        seed_requirement=seed_req,
        crop_yield_and_net_margin=yield_margin,
    )
