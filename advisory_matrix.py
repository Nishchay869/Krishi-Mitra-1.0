"""
Advisory Matrix: Integrated Pest Management (IPM) Decision Engine
Precision Agronomy rule base mapping multi-class plant leaf pathogens and insect pests
across Stage 1 (Early / Trace), Stage 2 (Moderate), and Stage 3 (Severe / Critical).

Strictly enforces biological, preventative, and low-toxicity botanical chemistries
during Stage 1, escalating to systemic synthetics only for Stage 2/3.
"""

from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field


class SeverityStage(str, Enum):
    STAGE_1 = "Stage 1 (Early / Trace)"
    STAGE_2 = "Stage 2 (Moderate)"
    STAGE_3 = "Stage 3 (Severe / Critical)"


class TargetCategory(str, Enum):
    PATHOGEN = "pathogen"
    PEST = "pest"


class IPMRecommendation(BaseModel):
    """Data payload for actionable agronomic and chemical intervention."""
    target_name: str = Field(..., description="Common name of diagnosed disease pathogen or pest species")
    scientific_name: str = Field(..., description="Binomial nomenclature of causal organism")
    category: TargetCategory = Field(..., description="Pathogen (fungal/bacterial) or Arthropod pest")
    severity_stage: SeverityStage = Field(..., description="Agronomic severity classification")
    
    # Chemistry / Bio-agent specifications
    active_agent: str = Field(..., description="Active chemical molecule or biological biocontrol strain")
    formulation: str = Field(..., description="Formulation code: WP (Wettable Powder), EC, SC, SL, etc.")
    dilution_rate: str = Field(..., description="Human-readable dilution rate per liter of water")
    dilution_numeric: float = Field(..., description="Numeric dose value for tank calculators")
    dilution_unit: str = Field(..., description="Measurement unit ('g/L' or 'ml/L')")
    
    # Application Engineering
    application_method: str = Field(..., description="Technique: foliar underside misting, root drench, etc.")
    nozzle_type: str = Field(..., description="Recommended spray nozzle tip and pressure setting")
    phi_days: int = Field(..., description="Pre-Harvest Interval (PHI) in days before safe harvest")
    buffer_hours: int = Field(..., description="Worker re-entry interval (REI) buffer in hours")
    
    # Agronomic Strategy & Bio-stewardship
    strategy_type: str = Field(..., description="Biological Prophylactic, Botanical Contact, or Systemic")
    tank_mix_compatibility: str = Field(..., description="Tank mixing instructions, surfactants, and incompatibilities")
    action_plan_summary: str = Field(..., description="Step-by-step field execution protocol for the farmer")


# ============================================================================
# COMPREHENSIVE ADVISORY MATRIX DICTIONARY
# ============================================================================

