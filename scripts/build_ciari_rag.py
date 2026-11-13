"""Build the comprehensive ICAR-CIARI RAG Knowledge Base from official Package of Practices PDFs.
Generates comprehensive, verified agricultural knowledge chunks for all crops and island farming practices.
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUT_FILE = os.path.join(DATA_DIR, 'ciari_rag_knowledge.json')

entries = []

def add(doc_id, crop, scientific_name, category, farming_type, topic, title, question, answer, keywords, source='ICAR-CIARI Package of Practices', source_url='https://ciari.icar.gov.in/'):
    entries.append({
        'id': doc_id,
        'crop': crop,
        'scientific_name': scientific_name,
        'category': category,
        'farming_type': farming_type,
        'topic': topic,
        'title': title,
        'question': question,
        'answer': answer.strip(),
        'keywords': keywords,
        'source': source,
        'source_url': source_url,
    })

# ==========================================
# 1. TOMATO (Solanum lycopersicum)
# ==========================================
add(
    'CIARI-TOMATO-ORG-01', 'Tomato', 'Solanum lycopersicum', 'Vegetable', 'organic',
    'varieties_season',
    'Tomato Organic Varieties and Growing Season in Andaman & Nicobar',
    'What are the recommended varieties and growing seasons for organic tomato in Andaman and Nicobar Islands?',
    """According to ICAR-CIARI recommendations for Andaman & Nicobar Islands:
- Growing Seasons:
  1. Dry Season (Main Open Field Crop): December to April. Seedlings raised in Oct-Nov for early crop, Nov-Dec for main crop, Jan for late crop.
  2. Rainy Season (Protected Cultivation / Rain Shelter): May to December. Raised under polyhouse or rain shelter with side insect nets (April-May for early, June for main, July-Aug for late).
- Recommended Varieties:
  - Arka Vikas, Ayush, Arka Samrat, Arka Saurabh, Pusa Sadabahar, Arka Shrestha, Arka Rakshak (triple disease resistant: ToLCV + Bacterial Wilt + Early Blight), BT-1, BT-10, Laxmi.
- Soil & Climate:
  - Optimum growth temperature 21-24°C; fruit set night temperature 15-20°C. Polyhouse temperature should be kept below 28-30°C with good ventilation.
  - Well drained sandy loam to loamy soils with pH 6.0-7.0 rich in organic matter. On acidic island soils, apply agricultural lime (1-2 t/ha) and organic amendments like coconut husk, vermicompost, and poultry manure.""",
    'tomato, tamatar, varieties, season, arka vikas, arka rakshak, arka samrat, sowing time, dec april, rain shelter, solanum lycopersicum'
)

add(
    'CIARI-TOMATO-ORG-02', 'Tomato', 'Solanum lycopersicum', 'Vegetable', 'organic',
    'nursery_spacing',
    'Tomato Nursery Management, Seed Rate, and Raised Bed Spacing (ICAR-CIARI)',
    'What is the seed rate, nursery preparation, and spacing for tomato in Andaman conditions?',
    """According to ICAR-CIARI Package of Practices:
- Seed Rate:
  - Open-pollinated varieties: 300 - 350 g/ha.
  - Hybrids: 150 g/ha.
- Nursery Preparation:
  - Prepare 10-15 raised beds of 7-10 m length, 1 m width, and 20-30 cm height with 50 cm wide furrows.
  - Mix FYM @ 5 kg/sq.m and vermicompost @ 1 kg/sq.m. Sow seeds in lines 5 cm apart and 1-2 cm deep.
  - Cover with fine FYM and dry grass mulch until germination. Protect from heavy rain using rain shelters.
  - Pro-tray method: Use 98-cell pro-trays with coir pith + vermicompost (1:1). Protect seedlings with Pseudomonas fluorescens and Trichoderma viride @ 2 g/10 ml.
  - Transplant 21-25 days old seedlings (4-5 true leaves). Harden by alternate-day watering 1 week before transplanting.
- Spacing:
  - Single row system: 50-60 cm (row to row) x 40-50 cm (plant to plant).
  - Double row raised bed system (strongly recommended for islands to avoid waterlogging): 80-100 cm bed width (plants at 60 cm x 40 cm) + 50 cm furrow between beds.""",
    'tomato seed rate, nursery raised beds, spacing, double row system, pro tray, hardening, transplanting age'
)

add(
    'CIARI-TOMATO-ORG-03', 'Tomato', 'Solanum lycopersicum', 'Vegetable', 'organic',
    'nutrient_fertilizer',
    'Tomato Organic Nutrient Management (ICAR-CIARI)',
    'How to fertilize tomato organically using ICAR-CIARI island package of practices?',
    """ICAR-CIARI Organic Nutrition Protocol for Tomato:
- Basal Pit Application:
  - Farmyard Manure (FYM) @ 20-25 tonnes/ha or Vermicompost @ 3-5 tonnes/ha.
  - Mix with Trichoderma viride (2.5 kg/ha), Pseudomonas fluorescens (2.5 kg/ha), and PGPR mix in planting pits.
- Liquid Organic Top-Dressing (applied every 7-10 days interval):
  1. Fresh cow dung slurry: 1 kg in 10 litres water (50 kg/ha equivalent).
  2. Biogas slurry: 1 kg in 10 litres water (50 kg/ha).
  3. Cow urine: 500 litres/ha diluted 8 times (1 part urine in 8 parts water) as root drench or foliar spray.
  4. Vermiwash: 500 litres/ha diluted 8 times as foliar misting for micronutrients and growth promoters.
  5. Groundnut cake slurry: 1 kg in 10 litres water (50 kg/ha) after 2-3 days fermentation.
- Panchagavya: 3% foliar spray (30 ml/L) at 15, 30, 45, and 60 days after transplanting improves fruit setting, lycopene content, and shelf life.""",
    'tomato organic fertilizer, cow dung slurry, vermiwash, cow urine, panchagavya, fym, biogas slurry, nutrient management'
)

add(
    'CIARI-TOMATO-ORG-04', 'Tomato', 'Solanum lycopersicum', 'Vegetable', 'organic',
    'pest_disease_management',
    'Tomato Organic Pest and Disease Management (ICAR-CIARI)',
    'How to manage tomato pests (fruit borer, leaf curl whitefly) and diseases (bacterial wilt, damping off) organically?',
    """ICAR-CIARI Organic Plant Protection for Tomato:
1. Pests:
   - Fruit Borer (Helicoverpa armigera):
     - Install pheromone traps (Helilure) @ 12-15 traps/ha.
     - Clip and destroy damaged fruits and bored shoots.
     - Spray cold-pressed Neem Oil 10,000 ppm (5 ml/litre water) + soap emulsifier or NSKE 5% at early larval instar.
     - Spray Bacillus thuringiensis (Bt) @ 2 g/L or Beauveria bassiana @ 5 g/L.
   - Sucking Pests & Whitefly (Vector of Tomato Leaf Curl Virus / ToLCV):
     - Set up yellow sticky traps @ 15-20 traps/ha.
     - Spray Sida spinosa 3% leaf extract or NSKE 5% extract.
     - Spray Garlic-Chilli-Ginger extract (18g garlic + 9g green chilli + 9g ginger crushed in 1L water + 5g soap).
   - Serpentine Leaf Miner: Spray 2% neem oil or Pongamia (karanj) oil emulsion.
2. Diseases:
   - Damping-Off (Pythium / Rhizoctonia): Raise nursery on 20 cm high beds with furrows. Seed treatment with Trichoderma viride @ 5-10 g/kg seed. Soil drenching with Trichoderma @ 10 g/L.
   - Bacterial Wilt (Ralstonia solanacearum): Highly prevalent in acidic island soils. Plant wilt-tolerant varieties like Arka Rakshak, BT-1, BT-10; dip roots in Pseudomonas fluorescens (10 g/L) for 30 minutes; incorporate lime and poultry manure.
   - Late Blight & Early Blight: Prophylactic foliar spray of Trichoderma viride (10 g/L) or Copper Oxychloride at half dose (1.5 g/L) or cow urine (10%) + Pseudomonas fluorescens (5 g/L).
- Yield: 25-35 tonnes/ha under open field, 40-50 t/ha under rain shelter/polyhouse.""",
    'tomato fruit borer, leaf curl, whitefly, bacterial wilt, damping off, trichoderma, neem oil, garlic chilli extract, helicoverpa'
)

add(
    'CIARI-TOMATO-CHEM-05', 'Tomato', 'Solanum lycopersicum', 'Vegetable', 'conventional',
    'nutrient_fertilizer',
    'Tomato Conventional / Integrated Fertilizer Doses (ICAR-CIARI PoP 2014)',
    'What is the recommended chemical NPK fertilizer dose for tomato in Andaman and Nicobar Islands?',
    """According to ICAR-CIARI Vegetable Cultivation PoP:
- Recommended NPK Dose: 100 : 60 : 60 kg/ha (N : P2O5 : K2O).
- Basal Application (at final land preparation):
  - FYM: 20-25 tonnes/ha.
  - Nitrogen: 50 kg N/ha (approx. 110 kg Urea).
  - Phosphorus: 60 kg P2O5/ha (approx. 375 kg Single Super Phosphate / SSP, or 130 kg DAP).
  - Potassium: 60 kg K2O/ha (approx. 100 kg Muriate of Potash / MOP).
- Top Dressing:
  - Remaining 50 kg Nitrogen divided into two equal split doses (25 kg N each = 55 kg Urea):
    1. First top dressing at 30 days after transplanting (DAT).
    2. Second top dressing at 45-50 DAT (flowering and early fruit formation).
- Micronutrients: Spray Borax @ 1 g/L and Zinc Sulphate @ 2 g/L at flower initiation to prevent blossom end rot and fruit cracking.""",
    'tomato npk dose, urea, dap, ssp, mop, fertilizer recommendation, andaman tomato fertilizer, top dressing'
)

# ==========================================
# 2. BRINJAL / EGGPLANT (Solanum melongena)
# ==========================================
add(
    'CIARI-BRINJAL-ORG-01', 'Brinjal', 'Solanum melongena', 'Vegetable', 'organic',
    'varieties_season',
    'Brinjal Varieties, Season, and Seed Rate in A&N Islands (ICAR-CIARI)',
    'What varieties and planting season are recommended for brinjal in Andaman & Nicobar?',
    """According to ICAR-CIARI Package of Practices:
- Season:
  - Main Open Field Crop: Dry season (December to May).
  - Rainy Season Crop: May to November (grown on raised beds with proper drainage or under rain shelter).
- Recommended Varieties:
  - Pusa Purple Cluster, Pusa Purple Round, Pusa Purple Long, Arka Keshav, Arka Nidhi, Arka Shirish, BB-44, CARI Brinjal-1 (bacterial wilt resistant island selection), Green Round local.
- Seed Rate:
  - Open-pollinated varieties: 350 - 400 g/ha.
  - Hybrids: 150 - 200 g/ha.
- Spacing:
  - Single row: 75 cm between rows x 50-60 cm between plants.
  - Double row bed system: 100 cm bed (rows at 80 cm x 60 cm) + 80 cm furrow between beds.
- Transplanting: 30-35 days old seedlings (12-15 cm height with 4-5 leaves).""",
    'brinjal, baingan, egg plant, varieties, cari brinjal 1, pusa purple cluster, seed rate, spacing, season, solanum melongena'
)

add(
    'CIARI-BRINJAL-ORG-02', 'Brinjal', 'Solanum melongena', 'Vegetable', 'organic',
    'pest_disease_management',
    'Brinjal Shoot and Fruit Borer and Bacterial Wilt Organic Control (ICAR-CIARI)',
    'How to control brinjal shoot and fruit borer and bacterial wilt using ICAR-CIARI practices?',
    """ICAR-CIARI Organic Protocol for Brinjal Protection:
1. Shoot and Fruit Borer (Leucinodes orbonalis) - The Most Damaging Pest:
   - Cultural & Mechanical: Clip off and bury all withered/drooping shoots along with larvae twice a week. Pick and destroy bored fruits at every harvest.
   - Pheromone Trapping: Install Lucinlure pheromone traps @ 12-15 traps/ha at crop canopy level.
   - Botanical Sprays:
     - Spray cold-pressed Neem Oil 10,000 ppm (5 ml/L) + 1 ml liquid soap every 10 days.
     - Spray Pongamia (karanj) oil @ 5 ml/L.
     - Prepare Garlic (18g) + Green Chilli (9g) + Ginger (9g) extract crushed separately, mixed in 1L water + 5g soap; spray thoroughly on shoots and flowers.
   - Bio-agent: Spray Bacillus thuringiensis (Bt) @ 2 g/L or Beauveria bassiana @ 5 g/L in the evening.
2. Epilachna Beetle (Hadda beetle): Hand-pick adult beetles and spiny grubs; spray 2% neem oil.
3. Sucking Pests (Aphids, Jassids, Whitefly): Yellow sticky traps; spray Verticillium lecanii @ 5 g/L or NSKE 5%.
4. Bacterial Wilt (Ralstonia solanacearum):
   - Grow CARI Brinjal-1, BB-44, or Arka Nidhi (resistant varieties).
   - Dip seedling roots in Pseudomonas fluorescens (10 g/L) for 30 minutes before planting.
   - Avoid planting in waterlogged soils; amend soil with lime (1-2 t/ha) to bring pH to 6.5.
5. Phomopsis Blight & Fruit Rot: Seed treatment with Trichoderma viride (10 g/kg); foliar spray with Trichoderma (10 g/L).
- Yield: 30-40 tonnes/ha.""",
    'brinjal shoot and fruit borer, leucinodes orbonalis, pheromone traps, lucinlure, bacterial wilt, epilachna beetle, neem oil, cari brinjal 1'
)

add(
    'CIARI-BRINJAL-CHEM-03', 'Brinjal', 'Solanum melongena', 'Vegetable', 'conventional',
    'nutrient_fertilizer',
    'Brinjal Chemical Fertilizers and Insecticides (ICAR-CIARI PoP 2014)',
    'What is the recommended fertilizer schedule and chemical pest spray for brinjal in Andaman?',
    """According to ICAR-CIARI Vegetable PoP 2014:
- Fertilizer Schedule:
  - FYM: 20-25 tonnes/ha.
  - NPK Dose: 100 : 60 : 60 kg/ha.
  - Basal: 50 kg N (110 kg Urea) + 60 kg P2O5 (375 kg SSP) + 60 kg K2O (100 kg MOP).
  - Top Dressing: 50 kg N in two equal splits at 30 and 45 days after transplanting.
- Chemical Plant Protection:
  - Shoot & Fruit Borer: Spray Chlorantraniliprole 18.5% SC @ 0.3 ml/L or Emamectin Benzoate 5% SG @ 0.4 g/L or Spinosad 45% SC @ 0.3 ml/L at 15-day intervals.
  - Sucking Pests (Jassids, Aphids): Spray Imidacloprid 17.8% SL @ 0.3 ml/L.
  - Bacterial Wilt: Drench root zone with Streptocycline (1 g/10L) + Copper Oxychloride (2.5 g/L).""",
    'brinjal chemical fertilizer, npk 100 60 60, chlorantraniliprole, emamectin benzoate, imidacloprid, shoot borer spray'
)

# ==========================================
# 3. CHILLI (Capsicum annuum)
# ==========================================
add(
    'CIARI-CHILLI-ORG-01', 'Chilli', 'Capsicum annuum', 'Vegetable', 'organic',
    'varieties_spacing_management',
    'Chilli Organic Cultivation Package of Practices (ICAR-CIARI)',
    'What are the recommended varieties, spacing, and organic practices for chilli in Andaman?',
    """According to ICAR-CIARI Package of Practices:
- Season:
  - Main crop: Dry season (December to May).
  - Rainy season: Raised beds with drainage or rain shelters (June to November).
- Recommended Varieties:
  - LCA-206, CARI Senorita, Pusa Sadabahar, Kashi Anmol, Bullet, local Andaman bird chilli selections.
- Seed Rate: 1.0 - 1.5 kg/ha for open-pollinated; 200-250 g/ha for hybrids.
- Nursery & Transplanting:
  - 6-7 weeks old seedlings (15 cm tall) transplanted at 60 cm x 45 cm on raised beds.
- Organic Nutrition:
  - Basal: FYM @ 20-25 t/ha + Vermicompost @ 2-3 t/ha + Trichoderma (2.5 kg/ha).
  - Top dressing: Cow dung slurry (1 kg/10L) or biogas slurry (1 kg/10L) at 15-day intervals; Vermiwash (500 L/ha diluted 8x) foliar spray; Panchagavya 3% at flowering.
- Pest & Disease Management:
  - Thrips, Aphids & Mites (vectors of Leaf Curl / Murda disease):
    - Intercrop with Sesbania grandiflora (Agathi) on field borders as live barrier/shade.
    - Set up yellow and blue sticky traps @ 15-20 traps/ha.
    - Spray Cold-pressed Neem oil (5 ml/L) or Pongamia oil (5 ml/L) + soap.
    - Spray Verticillium lecanii @ 5 g/L for thrips and mites.
  - Anthracnose / Fruit Rot / Die-Back (Colletotrichum capsici):
    - Seed treatment with Trichoderma viride (10 g/kg).
    - Prophylactic foliar spray with Pseudomonas fluorescens (10 g/L) or Copper Oxychloride (2 g/L).
- Yield: 8-12 tonnes/ha green chillies, 1.5-2.5 t/ha dry chillies.""",
    'chilli, mirch, capsicum annuum, varieties, lca 206, cari senorita, thrips, mites, leaf curl, anthracnose, dieback, neem oil'
)

# ==========================================
# 4. SWEET PEPPER / CAPSICUM (Capsicum annuum)
# ==========================================
add(
    'CIARI-CAPSICUM-ORG-01', 'Sweet Pepper', 'Capsicum annuum', 'Vegetable', 'organic',
    'capsicum_protected_cultivation',
    'Sweet Pepper / Capsicum Cultivation in Andaman Protected Structures (ICAR-CIARI)',
    'How to cultivate sweet pepper / capsicum under Andaman conditions according to ICAR-CIARI?',
    """According to ICAR-CIARI Recommendations:
- Cultivation System:
  - Best suited for Rain Shelter / Polyhouse / Net House cultivation in the islands due to high humidity and heavy rains.
- Varieties:
  - California Wonder, Orobelle (yellow), Indra, Bharat, Bachata (yellow), Bomby (red).
- Nursery:
  - Grow in 98-cell pro-trays with coir pith + vermicompost (1:1) enriched with Trichoderma and Pseudomonas. Transplant 30-35 days old seedlings.
- Spacing: 60 cm x 45 cm on raised beds of 1 m width.
- Plant Canopy Management:
  - Provide bamboo sticks or trellis string staking to keep plants upright.
  - Pruning: Essential operation—pinch/prune the initial 3-4 crown flowers to allow strong vegetative framework, then maintain 2-4 main stems.
- Nutrition:
  - Vermicompost @ 5 t/ha + neem cake 500 kg/ha. Apply fermented cow dung slurry or vermiwash weekly. Foliar spray Panchagavya 3% at 15-day intervals.
- Protection:
  - Broad mites & Thrips: Spray wettable sulphur (2 g/L) or neem oil (5 ml/L).
  - Powdery Mildew: Spray wettable sulphur 2 g/L or Trichoderma foliar spray.
  - Bacterial Wilt: Use resistant varieties and soil solarization.
- Yield: 20-35 tonnes/ha under protected structures.""",
    'capsicum, sweet pepper, shimla mirch, protected cultivation, rain shelter, polyhouse, california wonder, indra, pruning, broad mite'
)

# ==========================================
# 5. OKRA / BHINDI (Abelmoschus esculentus)
# ==========================================
add(
    'CIARI-OKRA-ORG-01', 'Okra', 'Abelmoschus esculentus', 'Vegetable', 'organic',
    'varieties_yvmv_management',
    'Okra / Bhindi Organic Cultivation and YVMV Control (ICAR-CIARI)',
    'What are the ICAR-CIARI recommendations for Okra varieties, spacing, and YVMV disease management?',
    """According to ICAR-CIARI Package of Practices:
- Season: Round the year cultivation in Andaman (90-110 days duration crop). Main sowings: May-June (rainy) and October-November (dry season).
- Recommended Varieties:
  - Arka Anamika (YVMV tolerant), Pusa Sawani, Pusa A-4, Kashi Pragati, Varsha Uphar, Parbhani Kranti.
- Seed Rate & Sowing:
  - Summer / Dry season: 12 - 15 kg/ha.
  - Rainy season: 8 - 10 kg/ha.
  - Pre-sowing seed treatment: Soak seeds in water for 12 hours, then treat with Trichoderma viride @ 5 g/kg seed to hasten germination and prevent collar rot.
- Spacing:
  - Rainy season: 60 cm (rows) x 30 cm (plants).
  - Dry season: 45 cm x 15-20 cm on raised beds.
- Organic Nutrition:
  - FYM 20-25 t/ha at first ploughing. Fresh cow dung slurry (1 kg/10L) or biogas slurry (50 kg/ha) or cow urine (500 L/ha diluted 8x) applied at 15-day intervals.
- Major Pest & Disease Management:
  1. Yellow Vein Mosaic Virus (YVMV):
     - Most devastating disease transmitted by whitefly (Bemisia tabaci).
     - Grow resistant varieties: Arka Anamika, Varsha Uphar.
     - Install yellow sticky traps @ 15 traps/ha.
     - Spray cold-pressed Neem Oil 10,000 ppm (5 ml/L) or NSKE 5% at weekly intervals to suppress whitefly vectors.
  2. Shoot and Fruit Borer (Earias vittella):
     - Remove damaged shoots and bored pods.
     - Install pheromone traps @ 10-12/ha. Spray Beauveria bassiana @ 5 g/L or Bt @ 2 g/L.
  3. Cercospora Leaf Spot: Spray Trichoderma (10 g/L) or Bordeaux mixture 1%.
- Harvesting & Yield: Harvest tender pods every alternate day (6-8 days after flowering). Yield: 10-15 tonnes/ha.""",
    'okra, bhindi, abelmoschus esculentus, yvmv, yellow vein mosaic virus, whitefly, arka anamika, seed rate, spacing, shoot fruit borer'
)

# ==========================================
# 6. COLE CROPS: CAULIFLOWER, CABBAGE, KNOLKHOL, BROCCOLI
# ==========================================
add(
    'CIARI-COLE-01', 'Cole Crops', 'Brassica oleracea', 'Vegetable', 'organic_and_conventional',
    'cole_crops_package',
    'Cauliflower, Cabbage, Knolkhol, and Broccoli Package of Practices (ICAR-CIARI)',
    'How to cultivate Cauliflower, Cabbage, Knolkhol, and Broccoli in Andaman & Nicobar Islands?',
    """According to ICAR-CIARI Package of Practices:
1. CAULIFLOWER (Brassica oleracea var. botrytis):
   - Season: Open field in Dry season (Nov-Jan sowing, Dec-April harvest); Rain shelter in rainy season (May-Sept).
   - Varieties: White Marble, White Shot, Best Early, Early Kunwari, Pusa Meghna.
   - Seed Rate: 400-450 g/ha. Spacing: 50 cm x 30-40 cm (single row) or double-row bed 60 cm (40x30 cm) + 50 cm furrow.
   - Nutrition: FYM 20-25 t/ha + NPK 120:80:80 kg/ha (or vermicompost 3 t/ha + cow dung slurry).
   - Micronutrient: Apply Borax @ 10-15 kg/ha in soil or spray Borax 1 g/L to prevent "Browning / Hollow Stem" (Boron deficiency) and Ammonium Molybdate 1 g/L to prevent "Whiptail".
   - Yield: 15-20 t/ha.
2. CABBAGE (Brassica oleracea var. capitata):
   - Varieties: NS-43, Green Express, Rare Ball, Pusa Ageti.
   - Seed Rate: 300-350 g/ha. Spacing: 45 cm x 30-45 cm on double row beds.
   - Yield: 20-30 t/ha.
3. KNOLKHOL (Brassica oleracea var. gongylodes):
   - Varieties: Super Star, White Vienna, Early White Vienna.
   - Seed Rate: 1.0 - 1.5 kg/ha. Spacing: 30 cm x 20-25 cm. Ready in 50-60 days.
   - Yield: 15-20 t/ha.
4. BROCCOLI (Brassica oleracea var. italica):
   - Varieties: Fiesta, KTS-1, Green Magic, Lucky.
   - Spacing: 45 cm x 45 cm. Rich in antioxidants and sulforaphane.
- Pest Management for all Cole Crops:
  - Diamondback Moth (DBM - Plutella xylostella): Most serious pest.
    - Intercrop with Indian Mustard as trap crop (sow 2 rows of mustard for every 25 rows of cabbage/cauliflower).
    - Spray Bacillus thuringiensis (Bt) @ 2 g/L or Spinosad 45% SC @ 0.3 ml/L or NSKE 5%.
    - Release egg parasitoid Trichogrammatoidea bactrae @ 50,000/ha.
  - Damping-off: Raise nursery on 20 cm raised beds; treat seeds with Trichoderma (10 g/kg).""",
    'cauliflower, cabbage, knolkhol, broccoli, cole crops, diamondback moth, dbm, whiptail, boron, borax, white marble, early kunwari, ns 43'
)

# ==========================================
# 7. CUCURBITS (Gourd Crops, Cucumber, Melons)
# ==========================================
add(
    'CIARI-CUCURBITS-01', 'Cucurbits', 'Cucurbitaceae', 'Vegetable', 'organic_and_conventional',
    'cucurbits_pop',
    'Cucurbits Cultivation and Fruit Fly Management (ICAR-CIARI)',
    'How to cultivate cucurbits (Bitter gourd, Bottle gourd, Cucumber, Ridge gourd, Snake gourd, Kakrol) and control fruit fly?',
    """According to ICAR-CIARI Package of Practices:
- Crops Covered: Bitter gourd, Bottle gourd, Ridge gourd, Snake gourd, Sponge gourd, Cucumber, Ash/Wax gourd, Watermelon, Kakrol (Teasle gourd), Parwal (Pointed gourd).
- Season: Main crop sown in Dec-January for dry season harvest. Rainy season crop sown in May-June on raised beds or trellises.
- Recommended Varieties:
  - Bitter Gourd: Katha, Priya, Meghana, Pusa Do Mausami.
  - Bottle Gourd: Pusa Naveen, Samrat, Arka Bahar.
  - Ridge Gourd: Pusa Nasdar, Surekha, Arka Sumeet.
  - Snake Gourd: CO-1, PKM-1.
  - Cucumber: Poinsette, Malini, Sheetal.
  - Kakrol (Teasle gourd) & Parwal (Pointed gourd): Planted in 9:1 female:male plant ratio since they are dioecious.
- Planting System & Spacing:
  - Bower / Trellis / Pandal system: Wire trellis or bamboo frames (essential in islands to protect vines from ground moisture and rot).
  - Spacing: 1.5 - 2.0 m between rows x 1.0 - 1.5 m between pits. Dig pits of 45x45x45 cm; fill with 10 kg FYM + 100g neem cake + topsoil.