ADVISORY_MATRIX: Dict[str, Dict[SeverityStage, IPMRecommendation]] = {

    # ------------------------------------------------------------------------
    # 1. EARLY BLIGHT (Alternaria solani)
    # ------------------------------------------------------------------------
    "Early Blight": {
        SeverityStage.STAGE_1: IPMRecommendation(
            target_name="Early Blight",
            scientific_name="Alternaria solani",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_1,
            active_agent="Bacillus subtilis (Strain QST 713 / minimum 1x10^9 CFU/g)",
            formulation="WP (Wettable Powder)",
            dilution_rate="3.0 g/L",
            dilution_numeric=3.0,
            dilution_unit="g/L",
            application_method="High-volume foliar misting targeting lower canopy leaves where spores germinate.",
            nozzle_type="Hollow Cone Nozzle (0.25 MPa pressure, 150-250 µm droplet VMD)",
            phi_days=0,
            buffer_hours=4,
            strategy_type="Biological Prophylactic & Contact Antagonism",
            tank_mix_compatibility="Compatible with bio-fertilizers. Do NOT mix with copper bactericides or chlorothalonil in the same tank.",
            action_plan_summary="Strip off bottom 3-4 older leaves exhibiting concentric target-board lesions. Apply Bacillus subtilis spray in the early morning before 9:00 AM."
        ),
        SeverityStage.STAGE_2: IPMRecommendation(
            target_name="Early Blight",
            scientific_name="Alternaria solani",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_2,
            active_agent="Copper Oxychloride 50% WP + Mancozeb 75% WP",
            formulation="WP (Wettable Powder)",
            dilution_rate="2.0 g/L + 2.0 g/L",
            dilution_numeric=2.0,
            dilution_unit="g/L",
            application_method="Full canopy coverage wash focusing on lower and mid-tier foliage.",
            nozzle_type="Air Induction Flat Fan Nozzle (0.3 MPa, 200–300 µm VMD)",
            phi_days=7,
            buffer_hours=24,
            strategy_type="Protective Contact Multisite Fungicide",
            tank_mix_compatibility="Add non-ionic wetting sticker (e.g., organosilicone at 0.3 ml/L) for rain-fast adhesion.",
            action_plan_summary="Lesions are coalescing. Spray contact multi-site protectant immediately. Ensure 100% underside leaf dampening."
        ),
        SeverityStage.STAGE_3: IPMRecommendation(
            target_name="Early Blight",
            scientific_name="Alternaria solani",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_3,
            active_agent="Azoxystrobin 18.2% + Difenoconazole 11.4% SC",
            formulation="SC (Suspension Concentrate)",
            dilution_rate="1.0 ml/L",
            dilution_numeric=1.0,
            dilution_unit="ml/L",
            application_method="Motorized knapsack mist blower, total vegetative drench.",
            nozzle_type="Fine Flat Fan (0.35 MPa)",
            phi_days=14,
            buffer_hours=48,
            strategy_type="Translaminar & Acropetal Systemic Curative",
            tank_mix_compatibility="Do not tank mix with EC formulations or calcium nitrate fertilizers.",
            action_plan_summary="Critical defoliation hazard. Deploy translaminar systemic therapy. Rotate modes of action within 10 days to inhibit strobilurin resistance."
        )
    },

    # ------------------------------------------------------------------------
    # 2. POWDERY MILDEW (Erysiphe / Podosphaera spp.)
    # ------------------------------------------------------------------------
    "Powdery Mildew": {
        SeverityStage.STAGE_1: IPMRecommendation(
            target_name="Powdery Mildew",
            scientific_name="Podosphaera / Erysiphe spp.",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_1,
            active_agent="Potassium Bicarbonate (KHCO3 85%) + Horticultural Mineral Oil",
            formulation="SP (Soluble Powder) + Oil",
            dilution_rate="3.5 g/L + 2.0 ml/L",
            dilution_numeric=3.5,
            dilution_unit="g/L",
            application_method="Delicate foliar misting directly onto white powdery talc patches.",
            nozzle_type="Hollow Cone (0.2 MPa)",
            phi_days=1,
            buffer_hours=4,
            strategy_type="Osmotic Cell-Wall Disruption & Fungal Desiccation",
            tank_mix_compatibility="Do not spray if ambient temperature exceeds 32°C to prevent solar leaf scorch.",
            action_plan_summary="Alkaline pH shock desiccates superficial fungal mycelia. Spray in late afternoon. Ensure top and bottom leaf wetness."
        ),
        SeverityStage.STAGE_2: IPMRecommendation(
            target_name="Powdery Mildew",
            scientific_name="Podosphaera / Erysiphe spp.",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_2,
            active_agent="Wettable Micronized Sulphur 80% WDG",
            formulation="WDG (Water Dispersible Granules)",
            dilution_rate="2.5 g/L",
            dilution_numeric=2.5,
            dilution_unit="g/L",
            application_method="Full plant foliar spray.",
            nozzle_type="Standard Flat Fan (0.25 MPa)",
            phi_days=5,
            buffer_hours=24,
            strategy_type="Multisite Respiratory Inhibitor & Vapor Action",
            tank_mix_compatibility="Never apply sulfur within 21 days of any petroleum or horticultural oil application.",
            action_plan_summary="Apply micronized sulfur. Sulfur vapors inhibit spore germination across the entire microclimate canopy."
        ),
        SeverityStage.STAGE_3: IPMRecommendation(
            target_name="Powdery Mildew",
            scientific_name="Podosphaera / Erysiphe spp.",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_3,
            active_agent="Myclobutanil 10% WP OR Tebuconazole 25.9% EC",
            formulation="EC / WP",
            dilution_rate="0.75 ml/L",
            dilution_numeric=0.75,
            dilution_unit="ml/L",
            application_method="High-pressure canopy mist drench.",
            nozzle_type="Twin Flat Fan Nozzle (0.35 MPa)",
            phi_days=14,
            buffer_hours=48,
            strategy_type="Demethylation Inhibitor (DMI) Systemic Curative",
            tank_mix_compatibility="Can be tank mixed with non-ionic adjuvants. Do not exceed 2 seasonal applications.",
            action_plan_summary="Severe systemic colonization. DMI triazole fungicide eradicates established hyphae inside the leaf epidermal matrix."
        )
    },

    # ------------------------------------------------------------------------
    # 3. DOWNY MILDEW (Pseudoperonospora cubensis / Plasmopara viticola)
    # ------------------------------------------------------------------------
    "Downy Mildew": {
        SeverityStage.STAGE_1: IPMRecommendation(
            target_name="Downy Mildew",
            scientific_name="Pseudoperonospora cubensis",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_1,
            active_agent="Trichoderma harzianum (2x10^8 CFU/g) + Copper Hydroxide (half-dose)",
            formulation="WP (Wettable Powder)",
            dilution_rate="2.0 g/L (Trichoderma alternate) / 1.25 g/L (Copper)",
            dilution_numeric=1.25,
            dilution_unit="g/L",
            application_method="High-angle under-leaf spraying to hit stomatal opening pores.",
            nozzle_type="Swirl Chamber Hollow Cone (0.25 MPa)",
            phi_days=2,
            buffer_hours=6,
            strategy_type="Preventative Bio-bacteriostatic & Stomatal Shield",
            tank_mix_compatibility="Apply Trichoderma and Copper Hydroxide in separate staggered passes (4 days apart).",
            action_plan_summary="Downy mildew sporulates on abaxial leaf surfaces. Spray upward from ground level targeting lower leaf bellies."
        ),
        SeverityStage.STAGE_2: IPMRecommendation(
            target_name="Downy Mildew",
            scientific_name="Pseudoperonospora cubensis",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_2,
            active_agent="Cymoxanil 8% + Mancozeb 64% WP",
            formulation="WP (Wettable Powder)",
            dilution_rate="2.0 g/L",
            dilution_numeric=2.0,
            dilution_unit="g/L",
            application_method="Complete leaf immersion spray.",
            nozzle_type="Air Induction Nozzle (0.3 MPa)",
            phi_days=10,
            buffer_hours=24,
            strategy_type="Locally Systemic Kickback & Multi-site Protectant",
            tank_mix_compatibility="Avoid alkaline water (pH > 7.5); buffer spray water with citric acid to pH 6.0.",
            action_plan_summary="Angular water-soaked lesions expanding. Cymoxanil provides 48-hour post-infection kickback curativity."
        ),
        SeverityStage.STAGE_3: IPMRecommendation(
            target_name="Downy Mildew",
            scientific_name="Pseudoperonospora cubensis",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_3,
            active_agent="Dimethomorph 50% WP OR Metalaxyl-M 4% + Mancozeb 64% WP",
            formulation="WP (Wettable Powder)",
            dilution_rate="1.5 g/L",
            dilution_numeric=1.5,
            dilution_unit="g/L",
            application_method="Continuous pressurized motorized misting.",
            nozzle_type="Hollow Cone Dual Swirl (0.35 MPa)",
            phi_days=14,
            buffer_hours=48,
            strategy_type="Oomycete Cell-Wall Phospholipid Inhibitor",
            tank_mix_compatibility="Strictly rotate with Cyazofamid or Fluopicolide to avoid oomycete resistance development.",
            action_plan_summary="High sporulation risk. Total vine/leaf shutdown threatened. Emergency systemic oomyceticide spray required."
        )
    },

    # ------------------------------------------------------------------------
    # 4. LEAF RUST (Puccinia spp.)
    # ------------------------------------------------------------------------
    "Rust": {
        SeverityStage.STAGE_1: IPMRecommendation(
            target_name="Rust",
            scientific_name="Puccinia sorghi / triticina / arachidis",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_1,
            active_agent="Bio-Fungicide Bacillus amyloliquefaciens + Cold-pressed Neem extract (0.5%)",
            formulation="AS (Aqueous Suspension) + EC",
            dilution_rate="3.0 ml/L + 3.0 ml/L",
            dilution_numeric=3.0,
            dilution_unit="ml/L",
            application_method="Targeted spray onto orange/brown pustules on adaxial/abaxial foliage.",
            nozzle_type="Even Flat Fan Nozzle (0.2 MPa)",
            phi_days=0,
            buffer_hours=4,
            strategy_type="Bio-antagonistic Antibiosis & Spore Barrier",
            tank_mix_compatibility="Mix with lukewarm water (25–30°C) for optimal microbial viability.",
            action_plan_summary="Pinpoint pustules detected. Bacillus lipopeptides dissolve urediniospore germ tubes. Spray before dew rises."
        ),
        SeverityStage.STAGE_2: IPMRecommendation(
            target_name="Rust",
            scientific_name="Puccinia spp.",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_2,
            active_agent="Hexaconazole 5% EC OR Propiconazole 25% EC",
            formulation="EC (Emulsifiable Concentrate)",
            dilution_rate="1.0 ml/L",
            dilution_numeric=1.0,
            dilution_unit="ml/L",
            application_method="Uniform upper and mid canopy misting.",
            nozzle_type="Flat Fan (0.3 MPa)",
            phi_days=21,
            buffer_hours=24,
            strategy_type="Sterol Biosynthesis Inhibitor (Ergosterol Disruption)",
            tank_mix_compatibility="Do not spray under high heat (>34°C). Avoid tank mixing with organophosphate insecticides.",
            action_plan_summary="Pustules ruptured and releasing orange spores. Ergosterol inhibitor arrests haustorial nutrient siphoning."
        ),
        SeverityStage.STAGE_3: IPMRecommendation(
            target_name="Rust",
            scientific_name="Puccinia spp.",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_3,
            active_agent="Pyraclostrobin 133 g/L + Epoxiconazole 50 g/L SE",
            formulation="SE (Suspo-Emulsion)",
            dilution_rate="1.25 ml/L",
            dilution_numeric=1.25,
            dilution_unit="ml/L",
            application_method="High capacity boom or mist cannon coverage.",
            nozzle_type="Air-Assisted Low Drift Nozzle (0.4 MPa)",
            phi_days=28,
            buffer_hours=48,
            strategy_type="Dual-Action Quinone Outside Inhibitor + Triazole",
            tank_mix_compatibility="Ensure tank pH is between 5.5 and 7.0. Use dedicated clean sprayer.",
            action_plan_summary="Epidemic chlorosis and necrosis. Deploy dual active strobe-triazole combo to maintain photosynthetic green leaf area."
        )
    },

    # ------------------------------------------------------------------------
    # 5. ANTHRACNOSE (Colletotrichum spp.)
    # ------------------------------------------------------------------------
    "Anthracnose": {
        SeverityStage.STAGE_1: IPMRecommendation(
            target_name="Anthracnose",
            scientific_name="Colletotrichum gloeosporioides / coccodes",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_1,
            active_agent="Copper Oxychloride 50% WP (Half-Dose: 1.5 g/L) + Pseudomonas fluorescens (2.5 g/L)",
            formulation="WP (Wettable Powder)",
            dilution_rate="1.5 g/L (Alternate staggered 3 days)",
            dilution_numeric=1.5,
            dilution_unit="g/L",
            application_method="Preemptive prophylactic barrier misting on leaf petiole joints.",
            nozzle_type="Cone Jet Tip (0.2 MPa)",
            phi_days=1,
            buffer_hours=4,
            strategy_type="Contact Protectant Barrier + Bio-colonization",
            tank_mix_compatibility="Never combine live Pseudomonas directly with copper in the same bucket.",
            action_plan_summary="Water-soaked dark sunken speckles detected. Prune diseased twigs. Apply low-toxicity copper protectant."
        ),
        SeverityStage.STAGE_2: IPMRecommendation(
            target_name="Anthracnose",
            scientific_name="Colletotrichum spp.",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_2,
            active_agent="Thiophanate-Methyl 70% WP OR Carbendazim 12% + Mancozeb 63% WP",
            formulation="WP (Wettable Powder)",
            dilution_rate="1.5 g/L",
            dilution_numeric=1.5,
            dilution_unit="g/L",
            application_method="Full plant structural spray.",
            nozzle_type="Flat Fan (0.3 MPa)",
            phi_days=14,
            buffer_hours=24,
            strategy_type="Beta-Tubulin Assembly Inhibitor Systemic",
            tank_mix_compatibility="Compatible with standard non-ionic spreaders.",
            action_plan_summary="Lesions sunken with salmon-pink acervuli spore masses. Mitotic inhibitor stops fungal nuclear division."
        ),
        SeverityStage.STAGE_3: IPMRecommendation(
            target_name="Anthracnose",
            scientific_name="Colletotrichum spp.",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_3,
            active_agent="Trifloxystrobin 25% + Tebuconazole 50% WG",
            formulation="WG (Water Dispersible Granules)",
            dilution_rate="0.7 g/L",
            dilution_numeric=0.7,
            dilution_unit="g/L",
            application_method="Intensive canopy wash and fruit cluster soak.",
            nozzle_type="Low Drift Air Induction (0.35 MPa)",
            phi_days=15,
            buffer_hours=48,
            strategy_type="Strobilurin Mesostemic + DMI Systemic Power Blend",
            tank_mix_compatibility="Do not apply when rain is imminent within 2 hours.",
            action_plan_summary="Severe necrotic girdling. Mesostemic redistribution bonds with waxy cuticles preventing further pathogen entry."
        )
    },

    # ------------------------------------------------------------------------
    # 6. APHIDS (Aphis gossypii / Myzus persicae)
    # ------------------------------------------------------------------------
    "Aphids": {
        SeverityStage.STAGE_1: IPMRecommendation(
            target_name="Aphids",
            scientific_name="Aphis gossypii / Myzus persicae",
            category=TargetCategory.PEST,
            severity_stage=SeverityStage.STAGE_1,
            active_agent="Cold-Pressed Neem Oil (Azadirachtin 10,000 ppm) + Potassium Horticultural Soap",
            formulation="EC (Emulsifiable Concentrate) + Liquid Soap",
            dilution_rate="5.0 ml/L + 2.0 ml/L soap emulsifier",
            dilution_numeric=5.0,
            dilution_unit="ml/L",
            application_method="Foliar underside misting directly wetting insect colonies to dissolve cuticle wax.",
            nozzle_type="Hollow Cone Nozzle (0.25 MPa fine mist)",
            phi_days=0,
            buffer_hours=4,
            strategy_type="Botanical Ecdysone Inhibitor & Mechanical Spiracle Suffocation",
            tank_mix_compatibility="Shake emulsion vigorously until milky white. Do not mix with sulfur or acidic fertilizers.",
            action_plan_summary="Isolated aphid colonies on young flush shoots. Neem azadirachtin halts insect molting; potassium soap suffocates breathing spiracles."
        ),
        SeverityStage.STAGE_2: IPMRecommendation(
            target_name="Aphids",
            scientific_name="Aphis gossypii",
            category=TargetCategory.PEST,
            severity_stage=SeverityStage.STAGE_2,
            active_agent="Beauveria bassiana (1x10^8 CFU/g) OR Flonicamid 50% WG",
            formulation="WG / Bio-suspension",
            dilution_rate="0.3 g/L (Flonicamid) or 4.0 g/L (Beauveria)",
            dilution_numeric=0.3,
            dilution_unit="g/L",
            application_method="Complete undersides and crown leaf coverage.",
            nozzle_type="Fine Flat Fan (0.3 MPa)",
            phi_days=7,
            buffer_hours=12,
            strategy_type="Selective Chordotonal Organ Modulator (Antifeedant)",
            tank_mix_compatibility="Flonicamid is benign to honeybees and predatory ladybird beetles. Can mix with mild foliar micro-nutrients.",
            action_plan_summary="Moderate aphid colonies producing sticky honeydew. Flonicamid causes immediate feeding cessation within 30 minutes."
        ),
        SeverityStage.STAGE_3: IPMRecommendation(
            target_name="Aphids",
            scientific_name="Aphis gossypii",
            category=TargetCategory.PEST,
            severity_stage=SeverityStage.STAGE_3,
            active_agent="Spirotetramat 15.31% w/w OD (Bifidirectional Systemic)",
            formulation="OD (Oil Dispersion)",
            dilution_rate="0.75 ml/L",
            dilution_numeric=0.75,
            dilution_unit="ml/L",
            application_method="Motorized sprayer covering dense canopy.",
            nozzle_type="Twin Jet Air Induction (0.35 MPa)",
            phi_days=14,
            buffer_hours=24,
            strategy_type="Lipid Biosynthesis Inhibitor (Group 23 Insecticide)",
            tank_mix_compatibility="Do not tank mix with captan or sulfur. Do not apply during peak bee forage hours.",
            action_plan_summary="Severe infestation, risk of viral transmission (Cucumber Mosaic Virus) and black sooty mold. Spirotetramat moves two-way in xylem & phloem."
        )
    },

    # ------------------------------------------------------------------------
    # 7. TWO-SPOTTED SPIDER MITES (Tetranychus urticae)
    # ------------------------------------------------------------------------
    "Spider Mites": {
        SeverityStage.STAGE_1: IPMRecommendation(
            target_name="Spider Mites",
            scientific_name="Tetranychus urticae",
            category=TargetCategory.PEST,
            severity_stage=SeverityStage.STAGE_1,
            active_agent="Horticultural Canola/Soybean Botanical Oil OR Neem Azadirachtin 3000 ppm",
            formulation="EC (Emulsifiable Concentrate)",
            dilution_rate="4.0 ml/L",
            dilution_numeric=4.0,
            dilution_unit="ml/L",
            application_method="High-pressure under-leaf wash to blast early webbing and suffocate mite nymphs.",
            nozzle_type="Hollow Cone Tip with 45-degree angled wand (0.3 MPa)",
            phi_days=0,
            buffer_hours=4,
            strategy_type="Physical Suffocation & Oviposition Deterrent",
            tank_mix_compatibility="Never spray plants experiencing drought or moisture stress; hydrate roots 12 hours prior.",
            action_plan_summary="Fine stippling chlorosis spots detected. Coat the ventral (underneath) leaf surface where spider mites reside."
        ),
        SeverityStage.STAGE_2: IPMRecommendation(
            target_name="Spider Mites",
            scientific_name="Tetranychus urticae",
            category=TargetCategory.PEST,
            severity_stage=SeverityStage.STAGE_2,
            active_agent="Fenazaquin 10% EC OR Clofentezine 50% SC (Ovicidal specialist)",
            formulation="EC / SC",
            dilution_rate="1.5 ml/L",
            dilution_numeric=1.5,
            dilution_unit="ml/L",
            application_method="Dense canopy penetration spray.",
            nozzle_type="Fine Hollow Cone (0.3 MPa)",
            phi_days=10,
            buffer_hours=24,
            strategy_type="Mitochondrial Electron Transport Inhibitor (METI) & Egg Ovicide",
            tank_mix_compatibility="Maintain neutral water pH (6.5–7.0). Avoid mixing with alkaline lime sulfur.",
            action_plan_summary="Webbing visible between leaf veins. Fenazaquin controls active mobile stages while ovicide prevents next generation emergence."
        ),
        SeverityStage.STAGE_3: IPMRecommendation(
            target_name="Spider Mites",
            scientific_name="Tetranychus urticae",
            category=TargetCategory.PEST,
            severity_stage=SeverityStage.STAGE_3,
            active_agent="Abamectin 1.9% EC + Spiromesifen 22.9% SC",
            formulation="EC + SC Blend",
            dilution_rate="0.5 ml/L + 1.0 ml/L",
            dilution_numeric=1.0,
            dilution_unit="ml/L",
            application_method="Thorough foliar drench saturating webs.",
            nozzle_type="Air Induction Hollow Cone (0.35 MPa)",
            phi_days=14,
            buffer_hours=48,
            strategy_type="Translaminar GABA Neuro-inhibitor + Lipid Synthesis Inhibitor",
            tank_mix_compatibility="Always add narrow-range paraffinic oil (0.25%) to maximize translaminar absorption through leaf wax.",
            action_plan_summary="Extensive silken sheets and bronze leaf bronzing. Translaminar systemic action penetrates through protective webbing layers."
        )
    },

    # ------------------------------------------------------------------------
    # 8. THRIPS (Thrips tabaci / Scirtothrips dorsalis)
    # ------------------------------------------------------------------------
    "Thrips": {
        SeverityStage.STAGE_1: IPMRecommendation(
            target_name="Thrips",
            scientific_name="Thrips tabaci / Scirtothrips dorsalis",
            category=TargetCategory.PEST,
            severity_stage=SeverityStage.STAGE_1,
            active_agent="Blue Sticky Card Trapping + Pongamia pinnata (Karanja) Oil (2%) + Garlic Bulb Extract",
            formulation="Aqueous Emulsion",
            dilution_rate="5.0 ml/L Karanja + 3.0 ml/L Garlic Extract",
            dilution_numeric=5.0,
            dilution_unit="ml/L",
            application_method="Misting inside unopened leaf buds, terminal shoots, and flower bracts.",
            nozzle_type="Ultra Fine Hollow Cone (0.25 MPa)",
            phi_days=0,
            buffer_hours=4,
            strategy_type="Mechanical Mass Trapping + Botanical Olfactory Repellent",
            tank_mix_compatibility="Install 30 blue sticky traps per acre at canopy height alongside botanical spray.",
            action_plan_summary="Silvery leaf streaks and upward leaf curling detected. Thrips hide deep inside buds. Spray early morning when adults are sluggish."
        ),
        SeverityStage.STAGE_2: IPMRecommendation(
            target_name="Thrips",
            scientific_name="Scirtothrips dorsalis",
            category=TargetCategory.PEST,
            severity_stage=SeverityStage.STAGE_2,
            active_agent="Spinosad 45% SC (Naturalyte Fermentation Metabolite)",
            formulation="SC (Suspension Concentrate)",
            dilution_rate="0.3 ml/L (or 75 ml per acre in 200L water)",
            dilution_numeric=0.3,
            dilution_unit="ml/L",
            application_method="Thorough canopy misting.",
            nozzle_type="Fine Flat Fan (0.3 MPa)",
            phi_days=3,
            buffer_hours=12,
            strategy_type="Nicotinic Acetylcholine Receptor Allosteric Activator (Bio-Synthetic)",
            tank_mix_compatibility="Do not spray directly on open blooms when honeybees are foraging. Highly safe once spray residue dries.",
            action_plan_summary="Upward leaf cupping and brown corky scars. Spinosad derived from soil actinomycete Saccharopolyspora spinosa stops thrips feeding."
        ),
        SeverityStage.STAGE_3: IPMRecommendation(
            target_name="Thrips",
            scientific_name="Scirtothrips dorsalis",
            category=TargetCategory.PEST,
            severity_stage=SeverityStage.STAGE_3,
            active_agent="Spinetoram 11.7% SC OR Fipronil 5% SC",
            formulation="SC (Suspension Concentrate)",
            dilution_rate="1.0 ml/L",
            dilution_numeric=1.0,
            dilution_unit="ml/L",
            application_method="Motorized knapsack sprayer with fine mist extension.",
            nozzle_type="Air Induction Cone (0.35 MPa)",
            phi_days=14,
            buffer_hours=48,
            strategy_type="High-Potency Multi-site Neuro-disruptor",
            tank_mix_compatibility="Rotate with Cyantraniliprole to manage documented thrips resistance.",
            action_plan_summary="Severe leaf boat-shaped distortion and Groundnut Bud Necrosis Virus risk. High potency spinosyn class intervention required."
        )
    },

    # ------------------------------------------------------------------------
    # 9. WHITEFLIES (Bemisia tabaci)
    # ------------------------------------------------------------------------
    "Whiteflies": {
        SeverityStage.STAGE_1: IPMRecommendation(
            target_name="Whiteflies",
            scientific_name="Bemisia tabaci",
            category=TargetCategory.PEST,
            severity_stage=SeverityStage.STAGE_1,
            active_agent="Yellow Sticky Traps (40/acre) + Verticillium lecanii (Lecanicillium lecanii 1x10^8 CFU/g)",
            formulation="WP (Entomopathogenic Fungal Spores)",
            dilution_rate="5.0 g/L",
            dilution_numeric=5.0,
            dilution_unit="g/L",
            application_method="Evening foliar misting under humid (>70% RH) conditions.",
            nozzle_type="Hollow Cone (0.25 MPa)",
            phi_days=0,
            buffer_hours=4,
            strategy_type="Entomopathogenic Myco-Insecticide (Cuticular Penetration)",
            tank_mix_compatibility="Never tank mix with fungicides or copper products. Spray in late evening to prevent UV spore deactivation.",
            action_plan_summary="Whitefly adults fluttering when plants are disturbed. Fungal spores germinate on insect cuticle, sending fungal hyphae through hemolymph."
        ),
        SeverityStage.STAGE_2: IPMRecommendation(
            target_name="Whiteflies",
            scientific_name="Bemisia tabaci",
            category=TargetCategory.PEST,
            severity_stage=SeverityStage.STAGE_2,
            active_agent="Pyriproxyfen 10% EC (Insect Growth Regulator)",
            formulation="EC (Emulsifiable Concentrate)",
            dilution_rate="1.5 ml/L",
            dilution_numeric=1.5,
            dilution_unit="ml/L",
            application_method="Targeted spray onto lower leaf undersides where nymphs and 'scale' pupae feed.",
            nozzle_type="Flat Fan (0.3 MPa)",
            phi_days=7,
            buffer_hours=12,
            strategy_type="Juvenile Hormone Mimic (Sterilizes Eggs & Halts Metamorphosis)",
            tank_mix_compatibility="Safe to beneficial encarsia parasitoid wasps and predatory mirid bugs.",
            action_plan_summary="Nymph scales accumulating on underside foliage. Pyriproxyfen halts adult emergence and prevents viable egg hatching."
        ),
        SeverityStage.STAGE_3: IPMRecommendation(
            target_name="Whiteflies",
            scientific_name="Bemisia tabaci",
            category=TargetCategory.PEST,
            severity_stage=SeverityStage.STAGE_3,
            active_agent="Diafenthiuron 50% WP OR Cyantraniliprole 10.26% OD",
            formulation="WP / OD",
            dilution_rate="1.2 g/L (Diafenthiuron) / 1.8 ml/L (Cyantraniliprole)",
            dilution_numeric=1.2,
            dilution_unit="g/L",
            application_method="Total canopy saturation drench.",
            nozzle_type="Air Induction Twin Cone (0.35 MPa)",
            phi_days=15,
            buffer_hours=48,
            strategy_type="Photochemically Activated ATPase Inhibitor & Ryanodine Receptor Modulator",
            tank_mix_compatibility="Diafenthiuron requires sunlight activation on leaves within 4 hours of spraying.",
            action_plan_summary="Severe vector emergency (Tomato Leaf Curl Virus / Cotton Leaf Curl Virus). Rapid knockdown required to prevent total crop loss."
        )
    },

    # ------------------------------------------------------------------------
    # 10. LATE BLIGHT (Phytophthora infestans)
    # ------------------------------------------------------------------------
    "Late Blight": {
        SeverityStage.STAGE_1: IPMRecommendation(
            target_name="Late Blight",
            scientific_name="Phytophthora infestans",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_1,
            active_agent="Copper Hydroxide 53.8% DF (Half-dose: 1.5 g/L) + Trichoderma viride (2.0 g/L)",
            formulation="DF (Dry Flowable) + WP",
            dilution_rate="1.5 g/L Copper / 2.0 g/L Trichoderma (alternate staggered)",
            dilution_numeric=1.5,
            dilution_unit="g/L",
            application_method="High-volume preventive wash over foliage and petiole stems.",
            nozzle_type="Hollow Cone Tip (0.25 MPa)",
            phi_days=3,
            buffer_hours=6,
            strategy_type="Preventative Bio-protectant & Multi-site Copper Shield",
            tank_mix_compatibility="Never combine live Trichoderma directly with copper in the same tank.",
            action_plan_summary="Pale water-soaked lesion borders detected. Late Blight spreads rapidly in cool, humid weather. Spray preventive copper shield immediately."
        ),
        SeverityStage.STAGE_2: IPMRecommendation(
            target_name="Late Blight",
            scientific_name="Phytophthora infestans",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_2,
            active_agent="Mandipropamid 23.4% SC OR Propamocarb Hydrochloride 72.2% SL",
            formulation="SC / SL",
            dilution_rate="1.0 ml/L",
            dilution_numeric=1.0,
            dilution_unit="ml/L",
            application_method="Full plant drench covering adaxial and abaxial surfaces.",
            nozzle_type="Air Induction Flat Fan (0.3 MPa)",
            phi_days=7,
            buffer_hours=24,
            strategy_type="Translaminar Post-Infection Kickback Protectant",
            tank_mix_compatibility="Ensure tank water pH is buffered to 6.0–6.5. Add non-ionic adjuvant for rain-fastness.",
            action_plan_summary="Greasy water-soaked lesions expanding with white fungal mold under leaves. Cymoxanil penetrates within 3 hours for post-infection control."
        ),
        SeverityStage.STAGE_3: IPMRecommendation(
            target_name="Late Blight",
            scientific_name="Phytophthora infestans",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_3,
            active_agent="Metalaxyl-M 4% + Mancozeb 64% WP OR Dimethomorph 50% WP",
            formulation="WP (Wettable Powder)",
            dilution_rate="2.5 g/L",
            dilution_numeric=2.5,
            dilution_unit="g/L",
            application_method="High-pressure misting throughout entire field canopy.",
            nozzle_type="Twin Swirl Cone Nozzle (0.35 MPa)",
            phi_days=14,
            buffer_hours=48,
            strategy_type="Acropetal Systemic Phenylamide Oomyceticide",
            tank_mix_compatibility="Rotate with Mandipropamid or Cyazofamid to prevent severe oomycete resistance development.",
            action_plan_summary="Severe blight collapse. Blackened necrotic stems and rotting foliage. Deploy systemic phenylamide fungicide immediately."
        )
    },

    # ------------------------------------------------------------------------
    # 11. BACTERIAL LEAF SPOT / CANKER (Xanthomonas campestris)
    # ------------------------------------------------------------------------
    "Bacterial Spot": {
        SeverityStage.STAGE_1: IPMRecommendation(
            target_name="Bacterial Spot",
            scientific_name="Xanthomonas campestris pv. vesicatoria",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_1,
            active_agent="Pseudomonas fluorescens (2x10^8 CFU/g) + Cold-pressed Neem extract",
            formulation="WP + EC",
            dilution_rate="3.0 g/L + 2.0 ml/L",
            dilution_numeric=3.0,
            dilution_unit="g/L",
            application_method="Early morning foliar spray targeting stomatal openings.",
            nozzle_type="Fine Mist Cone (0.2 MPa)",
            phi_days=0,
            buffer_hours=4,
            strategy_type="Biological Antagonism & Phyllosphere Bacteriostatic Colonization",
            tank_mix_compatibility="Compatible with bio-stimulants. Do not mix with antibiotics or synthetic copper.",
            action_plan_summary="Small dark angular spots with faint yellow halos. Apply beneficial Pseudomonas to outcompete pathogenic bacteria on leaf surfaces."
        ),
        SeverityStage.STAGE_2: IPMRecommendation(
            target_name="Bacterial Spot",
            scientific_name="Xanthomonas campestris",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_2,
            active_agent="Copper Oxychloride 50% WP (2.5 g/L) + Streptocycline 90:10 (0.1 g/L)",
            formulation="WP (Wettable Powder) + Soluble Powder",
            dilution_rate="2.5 g/L + 0.1 g/L",
            dilution_numeric=2.5,
            dilution_unit="g/L",
            application_method="Thorough foliar wash during dry weather.",
            nozzle_type="Flat Fan (0.3 MPa)",
            phi_days=10,
            buffer_hours=24,
            strategy_type="Contact Bactericidal Membrane Disruption + Protein Synthesis Inhibition",
            tank_mix_compatibility="Dissolve Streptocycline in a small cup of warm water first, then add to copper spray tank.",
            action_plan_summary="Spots coalescing with chlorotic yellow halos. Apply copper bactericide with agricultural antibiotic. Avoid touching wet plants."
        ),
        SeverityStage.STAGE_3: IPMRecommendation(
            target_name="Bacterial Spot",
            scientific_name="Xanthomonas campestris",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_3,
            active_agent="Kasugamycin 3% SL (1.5 ml/L) + Copper Hydroxide (1.5 g/L)",
            formulation="SL (Soluble Liquid) + DF",
            dilution_rate="1.5 ml/L + 1.5 g/L",
            dilution_numeric=1.5,
            dilution_unit="ml/L",
            application_method="Motorized fine mist wash over all vegetative tissue.",
            nozzle_type="Air Induction Twin Fan (0.35 MPa)",
            phi_days=14,
            buffer_hours=48,
            strategy_type="Systemic Aminoglycoside Antibiotic + Fixed Copper Protectant",
            tank_mix_compatibility="Do not spray in bright blazing direct midday sun; apply in early morning or overcast conditions.",
            action_plan_summary="Severe bacterial blight with extensive yellowing, shot-hole necrosis, and defoliation. Systemic Kasugamycin arrests bacterial proliferation."
        )
    },

    # ------------------------------------------------------------------------
    # 12. CERCOSPORA LEAF SPOT / TIKKA (Cercospora spp.)
    # ------------------------------------------------------------------------
    "Cercospora Leaf Spot": {
        SeverityStage.STAGE_1: IPMRecommendation(
            target_name="Cercospora Leaf Spot",
            scientific_name="Cercospora arachidicola / canescens",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_1,
            active_agent="Bacillus subtilis (QST 713) + Potassium Silicate (2.0 ml/L)",
            formulation="WP + Liquid",
            dilution_rate="3.0 g/L + 2.0 ml/L",
            dilution_numeric=3.0,
            dilution_unit="g/L",
            application_method="Foliar mist covering both upper and lower leaf canopy.",
            nozzle_type="Hollow Cone (0.25 MPa)",
            phi_days=0,
            buffer_hours=4,
            strategy_type="Bio-antagonism & Cuticular Epidermal Silicate Strengthening",
            tank_mix_compatibility="Compatible with seaweed extract biostimulants.",
            action_plan_summary="Discrete small circular spots with yellow borders. Silicate reinforces leaf cuticles against fungal appressorium penetration."
        ),
        SeverityStage.STAGE_2: IPMRecommendation(
            target_name="Cercospora Leaf Spot",
            scientific_name="Cercospora spp.",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_2,
            active_agent="Carbendazim 12% + Mancozeb 63% WP",
            formulation="WP (Wettable Powder)",
            dilution_rate="2.0 g/L",
            dilution_numeric=2.0,
            dilution_unit="g/L",
            application_method="Uniform foliar spray targeting lower and mid leaves.",
            nozzle_type="Standard Flat Fan (0.3 MPa)",
            phi_days=14,
            buffer_hours=24,
            strategy_type="Multisite Protectant + Systemic Tubulin Inhibitor",
            tank_mix_compatibility="Add sticker-spreader adjuvant for persistent adhesion during dew and rains.",
            action_plan_summary="Spots enlarging with dark brown necrotic centers. Dual-action carbendazim-mancozeb blend provides contact and upward systemic protection."
        ),
        SeverityStage.STAGE_3: IPMRecommendation(
            target_name="Cercospora Leaf Spot",
            scientific_name="Cercospora spp.",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_3,
            active_agent="Difenoconazole 25% EC (0.5 ml/L) OR Tebuconazole 25.9% EC (1.0 ml/L)",
            formulation="EC (Emulsifiable Concentrate)",
            dilution_rate="0.5 ml/L (Difenoconazole) or 1.0 ml/L (Tebuconazole)",
            dilution_numeric=0.5,
            dilution_unit="ml/L",
            application_method="High-pressure canopy mist penetration.",
            nozzle_type="Low Drift Air Induction (0.35 MPa)",
            phi_days=21,
            buffer_hours=48,
            strategy_type="Demethylation Inhibitor (DMI) Systemic Triazole Curative",
            tank_mix_compatibility="Do not exceed 2 consecutive applications. Rotate with chlorothalonil for resistance stewardship.",
            action_plan_summary="Critical leaf spotting causing premature senescence and defoliation. Potent triazole curative halts fungal ergosterol synthesis."
        )
    },

    # ------------------------------------------------------------------------
    # 13. HEALTHY CROP LEAF (No chemical pesticide required)
    # ------------------------------------------------------------------------
    "Healthy": {
        SeverityStage.STAGE_1: IPMRecommendation(
            target_name="Healthy Crop Foliage",
            scientific_name="Plantae / Healthy Vegetative Foliage",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_1,
            active_agent="Ascophyllum nodosum Seaweed Extract (2.0 ml/L) + Organic Microbial Bio-fertilizer",
            formulation="Liquid Organic Biostimulant",
            dilution_rate="2.0 ml/L",
            dilution_numeric=2.0,
            dilution_unit="ml/L",
            application_method="Light preventive nutritional misting across healthy foliage.",
            nozzle_type="Standard Flat Fan (0.2 MPa)",
            phi_days=0,
            buffer_hours=0,
            strategy_type="Prophylactic Plant Health & Natural Immunity Priming (NO Chemical Pesticide)",
            tank_mix_compatibility="Compatible with zinc, boron, and organic amino acid foliar sprays.",
            action_plan_summary="Leaf blade shows clear chlorophyll integrity with no significant necrotic lesions or pest colonies. No synthetic chemicals needed. Continue regular field monitoring and balanced nutrition."
        ),
        SeverityStage.STAGE_2: IPMRecommendation(
            target_name="Healthy Crop Foliage",
            scientific_name="Plantae / Healthy Vegetative Foliage",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_2,
            active_agent="Ascophyllum nodosum Seaweed Extract (2.0 ml/L) + Potassium Silicate (1.5 ml/L)",
            formulation="Liquid Organic Biostimulant",
            dilution_rate="2.0 ml/L",
            dilution_numeric=2.0,
            dilution_unit="ml/L",
            application_method="Preventive foliar nutrition.",
            nozzle_type="Flat Fan (0.2 MPa)",
            phi_days=0,
            buffer_hours=0,
            strategy_type="Preventive Crop Vigour (0 Synthetic Pesticides)",
            tank_mix_compatibility="Compatible with balanced organic nutrients.",
            action_plan_summary="Minor mechanical wear or natural vein texture detected, but leaf is fundamentally healthy. No pesticide application required."
        ),
        SeverityStage.STAGE_3: IPMRecommendation(
            target_name="Healthy Crop Foliage",
            scientific_name="Plantae / Healthy Vegetative Foliage",
            category=TargetCategory.PATHOGEN,
            severity_stage=SeverityStage.STAGE_3,
            active_agent="Ascophyllum nodosum Seaweed Extract (2.0 ml/L)",
            formulation="Liquid Biostimulant",
            dilution_rate="2.0 ml/L",
            dilution_numeric=2.0,
            dilution_unit="ml/L",
            application_method="Foliar misting.",
            nozzle_type="Flat Fan (0.2 MPa)",
            phi_days=0,
            buffer_hours=0,
            strategy_type="Organic Prophylactic",
            tank_mix_compatibility="Safe.",
            action_plan_summary="Healthy foliage confirmed. Maintain standard crop stewardship."
        )
    }
}