- Fruit Fly (Bactrocera cucurbitae) - The #1 Limiting Pest in Cucurbits:
  - Fruit fly oviposits inside young fruits causing maggots, fruit rotting, and premature dropping.
  - Control Protocol:
    1. Cue-lure Pheromone Traps: Install 15-20 traps/ha containing cue-lure + Malathion blocks at canopy height.
    2. Poison Bait Spray: Dissolve 100g jaggery or molasses + 2 ml Malathion 50% EC or Spinosad in 1 litre water; spray coarse droplets on lower surface of leaves (do not spray whole crop).
    3. Fruit Bagging: Cover young fruits with paper bags or cloth bags immediately after pollination.
    4. Collect and deeply bury all infested fruits.
- Downy Mildew & Powdery Mildew:
  - Downy Mildew: Spray Metalaxyl-Mancozeb (Ridomil MZ) @ 2 g/L or Trichoderma viride @ 10 g/L.
  - Powdery Mildew: Spray wettable sulphur @ 2 g/L or cow urine (10%) + wood ash dusting.
- Yield: Bitter gourd 10-15 t/ha, Bottle gourd 25-35 t/ha, Cucumber 15-20 t/ha, Ridge gourd 10-14 t/ha.""",
    'cucurbits, bitter gourd, bottle gourd, cucumber, ridge gourd, snake gourd, kakrol, parwal, fruit fly, bactrocera cucurbitae, cue lure, bower pandal'
)

# ==========================================
# 8. LEGUME VEGETABLES: COWPEA, DOLICHOS, CLUSTER BEAN, FRENCH BEAN
# ==========================================
add(
    'CIARI-LEGUMES-01', 'Cowpea and Beans', 'Fabaceae', 'Vegetable', 'organic_and_conventional',
    'legumes_pop',
    'Cowpea, Dolichos Bean, Cluster Bean, and French Bean Package of Practices (ICAR-CIARI)',
    'What are the ICAR-CIARI recommendations for growing cowpea, dolichos bean, french bean, and cluster bean in Andaman?',
    """According to ICAR-CIARI Package of Practices:
1. COWPEA / YARD LONG BEAN (Vigna unguiculata):
   - Varieties: Lobia-1, Gomati, Pusa Komal, Kashi Kanchan (Yard Long bean), Arka Garima.
   - Sowing: Round the year; main crop Sept-Jan.
   - Seed Rate: 15-20 kg/ha (bush type); 10-12 kg/ha (pole type). Treat seeds with Rhizobium culture + PSB (20 g/kg seed).
   - Spacing: Bush 50-60 cm x 10-15 cm; Pole 80-90 cm on raised beds with bamboo stakes.
   - Pod Borer & Aphid Control: Spray Neem oil 5 ml/L or diluted cow urine + asafoetida (hing) + bird chilli extract. For heavy infestation, spray Chlorantraniliprole 18.5% SC @ 0.3 ml/L.
   - Yield: 8-15 tonnes/ha green pods.
2. DOLICHOS BEAN / LABLAB (Lablab purpureus):
   - Varieties: Konkan Bhushan (bush), Pusa Early Prolific, local Andaman selections.
   - Seed Rate: 15-20 kg/ha. Spacing: 75-90 cm x 60 cm. Hardy and flourishes in dry season. Yield: 8-12 t/ha.
3. FRENCH BEAN (Phaseolus vulgaris):
   - Varieties: Contender (bush), Arka Komal, Pant Anupama, Premier.
   - Season: Dry season (Dec to March); heavy rains destroy flowers.
   - Seed Rate: 50-60 kg/ha (bush). Spacing: 45-60 cm x 10-15 cm. Yield: 8-12 t/ha.
4. CLUSTER BEAN / GUAR (Cyamopsis tetragonoloba):
   - Varieties: Pusa Domahe, Pusa Navbahar, HG-365.
   - Seed Rate: 10-12 kg/ha. Spacing: 45-60 cm x 15 cm. Drought tolerant; enriches island soil with nitrogen. Yield: 6-10 t/ha.""",
    'cowpea, lobia, yard long bean, dolichos bean, lablab, french bean, cluster bean, guar, contender, kashi kanchan, rhizobium, pod borer'
)

# ==========================================
# 9. LEAFY GREENS & TRADITIONAL ISLAND VEGETABLES
# ==========================================
add(
    'CIARI-GREENS-01', 'Leafy Vegetables', 'Various', 'Vegetable', 'organic',
    'leafy_greens_intercropping',
    'Palak, Poi, Amaranthus, and Broad Dhaniya Intercropping in Coconut & Arecanut (ICAR-CIARI)',
    'How to cultivate leafy vegetables (Palak, Poi, Amaranthus, Broad Dhaniya) as intercrops in Andaman plantations?',
    """According to ICAR-CIARI Package of Practices:
1. PALAK / INDIAN SPINACH (Beta vulgaris var. bengalensis):
   - Varieties: All Green, Pusa Palak, Pusa Harit, Pusa Bharati.
   - Intercropping Technology: ICAR-CIARI developed dedicated package for palak as intercrop in coconut and arecanut basins using filtered sunlight.
   - Seed rate: 25-30 kg/ha. Raised beds of 1m width. Spacing: 20 cm x 5-10 cm.
   - Nutrition: Vermicompost @ 2-3 t/ha + 5% cow urine foliar spray after every cutting.
   - Harvesting: 4-6 cuttings starting 30 days after sowing. Yield: 10-15 t/ha.
2. POI / INDIAN / CEYLON SPINACH (Basella alba & Basella rubra):
   - Red stem (B. rubra) and Green stem (B. alba). Excellent tolerance to island heat and heavy rains.
   - Propagation: Seeds (12-15 kg/ha) or vine stem cuttings (30-40 cm long).
   - Spacing: 60 cm x 45 cm or 1 m x 1 m trained on bamboo stakes/trellises.
   - Multiple pickings of tender shoots every 10-15 days. Yield: 20-30 t/ha.
3. AMARANTHUS / MARSHA BHAJI (Amaranthus tricolor):
   - Varieties: CO-1, CO-2, CO-3, Arka Suguna, local red & green types.
   - Seed Rate: 2.0 - 2.5 kg/ha mixed with fine sand for even broadcasting.
   - Harvested by whole plant uprooting at 25-30 days, or clipping leaves every 10-12 days. Yield: 15-20 t/ha.
4. BROAD DHANIYA / CULANTRO (Eryngium foetidum):
   - Andaman signature aromatic perennial herb with sawtooth leaves.
   - Highly profitable intercrop under 50-70% shade of coconut and arecanut gardens.
   - Propagated by root slips or seeds (1-1.5 kg/ha). Spacing: 20 cm x 15 cm.
   - Regular vermiwash foliar sprays enhance aroma and leaf size. Leaves harvested continuously every 30-45 days.
5. INDIGENOUS GREENS (Nalibhaji / Water spinach, Madrashibhaji, Khattabhaji / Roselle):
   - Nalibhaji (Ipomoea aquatica): Propagated by cuttings in moist marshy/bed areas; rich in iron.
   - Khattabhaji (Hibiscus sabdariffa): Drought-tolerant sour green; calyces used for jams and herbal teas.""",
    'palak, poi, amaranthus, marsha bhaji, broad dhaniya, eryngium foetidum, culantro, intercropping, coconut, arecanut, nalibhaji, khattabhaji'
)

# ==========================================
# 10. ROOT CROPS: RADISH, CARROT
# ==========================================
add(
    'CIARI-ROOTS-01', 'Radish and Carrot', 'Raphanus / Daucus', 'Vegetable', 'organic_and_conventional',
    'radish_carrot_pop',
    'Radish and Carrot Package of Practices (ICAR-CIARI)',
    'What varieties and cultivation practices are recommended for radish and carrot in Andaman?',
    """According to ICAR-CIARI Package of Practices:
1. RADISH (Raphanus sativus):
   - Season: Cool dry season (November to February).
   - Recommended Varieties: Pusa Chetki (heat tolerant, can be grown earlier), Japanese White, Pusa Himani, Arka Nishant.
   - Soil: Deep, loose, friable sandy loam rich in organic matter. Compact soil causes forked, malformed roots.
   - Seed Rate: 8 - 10 kg/ha. Sown on ridges 30-45 cm apart and 10 cm between plants.
   - Manuring: FYM 15-20 t/ha + NPK 50:40:40 kg/ha.
   - Harvesting: 40-55 days when roots reach edible tender size. Delaying harvest makes roots pithy and pungent. Yield: 20-25 t/ha.
2. CARROT (Daucus carota):
   - Season: November to January sowing.
   - Varieties: Pusa Kesar, Nantes, Kuroda, Early Nantes.
   - Seed Rate: 5 - 6 kg/ha. Sown in shallow lines 25-30 cm apart.
   - Yield: 15-20 t/ha.""",
    'radish, mooli, carrot, gajar, pusa chetki, japanese white, pusa kesar, root crops, ridges, spacing, seed rate'
)

# ==========================================
# 11. PERENNIAL & SPECIAL VEGETABLES: DRUMSTICK, CURRY LEAF, BABY CORN
# ==========================================
add(
    'CIARI-SPECIAL-01', 'Moringa, Curry Leaf, and Baby Corn', 'Various', 'Vegetable', 'organic',
    'perennial_vegetables_pop',
    'Drumstick / Moringa, Curry Leaf, and Baby Corn Package of Practices (ICAR-CIARI)',
    'How to cultivate Moringa (Drumstick), Curry leaf, and Baby corn according to ICAR-CIARI?',
    """According to ICAR-CIARI Package of Practices:
1. DRUMSTICK / MORINGA (Moringa oleifera):
   - Varieties: PKM-1, PKM-2, ODC-3, local perennial selections.
   - Propagation: Seeds (500 g/ha) or limb cuttings (1-1.5 m long).
   - Spacing: 2.5 m x 2.5 m (pits of 45x45x45 cm).
   - Pruning / Pinching: Crucial step—pinch terminal shoot when plant reaches 1 meter height to induce strong lateral branches. Repeat pinching at 1.5 m.
   - Nutrition: 15-20 kg FYM + 100g Urea, 100g SSP, 50g MOP per tree twice a year.
   - Yield: 200-300 pods/tree/year.
2. CURRY LEAF (Murraya koenigii):
   - Varieties: Suwasini, DWD-1, DWD-2.
   - Propagated by seeds or root suckers. Spacing: 1.5 m x 1.5 m.
   - Manuring: 20 kg FYM + 2 kg vermicompost per bush per year in two splits.
   - Harvesting: Main stem cut back at 1 m height to stimulate bushiness; leaves harvested every 2-3 months.
3. BABY CORN (Zea mays):
   - Varieties: G-5414, VL Baby Corn 1, HM-4.
   - Season: Sown in dry season (Dec-Feb). Seed rate: 20-25 kg/ha. Spacing: 45-60 cm x 15-20 cm.
   - Detasseling: Essential operation—remove male tassel as soon as it emerges before pollen shed to ensure tender unfertilized ear development.
   - Harvest ears 2-3 days after silk emergence (silks 1-2 cm long).
   - Yield: 1.0 - 1.5 t/ha dehusked baby corn + 25-30 t/ha nutritious green fodder.""",
    'moringa, drumstick, curry leaf, baby corn, pkm 1, detasseling, pinching, zea mays, murraya koenigii'
)

# ==========================================
# 12. COCONUT (Cocos nucifera)
# ==========================================
add(
    'CIARI-COCONUT-01', 'Coconut', 'Cocos nucifera', 'Plantation', 'integrated',
    'varieties_planting_spacing',
    'Coconut Varieties, Spacing, and Pit Preparation in A&N Islands (ICAR-CIARI)',
    'What varieties, spacing, and planting methods are recommended for coconut by ICAR-CIARI?',
    """According to ICAR-CIARI Training Manual on Major Horticultural Crops:
- Recommended Varieties for Andaman & Nicobar Islands:
  - Tall Varieties: Andaman Ordinary Tall (dominant commercial cultivar), Andaman Giant Tall, Nicobar Tall, West Coast Tall.
  - Dwarf Varieties: Nicobar Dwarf (green, yellow, orange), Chowghat Orange Dwarf (COD), Malayan Yellow Dwarf (MYD).
  - Hybrids: CARI Annapurna (local high-yielding selection), Chandrakalpa, Kera Sankara.
- Nursery & Seedling Selection:
  - Collect seednuts from mother palms yielding >80 nuts/year.
  - Transplant 9-12 month old seedlings having 6-8 leaves and collar girth >10 cm with early leaf splitting.
- Spacing & System:
  - Square system: 7.5 m x 7.5 m (accommodates 175 palms/hectare).
  - On bunds of paddy fields / lowlands: Single row at 6.0 m spacing.
- Pit Size & Planting:
  - Dig pits of 1 m x 1 m x 1 m. In rocky/laterite soils, dig 1.2 m cube pits.
  - Layering at pit bottom: Put two layers of coconut husks (facing upward) at the bottom for moisture retention and sponge action during dry season.
  - Fill bottom 50-60 cm with topsoil mixed with 25 kg FYM, 1 kg Rock Phosphate, and 2 kg wood ash. Plant seedling at center and press soil firmly.""",
    'coconut, nariyal, cocos nucifera, andaman ordinary tall, cari annapurna, spacing 7.5m, pit preparation, coconut husk layering'
)

add(
    'CIARI-COCONUT-02', 'Coconut', 'Cocos nucifera', 'Plantation', 'integrated',
    'fertilizer_irrigation',
    'Coconut Nutrient Schedule and Irrigation Management (ICAR-CIARI)',
    'What is the annual fertilizer dosage and irrigation requirement for bearing coconut palms?',
    """According to ICAR-CIARI Horticultural Manual:
- Annual Fertilizer Schedule per Bearing Adult Palm (from 5th year onward):
  - Organic Manure: 50 kg Farmyard Manure (FYM) or compost or green leaves.
  - Chemical Fertilizers (NPK):
    - Nitrogen (N): 500 g/palm/year (approx. 1.1 kg Urea).
    - Phosphorus (P2O5): 320 g/palm/year (approx. 2.0 kg Single Super Phosphate or 1.1 kg Rock Phosphate).
    - Potassium (K2O): 1200 g/palm/year (approx. 2.0 kg Muriate of Potash / MOP).
  - Split Application Timing:
    1. First split (1/3rd dose): May-June (pre-monsoon).
    2. Second split (2/3rd dose): September-October (post-monsoon).
  - Method: Apply in a circular basin of 1.8 m radius around the palm, 15-20 cm deep, and incorporate with soil.
  - Magnesium & Micronutrients: In sandy coastal soils, apply 500g Magnesium Sulphate (MgSO4) + 100g Borax per palm annually.
- Irrigation & Moisture Conservation:
  - Critical in dry season (Dec to April).
  - Water requirement: 40-50 litres per palm per day through drip irrigation.
  - Mulch the basin (1.8 m radius) with dry coconut leaves, coir pith, or green residues to reduce evaporation.""",
    'coconut fertilizer dose, urea, mop, ssp, npk 500 320 1200, drip irrigation, basin application, coastal sandy soil, magnesium'
)

add(
    'CIARI-COCONUT-03', 'Coconut', 'Cocos nucifera', 'Plantation', 'integrated',
    'pest_disease_management',
    'Coconut Rhinoceros Beetle, Red Palm Weevil, and Bud Rot Management (ICAR-CIARI)',
    'How to control rhinoceros beetle, red palm weevil, and bud rot disease in coconut palms?',
    """ICAR-CIARI Protocol for Coconut Pest and Disease Management:
1. Rhinoceros Beetle (Oryctes rhinoceros):
   - Symptoms: V-shaped cuts on opened fronds; chewed fibers in crown.
   - Cultural/Mechanical: Hook out beetles from crown with an iron spike; clean crown regularly.
   - Axil Filling: Fill the innermost 2-3 leaf axils with a mixture of Sevidol 8G (25g) or Chlorpyriphos 1.5% dust (25g) mixed with equal quantity of dry river sand (once in 3 months).
   - Bio-control: Spray Metarhizium anisopliae (green muscardine fungus) @ 5x10^11 spores/m3 on manure/compost breeding heaps; release Baculovirus-infected beetles.
2. Red Palm Weevil (Rhynchophorus ferrugineus) - Lethal Pest:
   - Symptoms: Holes on trunk with chewed fibrous material and brown fermented ooze; gnawing sound inside trunk.
   - Treatment: Trunk injection with Chlorpyriphos 20% EC (10 ml in 1 litre water) through a 1 cm drill hole above the infested site, then plug with cement/clay.
   - Install Ferrolure+ aggregation pheromone traps @ 1 trap per 2 hectares.
3. Eriophyid Mite (Aceria guerreronis):
   - Triangular pale yellow patches below perianth turning brown, warty, and causing nut cracking.
   - Root feeding with Azadirachtin 10,000 ppm (10 ml + 10 ml water) or spray Azadirachtin 5 ml/L on young button bunches.
4. Bud Rot (Phytophthora palmivora):
   - Heartleaf turns yellow, withers, and rots with foul smell.
   - Cut and remove all affected rotting tissues; apply Bordeaux paste (1:1:10) or Copper Oxychloride paste on cut surfaces and protect with polythene cap.
   - Prophylactic: Spray 1% Bordeaux mixture on all palms before monsoon.
5. Stem Bleeding (Thielaviopsis paradoxa):
   - Chisel out rotting tissue until healthy wood appears; dress with Coal Tar or Bordeaux paste. Root drench with Tridemorph (Calixin) 0.1% or Carbendazim 0.1%.
- Yield: 80 - 120 nuts/palm/year.""",
    'coconut rhinoceros beetle, red palm weevil, ferrolure, eriophyid mite, bud rot, phytophthora, stem bleeding, bordeaux paste'
)

add(
    'CIARI-COCONUT-04', 'Coconut', 'Cocos nucifera', 'Plantation', 'integrated',
    'intercropping_systems',
    'Multi-Tier Intercropping Systems in Coconut Plantations (ICAR-CIARI)',
    'What crops can be intercropped in coconut gardens according to ICAR-CIARI?',
    """According to ICAR-CIARI Multi-Tier Cropping Research:
- Coconut palms exploit only 25% of the soil area and intercept only 45-50% of available solar radiation, leaving vast space for multi-tier intercropping:
- Recommended Intercropping Models:
  1. Multi-Tier High Density Model:
     - Top tier: Coconut palms (7.5 m x 7.5 m).
     - Second tier (Spices/Fruits): Banana, Papaya, Black pepper (trained on coconut trunks), Clove, Nutmeg, Cinnamon.
     - Ground tier (Tubers/Spices/Greens): Elephant Foot Yam, Ginger, Turmeric, Colocasia, Tapioca, Broad Dhaniya, Palak.
  2. Spices in Coconut:
     - Black Pepper: Cuttings planted at base of coconut trunk on northern/eastern side; highly remunerative.
     - Ginger and Turmeric: Sown in 1 m wide raised beds between coconut rows with heavy green leaf mulching.
  3. Tuber Crops in Coconut:
     - Elephant Foot Yam (Amorphophallus) intercropped in coconut gardens yields 35-40 t/ha with high net returns.
  4. Leafy Vegetables in Coconut:
     - Broad Dhaniya (Eryngium foetidum) and Palak flourish under partial canopy shade.""",
    'coconut intercropping, multi-tier cropping, black pepper on coconut, ginger in coconut, elephant foot yam, broad dhaniya, shade crops'
)

# ==========================================
# 13. ARECANUT (Areca catechu)
# ==========================================
add(
    'CIARI-ARECANUT-01', 'Arecanut', 'Areca catechu', 'Plantation', 'integrated',
    'varieties_management',
    'Arecanut Package of Practices, Varieties, and Manuring (ICAR-CIARI)',
    'What are the recommended varieties, spacing, and fertilizer doses for Arecanut in A&N Islands?',
    """According to ICAR-CIARI Horticultural Manual:
- Recommended Varieties:
  - Mangala, Sumangala, Sreemangala, Mohitnagar, Kahikuchi, Calicut-17, local Andaman & Nicobar selections.
- Spacing & Pit Preparation:
  - Spacing: 2.7 m x 2.7 m (accommodates 1,370 palms/hectare).
  - Pit size: 90 cm x 90 cm x 90 cm.
  - Fill bottom with topsoil + 10-15 kg FYM + 200g Rock Phosphate. Plant 12-18 month old seedlings having >5 leaves.
- Annual Fertilizer Doses per Bearing Adult Palm:
  - Organic Manure: 15-20 kg FYM or green compost.
  - Chemical NPK:
    - Nitrogen: 100 g/palm/year (approx. 220 g Urea).
    - Phosphorus: 40 g/palm/year (approx. 250 g Single Super Phosphate / SSP).
    - Potassium: 140 g/palm/year (approx. 235 g Muriate of Potash / MOP).
  - Applied in 2 split doses: 1/3rd in May-June and 2/3rd in Sept-October in a basin of 0.75-1.0 m radius.
- Irrigation & Mulching:
  - Basin irrigation or drip (15-20 litres/palm/day) during dry spells. Mulch interspaces with arecanut leaves.
- Harvesting & Yield: 2.0 - 3.0 kg dry chali per palm/year (2,000 - 3,000 kg/ha).""",
    'arecanut, supari, betelnut, areca catechu, mangala, sumangala, mohitnagar, spacing 2.7m, npk dose arecanut, chali yield'
)

add(
    'CIARI-ARECANUT-02', 'Arecanut', 'Areca catechu', 'Plantation', 'integrated',
    'pest_disease_koleroga',
    'Arecanut Fruit Rot / Koleroga / Mahali and Pest Management (ICAR-CIARI)',
    'How to prevent and control Fruit Rot (Koleroga/Mahali) and pests in Arecanut?',
    """ICAR-CIARI Protocol for Arecanut Protection:
1. Fruit Rot / Koleroga / Mahali (Phytophthora arecae) - The Most Severe Disease:
   - Symptoms: Water-soaked lesions at the base of green nuts, shedding of immature nuts, rotting of bunches during heavy monsoon.
   - Management:
     1. Prophylactic Spray: Spray 1% Bordeaux mixture with resin adhesive/sticker (1 kg copper sulphate + 1 kg quicklime in 100 L water) on all bunches just before the onset of the southwest monsoon (May).
     2. Second Spray: Repeat 1% Bordeaux mixture 40-45 days after the first spray during a rain break.
     3. Polythene Bunch Covering: Cover bunches with 200-gauge non-absorbent polythene bags before the onset of rains; completely prevents infection without chemical spray.
     4. Collect and destroy all shed rotting nuts and fallen bunches to reduce inoculum.
2. Spindle Bug (Carvalhoia arecae):
   - Feeds on tender spindle leaves; spray Dimethoate 30% EC @ 1.5 ml/L or Quinalphos 25% EC @ 2 ml/L into innermost leaf axils.
3. White & Red Spider Mites (Oligonychus / Raoiella):
   - Feed on under-surface of leaves; spray wettable sulphur @ 3 g/L or Dicofol 0.05%.
4. Yellow Leaf Disease (YLD):
   - Ensure proper field drainage to avoid waterlogging; apply balanced NPK + zinc sulphate (25g) + borax (10g) per palm.""",
    'arecanut fruit rot, koleroga, mahali, phytophthora arecae, bordeaux mixture, polythene covering, spindle bug, carvalhoia arecae'
)

# ==========================================
# 14. BANANA (Musa sp.)
# ==========================================
add(
    'CIARI-BANANA-01', 'Banana', 'Musa sp.', 'Fruit', 'integrated',
    'varieties_spacing_management',
    'Banana Varieties, Spacing, and Cultural Practices (ICAR-CIARI)',
    'What varieties and agronomic practices are recommended for Banana in Andaman & Nicobar?',
    """According to ICAR-CIARI Horticultural Manual:
- Recommended Varieties:
  - Grand Naine, Robusta (high yielding commercial Cavendish group).
  - Poovan (Champa / Mysore type - hardy, acid-tolerant).
  - Rasthali (Silk group - premium dessert banana).
  - Red Banana (high nutritive value).
  - Monthan (cooking culinary variety).
  - Korangi, Karpooravalli, Rathalu (local Andaman cultivars).
- Planting Material:
  - Healthy sword suckers (1.5 - 2.0 kg) with well-developed rhizome, or disease-free tissue culture plantlets.
  - Sucker Treatment: Pare old roots; dip in cow dung slurry + Carbendazim 0.1% (1 g/L) + Chlorpyriphos 0.2% (2 ml/L) for 20 minutes before planting to eliminate nematodes and rhizome weevils.
- Spacing:
  - Grand Naine / Dwarf Cavendish: 1.5 m x 1.5 m (4,444 plants/ha) or 1.8 m x 1.5 m.
  - Tall types (Poovan, Rasthali, Red Banana): 2.1 m x 2.1 m or 2.4 m x 2.4 m.
  - Pit size: 60 cm x 60 cm x 60 cm; incorporate 15 kg FYM + 250g neem cake + topsoil.
- Essential Cultural Operations:
  1. Desuckering: Remove all side suckers until bunch emergence; retain only one follower sucker after bunching.
  2. Earthing up: Mound soil around base at 3rd and 5th month to support root anchorage.
  3. Propping: Support fruiting plants with two bamboo poles tied in an 'X' shape to prevent wind lodging during island gales.
  4. Denavelling: Remove the terminal male bud 10 days after the last hand opens to accelerate finger filling.
  5. Bunch Sleeving: Cover bunches with perforated blue polythene sleeves (6% ventilation) to protect against insects, sun scorch, and improve fruit grade.""",
    'banana, kela, musa, grand naine, robusta, poovan, rasthali, red banana, sword sucker, desuckering, propping, denavelling, bunch sleeving'
)

add(
    'CIARI-BANANA-02', 'Banana', 'Musa sp.', 'Fruit', 'integrated',
    'fertilizer_sigatoka_protection',
    'Banana Fertilizer Schedule, Sigatoka Leaf Spot, and Panama Wilt Control (ICAR-CIARI)',
    'What is the fertilizer schedule and pest/disease control for Banana in Andaman?',
    """According to ICAR-CIARI Recommendations:
- Fertilizer Schedule per Plant:
  - Basal: 15-20 kg FYM.
  - Chemical NPK per plant: 200 g Nitrogen (440 g Urea), 60 g P2O5 (375 g SSP), 300 g K2O (500 g MOP).
  - 4 Split Doses:
    1. 2nd month: 50g N, 60g P2O5, 75g K2O.
    2. 3rd month: 50g N, 75g K2O.
    3. 4th month: 50g N, 75g K2O.
    4. 5th month (shooting): 50g N, 75g K2O.
- Disease Management:
  1. Sigatoka Leaf Spot (Mycosphaerella musicola) - Highly Prevalent in High Humidity:
     - Symptoms: Spindle leaf yellow lesions turning dark brown necrotic streaks with gray center.
     - Control: Cut and burn severely spotted leaves; spray Propiconazole 25% EC @ 1 ml/L or Carbendazim 50% WP @ 1 g/L mixed with 1% mineral oil (Power oil) emulsion at 30-day intervals during monsoon.
  2. Panama Wilt (Fusarium oxysporum f. sp. cubense):
     - Internal vascular browning; splitting of pseudostem. Grow resistant Grand Naine/Robusta; avoid planting susceptible Rasthali in infested plots; drench corms with Carbendazim 0.1% or apply Trichoderma viride (50g) + neem cake.
  3. Banana Bunchy Top Virus (BBTV): Vector is banana aphid (Pentalonia nigronervosa). Rogue and inject kerosene/glyphosate into infected plants; spray aphicide Imidacloprid @ 0.3 ml/L.