# ============================================================================
# ADVISORY HELPER FUNCTIONS
# ============================================================================

def get_advisory(target_name: str, stage: SeverityStage, is_pest: bool = False) -> IPMRecommendation:
    """
    Retrieve typed IPM diagnostic recommendation for a diagnosed target organism
    at a specific agronomic severity stage. Fallback to closest match if not exact.
    """
    # 1. Exact match
    if target_name in ADVISORY_MATRIX:
        sub_map = ADVISORY_MATRIX[target_name]
        if stage in sub_map:
            return sub_map[stage]
        return sub_map[SeverityStage.STAGE_1]

    # 2. Case-insensitive fuzzy substring search
    target_lower = target_name.lower()
    for key, sub_map in ADVISORY_MATRIX.items():
        if key.lower() in target_lower or target_lower in key.lower():
            if stage in sub_map:
                return sub_map[stage]
            return sub_map[SeverityStage.STAGE_1]

    # 3. Categorical default fallback (Pathogen vs Pest)
    fallback_key = "Aphids" if is_pest else "Early Blight"
    return ADVISORY_MATRIX[fallback_key].get(stage, ADVISORY_MATRIX[fallback_key][SeverityStage.STAGE_1])


def get_all_stage_advisories(target_name: str, is_pest: bool = False) -> Dict[str, IPMRecommendation]:
    """
    Retrieve IPM recommendations across all 3 stages (Stage 1, Stage 2, Stage 3)
    for a diagnosed target organism.
    """
    key = target_name
    if target_name not in ADVISORY_MATRIX:
        target_lower = target_name.lower()
        found = False
        for k in ADVISORY_MATRIX.keys():
            if k.lower() in target_lower or target_lower in k.lower():
                key = k
                found = True
                break
        if not found:
            key = "Aphids" if is_pest else "Early Blight"

    sub_map = ADVISORY_MATRIX[key]
    return {
        "stage_1": sub_map[SeverityStage.STAGE_1],
        "stage_2": sub_map[SeverityStage.STAGE_2],
        "stage_3": sub_map[SeverityStage.STAGE_3],
    }