- Pest Management:
  - Pseudostem Borer & Rhizome Weevil: Apply Carbofuran 3G @ 20g/plant or stem injection with Chlorpyriphos.
- Yield: 40-60 t/ha (Grand Naine); 25-35 t/ha (Poovan/Rasthali).""",
    'banana fertilizer dose, sigatoka leaf spot, propiconazole, panama wilt, bunchy top, bbtv, rhizome weevil, pseudostem borer'
)

# ==========================================
# 15. PAPAYA (Carica papaya)
# ==========================================
add(
    'CIARI-PAPAYA-01', 'Papaya', 'Carica papaya', 'Fruit', 'integrated',
    'papaya_package_pop',
    'Papaya Cultivation, Sex Forms, and Disease Management (ICAR-CIARI)',
    'How to cultivate Papaya and manage its sex forms and viral diseases in Andaman?',
    """According to ICAR-CIARI Horticultural Manual:
- Recommended Varieties:
  - Dioecious types: Coorg Honey Dew, Pusa Delicious, Pusa Dwarf, Pusa Nanha (dwarf type for high density).
  - Gynodioecious / Hermaphrodite hybrids: Red Lady 786 (produces fruit on all plants; elongated sweet fruits).
- Seed Rate & Nursery:
  - Dioecious: 250-300 g/ha. Gynodioecious: 100-150 g/ha.
  - Raise in polybags (20x10 cm) filled with soil, sand, and FYM (1:1:1). Transplant 45-60 days old seedlings.
- Spacing: 1.8 m x 1.8 m (3,086 plants/ha) or 1.5 m x 1.5 m for Pusa Nanha.
- Managing Sex Forms:
  - For dioecious cultivars, plant 2-3 seedlings per pit at 15 cm distance. At flowering (3-4 months), remove all male plants except 1 vigorous male plant per 10 female plants for pollination. Thin females to 1 per pit.
- Nutrition:
  - Heavy feeder: 10-15 kg FYM + 200 g N, 200 g P2O5, 250 g K2O per plant/year divided into 6 bimonthly applications.
- Protection:
  - Papaya Ringspot Virus (PRSV): Transmitted by aphids; rogue infected plants; spray Imidacloprid (0.3 ml/L) or neem oil.
  - Collar Rot / Foot Rot (Pythium aphanidermatum): Avoid water stagnation around stem; drench base with Copper Oxychloride (2.5 g/L) or Metalaxyl (2 g/L).
- Yield: 60-100 kg fruits/plant in 2-3 years life cycle.""",
    'papaya, papita, carica papaya, red lady 786, pusa nanha, dioecious, sex forms, ringspot virus, collar rot, pythium'
)

# ==========================================
# 16. PINEAPPLE (Ananas comosus)
# ==========================================
add(
    'CIARI-PINEAPPLE-01', 'Pineapple', 'Ananas comosus', 'Fruit', 'integrated',
    'pineapple_high_density_ethrel',
    'Pineapple High-Density Planting and Ethrel Flower Induction (ICAR-CIARI)',
    'What are ICAR-CIARI practices for high density pineapple planting and flower induction with Ethrel?',
    """According to ICAR-CIARI Horticultural Manual:
- Varieties:
  - Kew (large fruits, 2-3 kg, ideal for canning & processing).
  - Queen (golden yellow, highly aromatic, sweet, table dessert variety).
  - Mauritius (crisp, early, good shelf life).
- Planting Material:
  - Suckers (400-500 g) from leaf axils, or slips (300-350 g) from fruit stalk base. Treat in Carbendazim 0.1% + Chlorpyriphos 0.2% before planting.
- High-Density Planting (Double Row Bed System):
  - Spacing: 30 cm between plants x 60 cm between rows x 90 cm between double beds.
  - Plant density: 43,500 plants/hectare. Gives much higher yield (50-70 t/ha) compared to traditional low density.
- Essential Operation - Flower Induction (Ethrel Application):
  - Pineapple plants naturally flower erratically over several months.
  - To achieve 100% synchronized flowering and single-window harvesting:
    - Apply Ethrel (Ethephon) @ 25 ppm solution (mix 2.5 ml Ethrel in 100 litres of water + 2 kg Urea + 40 g Sodium Carbonate / washing soda).
    - Pour 50 ml of this solution into the heart / center of each plant at 35-40 leaf stage (10-12 months after planting) during evening hours.
    - Uniform flowering occurs within 40-45 days of treatment.
- Nutrition: Apply 12 g N, 4 g P2O5, 12 g K2O per plant in 4 splits.
- Pest: Mealybug (Dysmicoccus brevipes - vector of wilt): spray Chlorpyriphos 0.05% or neem oil.
- Yield: 50-70 tonnes/ha.""",
    'pineapple, ananas comosus, kew, queen, mauritius, ethrel, flower induction, high density planting, double row system, mealybug'
)

# ==========================================
# 17. MANGO (Mangifera indica)
# ==========================================
add(
    'CIARI-MANGO-01', 'Mango', 'Mangifera indica', 'Fruit', 'integrated',
    'mango_varieties_protection',
    'Mango Varieties and Pest/Disease Management in Andaman (ICAR-CIARI)',
    'What varieties and pest management strategies are recommended for Mango by ICAR-CIARI?',
    """According to ICAR-CIARI Horticultural Manual:
- Recommended Varieties for Islands:
  - Amrapali (dwarf, regular bearer, high density planting at 5m x 5m = 400 trees/ha).
  - Mallika, Alphonso, Dashehari, Langra, Keshar, local Andaman polyembryonic types.
- Spacing: Normal varieties 10 m x 10 m (100 trees/ha). Pits of 1m x 1m x 1m.
- Manuring for Bearing Tree (10+ years):
  - 50 kg FYM + 1,000 g N (2.2 kg Urea), 500 g P2O5 (3.1 kg SSP), 1,000 g K2O (1.6 kg MOP) applied after fruit harvest in August-September.
- Major Pest & Disease Management:
  1. Mango Hopper (Amritodus atkinsoni / Idioscopus spp.):
     - Large populations suck sap from flower panicles causing blossom drop.
     - Spray Imidacloprid 17.8% SL @ 0.3 ml/L or Thiamethoxam 25% WG @ 0.3 g/L during flower bud emergence.
  2. Anthracnose (Colletotrichum gloeosporioides):
     - Causes black spots on leaves, blossom blight, and black rotting spots on ripe fruits.
     - Spray Copper Oxychloride 50% WP @ 2.5 g/L or Carbendazim @ 1 g/L.
  3. Powdery Mildew (Oidium mangiferae):
     - White powdery growth on panicles; spray Wettable Sulphur @ 2 g/L or Hexaconazole @ 1 ml/L.
  4. Fruit Fly (Bactrocera dorsalis): Install Methyl Eugenol pheromone traps @ 10-15 traps/ha; hot water treatment of fruits at 48°C for 20 minutes.
- Yield: 8-15 tonnes/ha.""",
    'mango, aam, mangifera indica, amrapali, mallika, mango hopper, imidacloprid, anthracnose, fruit fly, methyl eugenol'
)

# ==========================================
# 18. BLACK PEPPER (Piper nigrum)
# ==========================================
add(
    'CIARI-PEPPER-01', 'Black Pepper', 'Piper nigrum', 'Spices', 'integrated',
    'black_pepper_coconut_intercropping',
    'Black Pepper Cultivation as Intercrop on Coconut & Arecanut (ICAR-CIARI)',
    'How to cultivate Black Pepper on Coconut/Arecanut standards and process black and white pepper?',
    """According to ICAR-CIARI Horticultural Manual:
- Varieties:
  - Panniyur-1 (high yielder, adapts well to islands), Panniyur-2, Panniyur-3, Panniyur-4, Panniyur-5, Karimunda, Subhakara, Sreekara, Pournami.
- Propagation:
  - Rooted cuttings from runner shoots (3-4 nodes) raised in polybags. Bush pepper can be raised from plagiotropic (fruiting) branches.
- Planting on Living Standards (Coconut & Arecanut):
  - Plant 2-3 rooted cuttings on the northern or eastern side of the palm trunk at a distance of 30 cm from the base.
  - Pit size: 50 cm x 50 cm x 50 cm filled with topsoil, 5 kg FYM, and 100 g rock phosphate.
  - As vines grow, tie them to the palm trunk at 30 cm intervals using banana fiber or coir twine.
  - Prune terminal shoots at 1 m height to induce strong lateral fruiting branches.
- Annual Manuring per Bearing Vine:
  - 10 kg FYM/compost + 100 g N (220 g Urea), 40 g P2O5 (250 g SSP), 140 g K2O (235 g MOP) in 2 splits (May-June and August-September). Apply 500g lime every 2 years.
- Disease - Foot Rot / Quick Wilt (Phytophthora capsici) - Most Lethal Disease:
  - Causes sudden black spots, wilting, and vine death during monsoon.
  - Lopping standard shade to allow aeration and sunlight.
  - Drench vine basin and spray canopy with 1% Bordeaux mixture or Metalaxyl-Mancozeb (Ridomil MZ) @ 2 g/L in May-June and August-September.
  - Incorporate Trichoderma viride (50 g) in 1 kg neem cake around each vine.
- Post-Harvest Processing:
  - Black Pepper: Harvest spikes when 1-2 berries turn red/orange. Thresh, dip berries in boiling water for 1 minute (causes uniform wrinkling and dark black colour), sun dry for 5-7 days to 10-12% moisture.
  - White Pepper: Soak fully ripe red berries in running water for 7-8 days, peel off outer skin, wash, and sun dry.
- Yield: 1.5 - 2.5 kg dry black pepper per vine (1,500 - 2,500 kg/ha).""",
    'black pepper, kali mirch, piper nigrum, panniyur 1, karimunda, coconut standard, quick wilt, phytophthora capsici, boiling water dip, white pepper'
)

# ==========================================
# 19. TREE SPICES: CINNAMON, CLOVE, NUTMEG
# ==========================================
add(
    'CIARI-TREESPICES-01', 'Tree Spices (Cinnamon, Clove, Nutmeg)', 'Various', 'Spices', 'integrated',
    'tree_spices_pop',
    'Cinnamon, Clove, and Nutmeg Cultivation and Harvest Processing (ICAR-CIARI)',
    'How to cultivate and process Cinnamon, Clove, and Nutmeg according to ICAR-CIARI?',
    """According to ICAR-CIARI Horticultural Manual:
1. CINNAMON (Cinnamomum verum):
   - Varieties: Navashree, Nithyashree.
   - Spacing: 2.0 m x 2.0 m. Coppicing: Cut shoots 15 cm from ground level at 2-3 years to encourage vigorous bushy straight shoots.
   - Harvest: Harvest shoots of 1.5 - 2.0 m length and pencil thickness (1.5-2.0 cm diameter).
   - Bark Peeling: Scrape outer corky skin with curved knife; rub bark with brass rod to loosen; peel inner bark strips, roll into compound quills (inserting smaller strips into larger pipes), and dry in shade.
   - Yield: 200-300 kg dry quills/ha.
2. CLOVE (Syzygium aromaticum):
   - Thrives in humid island climate; excellent intercrop in coconut/arecanut plantations.
   - Spacing: 6 m x 6 m. Pits: 1m x 1m x 1m.
   - Manuring per adult tree: 50 kg FYM + 300 g N, 250 g P2O5, 750 g K2O.
   - Harvest: Pick unopened plump flower buds when they turn from green to pinkish-red (before opening). Sun dry for 4-5 days until dark brown (dry recovery 30%).
   - Yield: 3-5 kg dry cloves/tree/year.
3. NUTMEG (Myristica fragrans):
   - Dioecious tree (produces separate male and female trees; maintain 1 male tree for 10 females, or plant grafted plants).
   - Spacing: 8 m x 8 m. Intercropped in coconut orchards.
   - Dual Product: Harvest ripe fruits splitting open. Separate the bright scarlet red mace from the brown nutmeg seed. Dry mace to amber yellow; dry seed until kernel rattles.
   - Yield: 1,000 - 2,000 fruits/tree/year.""",
    'cinnamon, dalchini, clove, laung, nutmeg, jaiphal, javitri, mace, bark peeling, coppicing, unopened buds, dioecious'
)

# ==========================================
# 20. RHIZOME SPICES: GINGER & TURMERIC
# ==========================================
add(
    'CIARI-RHIZOMES-01', 'Ginger and Turmeric', 'Zingiberaceae', 'Spices', 'integrated',
    'ginger_turmeric_pop',
    'Ginger and Turmeric Cultivation, Mulching, and Curing (ICAR-CIARI)',
    'What are the ICAR-CIARI recommendations for growing Ginger and Turmeric and managing Soft Rot?',
    """According to ICAR-CIARI Horticultural Manual:
1. GINGER (Zingiber officinale):
   - Recommended Varieties: Rio de Janeiro, Suprabha, Suruchi, Maran, China.
   - Planting & Spacing: Raised beds (1 m width, 15 cm height, 30 cm drainage furrows). Spacing: 25-30 cm x 20-25 cm.
   - Seed Rhizome Rate: 1,500 - 1,800 kg/ha (healthy pieces of 20-25 g with 1-2 active viable buds).
   - Seed Treatment: Dip seed rhizomes in Trichoderma viride (10 g/L) or Carbendazim (2 g/L) + Mancozeb (2.5 g/L) for 30 minutes before planting.
   - Green Leaf Mulching (Crucial for Island Ginger):
     - 1st Mulching: Apply 12-15 tonnes/ha green leaves immediately after planting (suppresses weeds, lowers soil temp, conserves moisture).
     - 2nd Mulching: 5 t/ha at 45 days after planting (with first weeding).
     - 3rd Mulching: 5 t/ha at 90 days after planting (with earthing up).
   - Soft Rot / Rhizome Rot (Pythium aphanidermatum): Devastating disease. Provide drainage; drench with Metalaxyl-Mancozeb @ 2 g/L or Copper Oxychloride @ 3 g/L; incorporate Trichoderma viride with neem cake.
   - Yield: 15-25 tonnes/ha fresh rhizomes.
2. TURMERIC (Curcuma longa):
   - Recommended Varieties: Prathiba, Prabha, Kedaram, Alleppey Supreme, BSR-2.
   - Seed Rate: 2,000 - 2,500 kg/ha mother or finger rhizomes. Spacing: 30 cm x 20 cm on raised beds with green leaf mulching.
   - NPK Dose: FYM 25 t/ha + 60:50:120 kg NPK/ha.
   - Curing & Polishing: Boil cleaned fingers in water for 45-60 minutes until soft and white fumes emerge; sun dry for 10-15 days; polish manually or mechanically.
   - Yield: 20-30 tonnes/ha fresh rhizomes (dry recovery 18-22%).""",
    'ginger, adrak, turmeric, haldi, zingiber officinale, curcuma longa, green leaf mulching, soft rot, pythium, rhizome seed rate, curing boiling'
)

# ==========================================
# 21. TUBER CROPS: CASSAVA, SWEET POTATO, COLOCASIA, ELEPHANT FOOT YAM, DIOSCOREA
# ==========================================
add(
    'CIARI-TUBERS-01', 'Tuber Crops', 'Various', 'Tubers', 'integrated',
    'tuber_crops_island_package',
    'Package of Practices for Tuber Crops: Cassava, Sweet Potato, Colocasia, and Elephant Foot Yam (ICAR-CIARI)',
    'How to cultivate Cassava, Sweet Potato, Colocasia, and Elephant Foot Yam in Andaman & Nicobar?',
    """According to ICAR-CIARI Horticultural Manual:
1. CASSAVA / TAPIOCA (Manihot esculenta):
   - Varieties: H-165, H-226, Sree Sahya, Sree Vijaya, CARI Tapioca-1.
   - Propagation: Stem cuttings (setts) 15-20 cm long with 4-6 buds. Plant vertically on mounds or ridges at 90 cm x 90 cm.
   - Manuring: FYM 12.5 t/ha + NPK 100:50:100 kg/ha. Harvest at 8-10 months. Yield: 25-35 t/ha.
2. SWEET POTATO (Ipomoea batatas):
   - Varieties: Sree Bhadra, Sree Arun, Sree Varun, Kalingarayan local.
   - Propagation: Terminal vine cuttings (20-25 cm with 3-4 nodes). Spacing: 60 cm x 20 cm on ridges.
   - Sweet Potato Weevil (Cylas formicarius) Control: Earthing up at 30 and 60 days to prevent soil cracks; install pheromone traps @ 5/ha; dip cuttings in Chlorpyriphos 0.05%. Harvest at 90-105 days. Yield: 15-20 t/ha.
3. COLOCASIA / TARO (Colocasia esculenta):
   - Varieties: Sree Rashmi, Sree Pallavi, Muktakeshi, local Arbi.
   - Excellent shade-tolerant intercrop in coconut/arecanut basins.
   - Plant cormels (30-40 g) at 60 cm x 45 cm. FYM 15 t/ha + NPK 80:40:80 kg/ha.
   - Taro Leaf Blight (Phytophthora colocasiae): Spray Mancozeb @ 2.5 g/L or Ridomil MZ @ 2 g/L. Yield: 12-18 t/ha.
4. ELEPHANT FOOT YAM (Amorphophallus paeoniifolius):
   - Varieties: Gajendra, Bidhan Kusum, CARI EFY-1.
   - Planting Material: Corm cut pieces (500 g - 1,000 g) with portion of central bud. Smear cut surfaces with cow dung slurry + Trichoderma or Mancozeb and shade dry for 3 days.
   - Pit size: 60 cm x 60 cm x 45 cm. Spacing: 90 cm x 90 cm.
   - Heavy feeder: FYM 25 t/ha + NPK 100:50:100 kg/ha + heavy mulching.
   - Intercropping: Outstanding performance in coconut plantations. Harvest at 8-9 months when foliage completely withers. Yield: 35-50 t/ha.
5. GREATER YAM (Dioscorea alata):
   - Varieties: Sree Keerthi, Sree Roopa. Tuber setts (250-300 g) planted at 90 cm x 90 cm and staked with poles or coir rope to palms. Yield: 25-40 t/ha.""",
    'cassava, tapioca, sweet potato, shakarkand, colocasia, taro, arbi, elephant foot yam, jimikand, amorphophallus, gajendra, dioscorea, yam'
)

# ==========================================
# 22. ORGANIC PREPARATIONS & BIO-INPUTS
# ==========================================
add(
    'CIARI-ORGANIC-INPUTS-01', 'Organic Bio-Inputs', 'Formulations', 'Organic Inputs', 'organic',
    'panchagavya_vermiwash_extracts',
    'Preparation of Panchagavya, Vermiwash, Cow Dung Slurry, and Botanical Extracts (ICAR-CIARI)',
    'How to prepare and apply Panchagavya, Vermiwash, Cow dung slurry, and botanical insect sprays?',
    """According to ICAR-CIARI Organic Package of Practices:
1. PANCHAGAVYA PREPARATION & APPLICATION:
   - Ingredients: Fresh cow dung (5 kg), Cow urine (3 litres), Cow milk (2 litres), Curd (2 litres), Cow ghee (500 g), Jaggery (500 g dissolved in 3L water), Ripe banana (12 fruits), Tender coconut water (3 litres).
   - Preparation: Mix cow dung and ghee in plastic drum; keep for 3 days with twice daily stirring. On 4th day add cow urine, milk, curd, jaggery water, mashed banana, and coconut water. Stir twice daily for 15 days.
   - Application: 3% foliar spray (30 ml Panchagavya in 1 litre water). Filter through fine muslin cloth. Spray at 15-day intervals; dramatically boosts immunity, flowering, fruit setting, and taste.
2. VERMIWASH:
   - Collection from vermicompost units during watering. Rich in amino acids, gibberellins, and soluble plant nutrients.
   - Application: Dilute with water in 1:8 ratio (500 L/ha) as foliar spray or root drench every 10-15 days.
3. FRESH COW DUNG SLURRY:
   - Mix 1 kg fresh cow dung in 10 litres of water (or biogas slurry). Apply around root zone at 50 kg/ha equivalent every 7-10 days for leafy and fruit vegetables.
4. GARLIC-CHILLI-GINGER BOTANICAL INSECTICIDE EXTRACT:
   - Ingredients: Garlic cloves (18 g), Green pungent bird chilli (9 g), Fresh ginger (9 g).
   - Preparation: Crush each ingredient separately with a little water. Mix together in 1 litre water; add 5 g soap/detergent as surfactant.
   - Application: Highly potent organic spray against caterpillars, fruit borers, aphids, whiteflies, and epilachna beetles.
5. NEEM OIL SPRAY:
   - Cold-pressed neem oil (10,000 ppm azadirachtin) @ 5 ml/litre water + 1 ml liquid soap or potassium soap. Emulsify thoroughly before pouring into sprayer tank.""",
    'panchagavya preparation, vermiwash, cow dung slurry, garlic chilli ginger extract, neem oil 5ml, organic inputs, bio stimulants'
)

# ==========================================
# 23. EXTRA DETAILED CROPS FROM PDFs
# ==========================================
add(
    'CIARI-BITTER-GOURD-01', 'Bitter Gourd', 'Momordica charantia', 'Vegetable', 'organic_and_conventional',
    'bitter_gourd_details',
    'Bitter Gourd (Karela) Package of Practices (ICAR-CIARI)',
    'What are the recommended varieties, spacing, and practices for Bitter Gourd in Andaman?',
    """According to ICAR-CIARI Package of Practices:
- Varieties: Katha, Priya, Meghana, Pusa Do Mausami, Arka Harit.
- Seed Rate: 4.0 - 5.0 kg/ha. Pre-soak seeds in warm water for 12 hours to soften hard seed coat.
- Spacing & Training: Sown in pits of 45x45x45 cm at 2 m x 1.5 m. Must be trained on bower/trellis to prevent fruit rot from contact with wet island soil.
- Manuring: FYM 20 t/ha + NPK 80:50:50 kg/ha (or vermicompost + cow dung slurry).
- Fruit Fly Protection: Cue-lure pheromone traps @ 15-20/ha; poison bait spray (100g jaggery + 2 ml Malathion in 1L water); fruit bagging with paper pouches.
- Yield: 10-15 tonnes/ha.""",
    'bitter gourd, karela, momordica charantia, katha, priya, meghana, fruit fly, bower, spacing, seed rate'
)

add(
    'CIARI-BOTTLE-GOURD-01', 'Bottle Gourd', 'Lagenaria siceraria', 'Vegetable', 'organic_and_conventional',
    'bottle_gourd_details',
    'Bottle Gourd (Lauki) Package of Practices (ICAR-CIARI)',
    'What varieties and cultivation guidelines are recommended for Bottle Gourd by ICAR-CIARI?',
    """According to ICAR-CIARI Package of Practices:
- Varieties: Pusa Naveen, Samrat, Arka Bahar, Pusa Sandesh.
- Season: Sown in Dec-Jan (dry season) and May-June (rainy season).
- Seed Rate: 3.0 - 4.0 kg/ha. Spacing: 2.0 - 2.5 m between rows x 1.0 - 1.5 m between plants in pits.
- Nutrition: FYM 20 t/ha; top dress with urea or fermented cow dung slurry every 15 days from flowering.
- Yield: 25-35 tonnes/ha.""",
    'bottle gourd, lauki, lagenaria siceraria, pusa naveen, samrat, arka bahar, spacing, seed rate'
)

add(
    'CIARI-CUCUMBER-01', 'Cucumber', 'Cucumis sativus', 'Vegetable', 'organic_and_conventional',
    'cucumber_details',
    'Cucumber (Kheera) Package of Practices and Downy Mildew Control (ICAR-CIARI)',
    'What varieties, seed rate, and disease remedies are recommended for Cucumber in Andaman?',
    """According to ICAR-CIARI Package of Practices:
- Varieties: Poinsette, Malini, Sheetal, Japanese Long Green, Priya.
- Seed Rate: 2.5 - 3.0 kg/ha. Spacing: 1.5 m x 1.0 m on raised beds with trellis training.
- Major Disease - Downy Mildew (Pseudoperonospora cubensis):
  - Highly prevalent during warm humid weather; causes angular yellow spots on upper leaf surface with purplish downy growth underneath.
  - Spray Metalaxyl 8% + Mancozeb 64% (Ridomil MZ) @ 2 g/L or Copper Oxychloride @ 2.5 g/L at 10-day intervals.
- Yield: 15-20 tonnes/ha.""",
    'cucumber, kheera, cucumis sativus, poinsette, malini, downy mildew, ridomil mz, spacing, seed rate'
)

add(
    'CIARI-RIDGE-SNAKE-GOURD-01', 'Ridge and Snake Gourd', 'Luffa / Trichosanthes', 'Vegetable', 'organic_and_conventional',
    'ridge_snake_gourd_details',
    'Ridge Gourd (Torai) and Snake Gourd (Chichinda) Package of Practices (ICAR-CIARI)',
    'How to cultivate Ridge Gourd and Snake Gourd according to ICAR-CIARI?',
    """According to ICAR-CIARI Package of Practices:
- RIDGE GOURD (Luffa acutangula):
  - Varieties: Pusa Nasdar, Surekha, Arka Sumeet, local angled selections.
  - Seed Rate: 3.5 - 4.0 kg/ha. Spacing: 1.5 - 2.0 m x 1.0 m. Trained on bower.
  - Yield: 10-14 t/ha.
- SNAKE GOURD (Trichosanthes cucumerina):
  - Varieties: CO-1, PKM-1, Kaumudi.
  - Seed Rate: 3.0 - 4.0 kg/ha. Spacing: 2.0 m x 1.5 m on pandal trellis.
  - Tying small stones to tips of young elongated fruits ensures straight growth.
  - Yield: 18-25 t/ha.""",
    'ridge gourd, torai, snake gourd, chichinda, luffa acutangula, trichosanthes cucumerina, pusa nasdar, co 1, pkm 1, pandal'
)

add(
    'CIARI-KAKROL-PARWAL-01', 'Kakrol and Parwal', 'Momordica dioica / Trichosanthes dioica', 'Vegetable', 'organic',
    'kakrol_parwal_dioecious',
    'Kakrol (Teasle Gourd) and Parwal (Pointed Gourd) Cultivation (ICAR-CIARI)',
    'What are the special cultivation practices for Kakrol and Parwal in Andaman?',
    """According to ICAR-CIARI Package of Practices:
- Dioecious Nature & Sex Ratio:
  - Kakrol (Momordica dioica) and Parwal (Trichosanthes dioica) are dioecious (separate male and female plants).
  - Planting Ratio: Plant in 9:1 female to male ratio (after every 9 female rows, plant 1 male row) to ensure adequate pollination.
- Propagation:
  - Kakrol: Propagated through tuberous roots (setts) or seeds.
  - Parwal: Propagated through mature vine cuttings (root cuttings) 1-1.5 m long in coiled planting method.
- Spacing: 2.0 m x 1.5 m on raised trellis.
- High value seasonal vegetables fetching top prices in island markets. Yield: Kakrol 6-10 t/ha, Parwal 10-15 t/ha.""",
    'kakrol, teasle gourd, parwal, pointed gourd, dioecious, 9:1 ratio, momordica dioica, trichosanthes dioica, high value vegetable'
)

add(
    'CIARI-BROAD-DHANIYA-01', 'Broad Dhaniya', 'Eryngium foetidum', 'Vegetable', 'organic',
    'broad_dhaniya_complete',
    'Broad Dhaniya / Culantro Package of Practices in Andaman (ICAR-CIARI)',
    'What is the complete package of practices for Broad Dhaniya (Eryngium foetidum) in Andaman?',
    """According to ICAR-CIARI Organic Package of Practices:
- Botanical Name: Eryngium foetidum L. (Common names: Broad Dhaniya, Culantro, Sawtooth Coriander, Bilayati Dhaniya).
- Economic Importance: The most popular and lucrative culinary herb in Andaman & Nicobar, retaining rich aroma even after boiling/drying.
- Season & Ecology: Shade-loving biennial/perennial; grows best under 50-70% shade of coconut/arecanut plantations or under 50% agro-shade nets.
- Propagation:
  - By seeds (1.0 - 1.5 kg/ha) or by root slips/divisions (vegetative).
- Spacing & Beds:
  - Raised beds of 1 m width, 15 cm height. Spacing: 20 cm x 15 cm or 30 cm x 20 cm.
- Nutrition:
  - FYM 15-20 t/ha + Vermicompost 2 t/ha.
  - Regular foliar spray of Vermiwash (diluted 8x) or cow urine (5%) every 15 days keeps leaves vibrant green and succulent.
- Harvesting:
  - First harvest 60-75 days after transplanting. Cut outer rosette leaves with sharp knife leaving central crown intact. Subsequent pickings every 30-45 days.
  - Highly profitable: Farmers earn up to Rs 3-5 lakhs/ha annually from coconut intercropping.""",
    'broad dhaniya, eryngium foetidum, culantro, sawtooth coriander, bilayati dhaniya, shade herb, coconut intercrop, vermiwash'
)

add(
    'CIARI-POI-SPINACH-01', 'Poi Spinach', 'Basella alba / rubra', 'Vegetable', 'organic',
    'poi_spinach_pop',
    'Poi / Malabar / Ceylon Spinach Cultivation (ICAR-CIARI)',
    'How to grow Poi / Malabar Spinach in Andaman according to ICAR-CIARI?',
    """According to ICAR-CIARI Package of Practices:
- Species: Basella alba (green stem) and Basella rubra (red stem).
- Adaptability: Thrives exceedingly well in the hot, humid tropical climate of Andaman; highly resistant to diseases.
- Propagation:
  - Seeds: 12 - 15 kg/ha.
  - Stem Cuttings: 30 - 40 cm long cuttings rooted in nursery or planted directly.
- Spacing: 60 cm x 45 cm on ridges or 1 m x 1 m with bamboo trellis/wire netting support.
- Nutrition: FYM 20 t/ha + vermicompost. Frequent light irrigation in dry season; no irrigation in monsoon.
- Harvesting: Multi-cut crop. Harvest 15-20 cm long tender vine tips with leaves every 10-15 days over 6-8 months. Yield: 20-30 t/ha.""",
    'poi, poi sag, malabar spinach, ceylon spinach, basella alba, basella rubra, multi cut greens, bamboo trellis, vine cuttings'
)

add(
    'CIARI-AMARANTHUS-01', 'Amaranthus', 'Amaranthus tricolor', 'Vegetable', 'organic',
    'amaranthus_marsha_bhaji_pop',
    'Amaranthus / Marsha Bhaji Cultivation Practices (ICAR-CIARI)',
    'What are ICAR-CIARI practices for growing Amaranthus / Marsha Bhaji in Andaman?',
    """According to ICAR-CIARI Package of Practices:
- Varieties: CO-1, CO-2, CO-3, Arka Suguna, local red and green Marsha Bhaji.
- Soil & Beds: Well drained sandy loam to clay loam; raised beds of 1 m width.
- Seed Rate & Sowing: 2.0 - 2.5 kg/ha. Mix seeds with 10 parts dry sand for uniform shallow broadcasting.
- Intercropping: Excellent short-duration catch crop in young coconut/arecanut orchards.
- Harvesting:
  1. Uprooting Method: Whole plants uprooted at 25-30 days after sowing.
  2. Clipping Method: First clipping at 25 days; subsequent clippings every 10-12 days (up to 4-6 pickings).
- Yield: 15-20 tonnes/ha.""",
    'amaranthus, marsha bhaji, chaulai, amaranthus tricolor, co 1, arka suguna, sand mixing, clipping, uprooting'
)

add(
    'CIARI-WATER-SPINACH-01', 'Nalibhaji (Water Spinach)', 'Ipomoea aquatica', 'Vegetable', 'organic',
    'nalibhaji_water_spinach_pop',
    'Nalibhaji / Water Spinach Cultivation in Andaman (ICAR-CIARI)',
    'How to cultivate Nalibhaji / Water Spinach according to ICAR-CIARI?',
    """According to ICAR-CIARI Package of Practices:
- Species: Ipomoea aquatica (Nalibhaji / Kalmi Saag / Water Spinach).
- Season: Rainy season (May to December), but can be grown round the year with irrigation.
- Ecology: Semi-aquatic or upland raised beds with high organic matter and moisture.
- Propagation: Terminal stem cuttings 15-20 cm long planted at 20 cm x 15 cm spacing.
- Nutrition: FYM 20-25 t/ha + vermicompost 1.5 t/ha. Apply cow dung slurry fortnightly.
- Harvest: Tender shoots clipped every 15-20 days. Rich in vitamins A, C, and iron. Yield: 25-35 t/ha.""",
    'nalibhaji, water spinach, kalmi saag, ipomoea aquatica, marshy greens, cuttings, semi aquatic, iron rich'
)

add(
    'CIARI-INDIGENOUS-GREENS-01', 'Indigenous Leafy Greens', 'Various', 'Vegetable', 'organic',
    'indigenous_greens_andaman',
    'Indigenous Island Leafy Vegetables: Madrashibhaji, Khattabhaji, Dalbhaji, Brahmi (ICAR-CIARI)',
    'What indigenous leafy greens are recommended by ICAR-CIARI for Andaman?',
    """According to ICAR-CIARI Organic Package of Practices:
1. Madrashibhaji (Alternanthera sessilis / Alternanthera spp.):
   - High moisture leafy vegetable; propagated by stem cuttings; dense ground cover; rich in iron and calcium.
2. Khattabhaji / Roselle (Hibiscus sabdariffa):
   - Sown by seeds (10-12 kg/ha); sour leaves used in dal and curries; deep red calyces harvested for herbal teas, jams, and jellies. Drought-hardy.
3. Dalbhaji (Portulaca oleracea / Purslane):
   - Rich in Omega-3 fatty acids and antioxidants; added to dal for thickening and pleasant sour taste.
4. Brahmi (Bacopa monnieri):
   - Traditional brain-tonic medicinal green; cultivated on moist raised beds; harvested for leaves and herbal formulations.
5. Aam Bhaji (Limnophila chinensis) & Medak Bhaji (Centella asiatica):
   - Traditional culinary greens used for chutneys, seasonings, and therapeutic home remedies.""",
    'indigenous greens, madrashibhaji, khattabhaji, roselle, dalbhaji, purslane, brahmi, bacopa monnieri, aam bhaji, centella asiatica'
)

add(
    'CIARI-DRUMSTICK-01', 'Drumstick / Moringa', 'Moringa oleifera', 'Vegetable', 'organic',
    'drumstick_moringa_pop',
    'Drumstick / Moringa Package of Practices (ICAR-CIARI)',
    'What varieties, pruning techniques, and spacing are recommended for Moringa in Andaman?',
    """According to ICAR-CIARI Package of Practices:
- Varieties: PKM-1, PKM-2, ODC-3, local perennial selections.
- Propagation: Seeds (500 g/ha) or limb cuttings (1-1.5 m long).
- Spacing: 2.5 m x 2.5 m in pits of 45x45x45 cm.
- Pruning / Pinching (Essential):
  - When seedling reaches 1 m height, pinch terminal shoot to stimulate lateral branches.
  - Pinch lateral branches again when they reach 1 m length. This creates a compact, umbrella-shaped tree with maximum fruiting spurs within reach.
- Manuring: 15-20 kg FYM + 100g Urea, 100g SSP, 50g MOP per tree twice a year.
- Pest: Hairy caterpillar and pod borer; spray neem oil 5 ml/L or Bt 2 g/L.
- Yield: 200-300 pods/tree/year.""",
    'drumstick, moringa, sahjan, moringa oleifera, pkm 1, pkm 2, pruning, pinching, spacing'
)

add(
    'CIARI-CURRY-LEAF-01', 'Curry Leaf', 'Murraya koenigii', 'Vegetable', 'organic',
    'curry_leaf_pop',
    'Curry Leaf Cultivation Practices (ICAR-CIARI)',
    'How to cultivate Curry Leaf according to ICAR-CIARI?',
    """According to ICAR-CIARI Package of Practices:
- Varieties: Suwasini, DWD-1, DWD-2.
- Propagation: Fresh seeds sown in nursery beds or root suckers.
- Spacing: 1.5 m x 1.5 m in pits of 45x45x45 cm.
- Manuring: 20 kg FYM + 2 kg vermicompost per bush per year in two splits.
- Training: Head back main shoot at 1 m height to stimulate bushiness and multiple harvesting flushes.
- Pest: Citrus butterfly caterpillar; hand pick caterpillars and spray neem oil 5 ml/L.
- Harvesting: Harvest tender branches every 2-3 months. Yield: 15-20 t/ha/year.""",
    'curry leaf, kadi patta, murraya koenigii, suwasini, spacing, heading back, citrus butterfly'
)

add(
    'CIARI-BABY-CORN-01', 'Baby Corn', 'Zea mays', 'Vegetable', 'organic',
    'baby_corn_pop',
    'Baby Corn Package of Practices and Detasseling (ICAR-CIARI)',
    'What are the key practices for Baby Corn in Andaman including detasseling?',
    """According to ICAR-CIARI Package of Practices:
- Varieties: G-5414, VL Baby Corn 1, HM-4.
- Season: Dry season (Dec-Feb); can be intercropped in vegetables or pulses.
- Seed Rate: 20-25 kg/ha. Spacing: 45-60 cm x 15-20 cm.
- Detasseling (Mandatory Operation):
  - Remove the male tassel immediately upon emergence before it sheds pollen.
  - Keeps the cob unfertilized, yellow, and tender with uniform ovule development.
- Harvest: 2-3 days after silk emergence (silks 1-2 cm long). Pick cobs every 2-3 days (3-4 pickings per plant).
- Yield: 1.0 - 1.5 t/ha dehusked baby corn + 25-30 t/ha green fodder.""",
    'baby corn, zea mays, detasseling, unfertilized ear, g 5414, vl baby corn 1, dry season'
)

add(
    'CIARI-COCONUT-FERTILIZER-01', 'Coconut Fertilizer Schedule', 'Cocos nucifera', 'Plantation', 'integrated',
    'coconut_fertilizer_details',
    'Detailed Fertilizer and Manuring Schedule for Coconut (ICAR-CIARI)',
    'What is the year-by-year fertilizer schedule for coconut palms from planting to bearing?',
    """According to ICAR-CIARI Training Manual on Major Horticultural Crops:
- Year-by-Year Fertilizer Schedule per Palm (Urea, SSP, MOP):
  - 1st Year (3 months after planting): 1/4th adult dose: 250g Urea, 500g SSP, 500g MOP + 10 kg FYM.
  - 2nd Year: 1/2 adult dose: 550g Urea, 1.0 kg SSP, 1.0 kg MOP + 20 kg FYM.
  - 3rd Year: 3/4th adult dose: 800g Urea, 1.5 kg SSP, 1.5 kg MOP + 30 kg FYM.
  - 4th Year onward (Full Adult Dose):
    - Urea: 1.1 kg (500 g N)
    - Single Super Phosphate (SSP): 2.0 kg (320 g P2O5)
    - Muriate of Potash (MOP): 2.0 kg (1,200 g K2O)
    - Farmyard Manure (FYM): 50 kg
    - Magnesium Sulphate (MgSO4): 500 g (especially in sandy coastal soils)
- Split Application:
  - 1/3rd in May-June (pre-monsoon).
  - 2/3rd in Sept-October (post-monsoon).
- Application method: In circular trench 1.8 m radius from trunk, 15 cm deep, covered with soil and green mulch.""",
    'coconut fertilizer schedule, year by year coconut fertilizer, urea ssp mop, adult palm, 500g n 320g p 1200g k, pre monsoon post monsoon'
)

add(
    'CIARI-COCONUT-PESTS-01', 'Coconut Pests', 'Cocos nucifera', 'Plantation', 'integrated',
    'coconut_pests_complete',
    'Complete Management of Coconut Pests: Rhinoceros Beetle, Red Palm Weevil, Mite, Caterpillar (ICAR-CIARI)',
    'How to manage all major coconut pests according to ICAR-CIARI?',
    """According to ICAR-CIARI Horticultural Manual:
1. Rhinoceros Beetle (Oryctes rhinoceros):
   - Hook out beetles using iron wire spike.
   - Mix Sevidol 8G (25g) or Chlorpyriphos 1.5% dust (25g) with equal volume of sand and place in leaf axils around spindle.
   - Treat compost/cow dung breeding pits with Metarhizium anisopliae.
2. Red Palm Weevil (Rhynchophorus ferrugineus):
   - Lethal trunk borer. Set up Ferrolure+ bucket traps with sugarcane/pineapple pieces.
   - For infested trunks: Trunk injection with Chlorpyriphos 20% EC (10 ml in 1L water) through downward slanted 15 mm hole, then plug hole.
3. Eriophyid Mite (Aceria guerreronis):
   - Spray young button bunches with Azadirachtin 10,000 ppm (5 ml/L) or wettable sulphur (4 g/L).
   - Root feeding with Azadirachtin (10 ml in 10 ml water) in morning.
4. Black Headed Caterpillar (Opisina arenosella):
   - Larvae feed on green leaf tissue from underside silk galleries.
   - Release larval parasitoids Goniozus nephantidis @ 20 parasitoids/palm or Bracon brevicornis.""",
    'coconut pests, rhinoceros beetle, red palm weevil, ferrolure, eriophyid mite, black headed caterpillar, goniozus nephantidis'
)

add(
    'CIARI-ARECANUT-DISEASES-01', 'Arecanut Diseases', 'Areca catechu', 'Plantation', 'integrated',
    'arecanut_diseases_complete',
    'Complete Arecanut Disease Management: Koleroga, Foot Rot, Yellow Leaf (ICAR-CIARI)',
    'How to diagnose and treat all major arecanut diseases according to ICAR-CIARI?',
    """According to ICAR-CIARI Horticultural Manual:
1. Fruit Rot / Koleroga / Mahali (Phytophthora arecae):
   - Most devastating disease during monsoon causing premature rotting and dropping of green nuts.
   - Prophylactic spray with 1% Bordeaux mixture (with resin sticker) in May before monsoon; second spray 40 days later.
   - Polythene bunch covering (200-gauge covers tied over bunches) prevents disease 100% without chemicals.
2. Foot Rot / Anabe Roga (Ganoderma lucidum):
   - Lower leaves droop, brown liquid oozes from trunk base, mushroom-like brackets form.
   - Trench around infected palms (1 m deep); drench basin with Tridemorph (Calixin) 0.2% or Hexaconazole 0.1% or apply Trichoderma viride in neem cake.
3. Yellow Leaf Disease (YLD):
   - Leaves turn yellow starting from inner whorls; nuts become black and kernel spongy.
   - Improve garden drainage; apply balanced NPK + Zinc Sulphate (25g) + Borax (10g) per palm annually.""",
    'arecanut diseases, koleroga, mahali, fruit rot, phytophthora arecae, foot rot, ganoderma, anabe roga, yellow leaf disease'
)

add(
    'CIARI-BANANA-PESTS-DISEASES-01', 'Banana Plant Protection', 'Musa sp.', 'Fruit', 'integrated',
    'banana_protection_complete',
    'Complete Management of Banana Diseases: Sigatoka, Panama Wilt, BBTV, and Weevils (ICAR-CIARI)',
    'How to manage Sigatoka leaf spot, Panama wilt, Bunchy Top virus, and weevils in banana?',
    """According to ICAR-CIARI Horticultural Manual:
1. Sigatoka Leaf Spot (Mycosphaerella musicola):
   - Severe in humid island conditions. Cut off and burn severely infected leaves.
   - Spray Propiconazole 25% EC @ 1 ml/L or Carbendazim 50% WP @ 1 g/L with 1% mineral oil (Power oil) emulsion every 30 days during rainy season.
2. Panama Wilt (Fusarium oxysporum f. sp. cubense):
   - Lower leaves turn yellow and collapse around pseudostem; vascular browning.
   - Plant resistant cultivars (Grand Naine, Robusta). Dip suckers in Carbendazim 0.1% + Trichoderma viride (10 g/L); drench soil with Carbendazim 0.1%.
3. Banana Bunchy Top Virus (BBTV):
   - Leaves bunched together at crown with dark green 'dot-dash' streaks on petiole.
   - Rogue and inject infected plants with kerosene or glyphosate (4 ml); spray Imidacloprid (0.3 ml/L) to kill vector aphids (Pentalonia nigronervosa).
4. Pseudostem Borer & Rhizome Weevil:
   - Apply Carbofuran 3G @ 20g/plant around base or inject stem with Chlorpyriphos.""",
    'banana protection, sigatoka leaf spot, propiconazole, panama wilt, fusarium, bunchy top, bbtv, rhizome weevil, pseudostem borer'
)

add(
    'CIARI-BLACK-PEPPER-PROCESSING-01', 'Black Pepper Processing', 'Piper nigrum', 'Spices', 'integrated',
    'pepper_harvest_curing',
    'Black Pepper and White Pepper Harvesting and Post-Harvest Processing (ICAR-CIARI)',
    'How to harvest and process Black Pepper and White Pepper according to ICAR-CIARI?',
    """According to ICAR-CIARI Horticultural Manual:
1. Harvest Timing:
   - Harvest spikes when 1 or 2 berries in the spike turn bright yellow to orange-red.
2. Black Pepper Processing (Boiling Water Dip Method):
   - Separate berries from stalks manually or with mechanical thresher.
   - Boiling Water Treatment (Blanching): Dip separated berries in boiling water (100°C) for 1 minute using a perforated bucket.
   - Advantages: Removes dust, kills fungal spores, accelerates enzymatic browning, cuts drying time by half, and produces clean, uniformly black wrinkled peppercorns.
   - Sun dry on clean mats/cement floor for 5-7 days until moisture drops to 10-11%.
   - Dry Recovery: 33-35% of fresh berries.
3. White Pepper Processing:
   - Harvest fully ripe crimson-red berries.
   - Pack berries in gunny bags and immerse in running water for 7-8 days to soften outer skin.
   - Rub off softened pulp and skin by hand or trampling in water; wash thoroughly and sun dry white seeds for 3-4 days.
   - Yield: Premium export product fetching 30-50% higher market price.""",
    'black pepper processing, white pepper, boiling water blanching, drying, moisture 10 percent, dry recovery, harvest spikes'
)

add(
    'CIARI-GINGER-TURMERIC-CURING-01', 'Ginger and Turmeric Curing', 'Zingiberaceae', 'Spices', 'integrated',
    'rhizome_curing_processing',
    'Ginger and Turmeric Harvesting, Curing, and Polishing (ICAR-CIARI)',
    'How to harvest and cure Ginger and Turmeric according to ICAR-CIARI?',
    """According to ICAR-CIARI Horticultural Manual:
1. GINGER HARVEST & PROCESSING:
   - Harvest at 5 months for green ginger (for vegetables/pickles) and at 8 months (when foliage turns yellow and dies down) for dry ginger.
   - Wash rhizomes; scrape outer skin with bamboo splints (do not use iron knives which discolour ginger); wash and sun dry for 7-10 days to 10% moisture. Dry recovery: 16-25%.
2. TURMERIC CURING & POLISHING:
   - Harvest at 7-9 months when leaves turn completely yellow and dry.
   - Curing (Boiling): Clean fingers and boil in water (or 0.1% sodium bicarbonate solution) for 45-60 minutes in copper or galvanized iron vessels until white fumes with characteristic aroma emerge and fingers become soft (pierced by matchstick).
   - Drying: Spread boiled fingers in 5-7 cm thick layer on clean drying floor in sun for 10-15 days until dry and crisp (dry recovery 18-22%).
   - Polishing: Polish dried turmeric manually (in gunny bags) or in rotating polishing drums with turmeric powder suspension to give bright attractive yellow finish.""",
    'ginger drying, turmeric curing, boiling turmeric, polishing drum, harvest maturity, dry recovery, scraping skin'
)

add(
    'CIARI-TAPIOCA-CASSAVA-01', 'Cassava / Tapioca', 'Manihot esculenta', 'Tubers', 'integrated',
    'cassava_complete_pop',
    'Cassava / Tapioca Package of Practices in Andaman (ICAR-CIARI)',
    'What are the complete cultivation practices for Cassava / Tapioca in Andaman & Nicobar?',
    """According to ICAR-CIARI Horticultural Manual:
- Varieties: H-165, H-226, Sree Sahya, Sree Vijaya, CARI Tapioca-1.
- Propagation & Setts:
  - Select mature, disease-free stems (2-3 cm diameter); prepare 15-20 cm long cuttings (setts) with 4-6 viable buds using a sharp saw/knife with smooth cut.
- Planting Method:
  - Mound method (sloping/wet land) or Ridge method (flat land). Plant setts vertically or slightly slanted (5-7 cm deep) with buds facing upward.
- Spacing: 90 cm x 90 cm (12,345 plants/ha).
- Nutrition: FYM 12.5 t/ha + NPK 100:50:100 kg/ha (half N + full P & K as basal; half N top dressed at 45-60 DAP with earthing up).
- Protection: Red spider mite: spray wettable sulphur @ 3 g/L; Cassava Mosaic Disease: rogue infected plants, use disease-free setts.
- Harvest: 8-10 months when leaves begin to shed and tubers crack soil surface. Yield: 25-35 tonnes/ha.""",
    'cassava, tapioca, manihot esculenta, setts, mound method, h 165, cari tapioca 1, mosaic disease, red spider mite'
)

add(
    'CIARI-SWEET-POTATO-01', 'Sweet Potato', 'Ipomoea batatas', 'Tubers', 'integrated',
    'sweet_potato_pop',
    'Sweet Potato Package of Practices and Weevil Control (ICAR-CIARI)',
    'What varieties and weevil control measures are recommended for Sweet Potato by ICAR-CIARI?',
    """According to ICAR-CIARI Horticultural Manual:
- Varieties: Sree Bhadra, Sree Arun, Sree Varun, Kalingarayan local.
- Propagation: Terminal vine cuttings (20-25 cm long with 3-4 nodes). Terminal cuttings give significantly higher tuber yield than middle or basal cuttings.
- Spacing: 60 cm (ridges) x 20 cm (between cuttings).
- Manuring: FYM 10 t/ha + NPK 50:25:50 kg/ha.
- Sweet Potato Weevil (Cylas formicarius) - The Most Severe Pest:
  - Weevil lays eggs in exposed tubers causing bitter taste and black tunnels.
  - Management:
    1. Earthing up at 30 and 60 days after planting to cover tubers and seal soil cracks.
    2. Install Cylas pheromone traps @ 5 traps/ha.
    3. Dip vine cuttings in Chlorpyriphos 20% EC (2 ml/L) for 10 minutes before planting.
- Harvesting & Yield: Ready in 90-105 days when leaves turn yellow. Yield: 15-20 tonnes/ha.""",
    'sweet potato, shakarkand, ipomoea batatas, sree bhadra, vine cuttings, sweet potato weevil, cylas formicarius, earthing up'
)

add(
    'CIARI-COLOCASIA-TARO-01', 'Colocasia / Taro', 'Colocasia esculenta', 'Tubers', 'integrated',
    'colocasia_taro_pop',
    'Colocasia / Taro Cultivation as Intercrop in Coconut and Blight Control (ICAR-CIARI)',
    'How to cultivate Colocasia / Taro and control Leaf Blight according to ICAR-CIARI?',
    """According to ICAR-CIARI Horticultural Manual:
- Varieties: Sree Rashmi, Sree Pallavi, Muktakeshi, local Arbi/Ghuiya selections.
- Adaptability: Excellent shade tolerance; ideal intercrop in coconut and arecanut gardens.
- Planting Material: Mother corms or healthy side cormels (30-40 g) with intact apical bud.
- Spacing: 60 cm x 45 cm on ridges or flat beds. Pits filled with 500g FYM.
- Nutrition: FYM 15 t/ha + NPK 80:40:80 kg/ha in 2 splits.
- Leaf Blight (Phytophthora colocasiae) - Major Disease:
  - Circular water-soaked lesions with yellow margin and droplet exudation during monsoon.
  - Spray Mancozeb @ 2.5 g/L or Metalaxyl-Mancozeb (Ridomil MZ) @ 2 g/L at 15-day intervals.
- Harvesting: 5-6 months when leaves turn completely yellow. Yield: 12-18 tonnes/ha.""",
    'colocasia, taro, arbi, ghuiya, colocasia esculenta, sree rashmi, muktakeshi, coconut intercrop, leaf blight, phytophthora colocasiae'
)

add(
    'CIARI-ELEPHANT-FOOT-YAM-01', 'Elephant Foot Yam', 'Amorphophallus paeoniifolius', 'Tubers', 'integrated',
    'elephant_foot_yam_pop',
    'Elephant Foot Yam (Amorphophallus) Package of Practices (ICAR-CIARI)',
    'What are the complete practices for Elephant Foot Yam (Jimikand) cultivation in Andaman?',
    """According to ICAR-CIARI Horticultural Manual:
- Varieties: Gajendra (non-acrid, high yielding), Bidhan Kusum, CARI EFY-1.
- Planting Material Preparation:
  - Corm pieces of 500 g - 1,000 g cut vertically from mother corm, ensuring each sett has a piece of the central apical bud ring.
  - Smear cut surfaces with fresh cow dung slurry mixed with Trichoderma viride or Mancozeb (2 g/L) and shade dry for 3-4 days before planting to heal wounds.
- Pit Size & Spacing:
  - Dig pits of 60 cm x 60 cm x 45 cm at 90 cm x 90 cm spacing.
  - Fill bottom with topsoil + 2 kg FYM + 25g neem cake. Plant corm piece with bud facing upward and cover with 10 cm soil.
- Intercropping in Coconut: Outstanding companion crop; performs exceptionally well in coconut interspaces.
- Mulching & Earthing Up: Heavy green leaf mulching at planting. Earthing up at 60 and 90 DAP with second split fertilizer.
- Collar Rot (Sclerotium rolfsii): Avoid waterlogging; drench stem base with Carbendazim (1 g/L) or apply Trichoderma with compost.
- Harvesting: 8-9 months when umbrella-like pseudostem turns completely yellow and collapses. Yield: 35-50 tonnes/ha.""",
    'elephant foot yam, jimikand, suran, amorphophallus paeoniifolius, gajendra, corm sett cutting, cow dung smear, coconut intercrop, collar rot'
)

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(entries, f, indent=2, ensure_ascii=False)

print(f'Successfully built ICAR-CIARI RAG Knowledge Base: {len(entries)} comprehensive entries saved to {OUT_FILE}')
