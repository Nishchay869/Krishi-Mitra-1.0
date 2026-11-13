"""ICAR-CIARI RAG (Retrieval-Augmented Generation) Knowledge Engine for Krishi Mitra Farm Assistant.

Provides authoritative, locally grounded agricultural advisory by retrieving verified practices
from ICAR-Central Island Agricultural Research Institute (CIARI) Package of Practices PDFs:
1. Package of Practices for Organic Vegetable production in A & N Islands
2. Package of Practices (PoP) for Vegetable Cultivation in Andaman & Nicobar Islands (2014)
3. Training Manual on Package of Practices for Major Horticultural Crops (Plantation, Fruit, Spices, Tubers)
"""
import json
import logging
import os
import re
from dataclasses import dataclass
from typing import List, Optional

from django.conf import settings

logger = logging.getLogger(__name__)

KNOWLEDGE_FILE = os.path.join(settings.BASE_DIR, 'data', 'ciari_rag_knowledge.json')

KNOWLEDGE_FILES = [
    os.path.join(settings.BASE_DIR, 'data', 'ciari_rag_knowledge.json'),
    os.path.join(settings.BASE_DIR, 'data', 'cpg2012_rag_knowledge.json'),
    os.path.join(settings.BASE_DIR, 'data', 'horticulture_rag_knowledge.json'),
    os.path.join(settings.BASE_DIR, 'data', 'uas_dharwad_rag_knowledge.json'),
    os.path.join(settings.BASE_DIR, 'data', 'farmerbook_rag_knowledge.json'),
]

# Crop name aliases and multi-lingual synonyms (Hindi, Kannada, Tamil, Telugu, botanical)
CROP_ALIASES = {
    # Cereals & Millets
    'ragi': ['ragi', 'finger millet', 'nachni', 'eleusine coracana', 'ragulu', 'kezhvaragu', 'mandua'],
    'sorghum': ['sorghum', 'jowar', 'jola', 'cholam', 'jonnalu', 'sorghum bicolor', 'chari'],
    'pearl millet': ['pearl millet', 'cumbu', 'bajra', 'sajje', 'sajjalu', 'kambu', 'pennisetum glaucum'],
    'rice': ['rice', 'paddy', 'dhan', 'bhatta', 'nellu', 'vari', 'chawal', 'oryza sativa'],
    'wheat': ['wheat', 'gehun', 'godhi', 'godumai', 'godhumalu', 'triticum'],
    'maize': ['maize', 'corn', 'makka', 'musukina jola', 'makka cholam', 'mokka jonnalu', 'zea mays'],
    'sweet sorghum': ['sweet sorghum'],
    # Pulses
    'redgram': ['red gram', 'redgram', 'pigeon pea', 'arhar', 'tur', 'toor', 'togari', 'thuvarai', 'kandulu', 'cajanus cajan'],
    'blackgram': ['black gram', 'blackgram', 'urad', 'udad', 'uddina bele', 'ulundu', 'minumulu', 'vigna mungo'],
    'greengram': ['green gram', 'greengram', 'moong', 'mung', 'hesaru', 'pasi payaru', 'pesalu', 'vigna radiata'],
    'bengalgram': ['bengal gram', 'bengalgram', 'chickpea', 'chana', 'kadale', 'konda kadalai', 'senagalu', 'cicer arietinum', 'gram'],
    'cowpea': ['cowpea', 'lobia', 'barbatti', 'yard long bean', 'alasande', 'karamani', 'bobbarlu', 'vigna unguiculata'],
    'horsegram': ['horse gram', 'horsegram', 'kulthi', 'huruli', 'kollu', 'ulavalu', 'macrotyloma uniflorum'],
    'lab lab': ['lab lab', 'lablab', 'dolichos', 'sem', 'hyacinth bean', 'avara', 'avarai', 'mochai'],
    'sword bean': ['sword bean', 'valavara', 'canavalia'],
    'soybean': ['soybean', 'soya bean', 'glycine max'],
    # Oilseeds
    'groundnut': ['groundnut', 'peanut', 'moongphali', 'shenga', 'kadalai', 'verukadalai', 'verusenaga', 'arachis hypogaea'],
    'sesame': ['sesame', 'gingelly', 'til', 'ellu', 'nuvvulu', 'sesamum indicum'],
    'castor': ['castor', 'arandi', 'haralu', 'aamanakku', 'amudamu', 'ricinus communis'],
    'sunflower': ['sunflower', 'surajmukhi', 'suryakanti', 'helianthus annuus'],
    'safflower': ['safflower', 'kusum', 'kusubi', 'carthamus tinctorius'],
    'oil palm': ['oil palm', 'oilpalm', 'elaeis guineensis'],
    'niger': ['niger', 'ramtil', 'gurellu', 'uchellu', 'guizotia abyssinica'],
    # Commercial & Fibre
    'cotton': ['cotton', 'kapas', 'hatti', 'paruthi', 'paththi', 'gossypium'],
    'sugarcane': ['sugarcane', 'ganna', 'kabbu', 'karumbu', 'cheruku', 'saccharum officinarum'],
    'jute': ['jute', 'patson', 'san', 'corchorus'],
    'agave': ['agave', 'sisal', 'kathaale'],
    # Vegetables
    'tomato': ['tomato', 'tamatar', 'lycopersicon', 'solanum lycopersicum'],
    'brinjal': ['brinjal', 'baingan', 'eggplant', 'aubergine', 'solanum melongena'],
    'chilli': ['chilli', 'chili', 'mirch', 'capsicum annuum'],
    'sweet pepper': ['sweet pepper', 'capsicum', 'shimla mirch', 'bell pepper'],
    'okra': ['okra', 'bhindi', 'bhendi', 'lady finger', 'ladies finger', 'abelmoschus'],
    'potato': ['potato', 'aloo', 'alu', 'batata', 'urulakizhangu', 'bangaladumpa', 'solanum tuberosum'],
    'onion': ['onion', 'pyaz', 'kanda', 'eerulli', 'vengayam', 'ullipayalu', 'allium cepa'],
    'garlic': ['garlic', 'lahsun', 'bellulli', 'poondu', 'vellulli', 'allium sativum'],
    'cauliflower': ['cauliflower', 'phool gobhi', 'gobhi', 'brassica oleracea var botrytis'],
    'cabbage': ['cabbage', 'patta gobhi', 'band gobhi'],
    'knolkhol': ['knolkhol', 'kholrabi', 'ganth gobhi'],
    'broccoli': ['broccoli', 'hari gobhi'],
    'bitter gourd': ['bitter gourd', 'karela', 'momordica'],
    'bottle gourd': ['bottle gourd', 'lauki', 'ghiya', 'lagenaria'],
    'cucumber': ['cucumber', 'kheera', 'kakdi', 'cucumis'],
    'gherkin': ['gherkin', 'cucumis anguria'],
    'ridge gourd': ['ridge gourd', 'torai', 'tori', 'luffa acutangula'],
    'snake gourd': ['snake gourd', 'chichinda', 'padwal', 'trichosanthes'],
    'ash gourd': ['ash gourd', 'petha', 'budagumbala', 'neer poosani', 'benincasa'],
    'pumpkin': ['pumpkin', 'kaddu', 'sihi kumbala', 'cucurbita'],
    'watermelon': ['watermelon', 'tarbooj', 'kallangadi', 'tharpoosani'],
    'muskmelon': ['muskmelon', 'kharbooza', 'kharbuj', 'cucumis melo'],
    'kakrol': ['kakrol', 'teasle gourd', 'kantola', 'momordica dioica'],
    'parwal': ['parwal', 'pointed gourd', 'patal', 'trichosanthes dioica'],
    'cluster bean': ['cluster bean', 'guar', 'gwar', 'cyamopsis'],
    'french bean': ['french bean', 'beans', 'farashi bean', 'phaseolus vulgaris'],
    'broad bean': ['broad bean', 'bakla', 'vicia faba'],
    'peas': ['peas', 'pea', 'matar', 'batani', 'pattani', 'pisum sativum'],
    'palak': ['palak', 'spinach', 'indian spinach'],
    'poi': ['poi', 'poi sag', 'malabar spinach', 'ceylon spinach', 'basella'],
    'amaranthus': ['amaranthus', 'marsha bhaji', 'chaulai', 'lal sag', 'thotakura'],
    'radish': ['radish', 'mooli', 'mula', 'raphanus'],
    'carrot': ['carrot', 'gajar', 'gajjari', 'daucus'],
    'beetroot': ['beetroot', 'beet', 'beta vulgaris'],
    'coriander': ['coriander', 'dhaniya', 'kothmir', 'kothamalli'],
    'broad dhaniya': ['broad dhaniya', 'culantro', 'sawtooth coriander', 'eryngium', 'bilayati dhaniya'],
    'water spinach': ['nalibhaji', 'water spinach', 'kalmi saag', 'ipomoea aquatica'],
    'drumstick': ['drumstick', 'moringa', 'sahjan', 'saijan', 'nuggekayi', 'murungai'],
    'curry leaf': ['curry leaf', 'kadi patta', 'karivepaku', 'karibevu', 'murraya'],
    'baby corn': ['baby corn'],
    # Fruits & Plantation
    'coconut': ['coconut', 'nariyal', 'thengu', 'kobbari', 'thengai', 'cocos nucifera'],
    'arecanut': ['arecanut', 'supari', 'betel nut', 'areca catechu', 'adike', 'paaku'],
    'banana': ['banana', 'kela', 'bale', 'arati', 'vazhai', 'musa'],
    'papaya': ['papaya', 'papita', 'parangi', 'pappali', 'carica papaya'],
    'pineapple': ['pineapple', 'ananas', 'ananas comosus'],
    'mango': ['mango', 'aam', 'mavu', 'manga', 'mamidi', 'mangifera indica'],
    'acid lime': ['acid lime', 'lime', 'lemon', 'nimbu', 'nimbe', 'elumichai', 'nimmakaya', 'citrus aurantiifolia'],
    'sweet orange': ['sweet orange', 'mosambi', 'mousambi', 'sathgudi', 'citrus sinensis'],
    'mandarin orange': ['mandarin', 'orange', 'kamala orange', 'citrus reticulata'],
    'grapes': ['grapes', 'grape', 'angoor', 'drakshi', 'thiratchai', 'draksha', 'vitis vinifera'],
    'guava': ['guava', 'amrood', 'seebe', 'koyya', 'jama', 'psidium guajava'],
    'sapota': ['sapota', 'chikoo', 'chiku', 'sapodilla', 'manilkara zapota'],
    'pomegranate': ['pomegranate', 'anar', 'dalimbe', 'madhulam', 'danimma', 'punica granatum'],
    'jackfruit': ['jackfruit', 'jack', 'kathal', 'halasu', 'pala', 'artocarpus'],
    'ber': ['ber', 'jujube', 'bore', 'elanthai', 'ziziphus'],
    'amla': ['amla', 'indian gooseberry', 'bettada nellikai', 'nelli', 'phyllanthus emblica'],
    'apple': ['apple', 'seb', 'sebu', 'malus domestica'],
    'pear': ['pear', 'nashpati', 'pyrus'],
    'plum': ['plum', 'prunus domestica'],
    'peach': ['peach', 'aadoo', 'prunus persica'],
    # Spices
    'black pepper': ['black pepper', 'pepper', 'kali mirch', 'karimenasu', 'milagu', 'piper nigrum'],
    'cinnamon': ['cinnamon', 'dalchini', 'lavanga pattai', 'cinnamomum'],
    'clove': ['clove', 'laung', 'lavanga', 'krambu', 'syzygium aromaticum'],
    'nutmeg': ['nutmeg', 'mace', 'jaiphal', 'javitri', 'jathikai', 'myristica'],
    'ginger': ['ginger', 'adrak', 'shunti', 'inji', 'allam', 'zingiber'],
    'turmeric': ['turmeric', 'haldi', 'arishina', 'manjal', 'pasupu', 'curcuma longa'],
    'cardamom': ['cardamom', 'elaichi', 'elakki', 'elakkai', 'yelakulu', 'elettaria'],
    'tamarind': ['tamarind', 'imli', 'hunase', 'puli', 'chintha', 'tamarindus indica'],
    'fenugreek': ['fenugreek', 'methi', 'menthya', 'vendhayam', 'menthulu'],
    # Plantation & Commercial
    'coffee': ['coffee', 'kapi', 'coffea arabica'],
    'tea': ['tea', 'chai', 'camellia sinensis'],
    'cashew': ['cashew', 'kaju', 'geru', 'mundhiri', 'anacardium'],
    'rubber': ['rubber', 'hevea brasiliensis'],
    # Tubers
    'cassava': ['cassava', 'tapioca', 'maravalli', 'manihot esculenta'],
    'sweet potato': ['sweet potato', 'shakarkand', 'genasu', 'ipomoea batatas'],
    'colocasia': ['colocasia', 'taro', 'arbi', 'ghuiya', 'keshavu'],
    'elephant foot yam': ['elephant foot yam', 'yam', 'jimikand', 'suran', 'suvarna gedde', 'senai', 'amorphophallus'],
    # Flowers
    'rose': ['rose', 'gulab', 'roja', 'gulabi', 'rosa'],
    'jasmine': ['jasmine', 'chameli', 'mogra', 'malli', 'mallige', 'jasminum'],
    'marigold': ['marigold', 'genda', 'chendumalli', 'chemanthi', 'tagetes'],
    'chrysanthemum': ['chrysanthemum', 'sevanthi', 'sevvanthi'],
    'crossandra': ['crossandra', 'kanakambaram'],
    # Medicinal & Aromatic
    'coleus': ['coleus', 'plectranthus barbatus'],
    'senna': ['senna', 'senna alexandrina'],
    'periwinkle': ['periwinkle', 'catharanthus roseus'],
    'glory lilly': ['glory lilly', 'gloriosa superba'],
    'lemongrass': ['lemongrass', 'cymbopogon'],
    'mint': ['mint', 'pudina', 'mentha'],
    # Forage & Forestry
    'fodder': ['fodder', 'soundal', 'leucaena', 'guinea grass', 'napier', 'cholam fodder', 'cumbu fodder', 'lucerne'],
    'mushroom': ['mushroom', 'khumbi', 'anabe', 'kalan', 'puttakokkulu', 'oyster mushroom', 'milky mushroom'],
    # Natural & Organic farming inputs
    'natural farming': ['natural farming', 'jeevamrit', 'ghanjeevamrit', 'beejamrit', 'neemastra', 'agniastra', 'dashaparni', 'zero budget'],
    'panchagavya': ['panchagavya', 'panchgavya', 'bio-stimulant'],
    'vermiwash': ['vermiwash', 'earthworm wash'],
}

_KNOWLEDGE_BASE = None


def load_knowledge_base():
    """Load unified agricultural RAG knowledge base into memory with caching."""
    global _KNOWLEDGE_BASE
    if _KNOWLEDGE_BASE is not None:
        return _KNOWLEDGE_BASE

    combined = []
    seen_ids = set()

    for kpath in KNOWLEDGE_FILES:
        if not os.path.exists(kpath):
            continue
        try:
            with open(kpath, encoding='utf-8') as fh:
                data = json.load(fh)
            loaded_count = 0
            for item in data:
                iid = item.get('id')
                if iid and iid in seen_ids:
                    continue
                if iid:
                    seen_ids.add(iid)
                combined.append(item)
                loaded_count += 1
            logger.info('Loaded %d entries from %s', loaded_count, os.path.basename(kpath))
        except Exception as e:
            logger.error('Failed to load knowledge file %s: %s', kpath, e)

    _KNOWLEDGE_BASE = combined
    logger.info('Total loaded agricultural RAG knowledge base entries: %d', len(_KNOWLEDGE_BASE))
    return _KNOWLEDGE_BASE


@dataclass
class RAGMatch:
    entry: dict
    score: float
    matched_crop: str
    relevance_reason: str


STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
    'what', 'how', 'when', 'where', 'which', 'who', 'why', 'can', 'should', 'is', 'are', 'was',
    'were', 'be', 'been', 'do', 'does', 'did', 'have', 'has', 'had', 'per', 'dose', 'rate'
}


def matches_word(word: str, text: str) -> bool:
    """Check if word/phrase appears as a whole distinct word in text (case-insensitive)."""
    if not word or not text:
        return False
    # Use word boundaries so 'til' does not match 'fertilizer' and 'pea' does not match 'repeat'
    return bool(re.search(rf'\b{re.escape(word.strip())}\b', str(text), re.IGNORECASE))


def tokenize(text: str) -> set:
    """Normalize text into lowercase alphanumeric words."""
    clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', str(text).lower())
    return set(w for w in clean.split() if len(w) > 2)


def retrieve_relevant_ciari_docs(query: str, top_k: int = 3, threshold: float = 2.5) -> List[RAGMatch]:
    """Retrieve top matching agricultural Package of Practices documents for user query.
    
    Uses hybrid scoring:
    - Direct crop identification & whole-word synonym resolution (high boost)
    - Strict cross-crop isolation (prevents dosages/chemicals of one crop from mixing with another)
    - Topic / Intent alignment (fertilizer, pest, disease, variety, pruning, intercropping)
    - Content-specific overlap across title, content, keywords, and questions
    """
    kb = load_knowledge_base()
    if not kb:
        return []

    q_lower = query.lower()
    q_tokens = tokenize(query)

    # 1. Identify matched crops in query using whole-word matching
    detected_crops = set()
    for canonical_crop, aliases in CROP_ALIASES.items():
        if any(matches_word(alias, query) for alias in aliases):
            detected_crops.add(canonical_crop)

    # Topic indicators using whole-word matching to avoid substring false positives (e.g. 'rog' inside 'nitrogen')
    pest_words = ['pest', 'insect', 'disease', 'spray', 'keeda', 'rog', 'rot', 'borer', 'blight', 'wilt', 'mildew', 'fly', 'mite', 'caterpillar', 'sigatoka', 'koleroga', 'weevil']
    fert_words = ['fertilizer', 'fertiliser', 'urea', 'npk', 'dap', 'mop', 'manure', 'compost', 'khad', 'dung', 'slurry', 'vermiwash', 'panchagavya', 'dose', 'dosage', 'nitrogen', 'phosphorus', 'potassium', 'potash', 'pottash', 'nutrient', 'nutrients', 'macro', 'micronutrient', 'fertigation']
    variety_words = ['variety', 'varieties', 'kisme', 'seed', 'sow', 'season', 'spacing', 'plant', 'yield', 'rate', 'nursery']
    intercrop_words = ['intercrop', 'intercropping', 'mixed', 'coconut garden', 'shade', 'multi-tier']
    prep_words = ['prepare', 'preparation', 'how to prepare', 'how to make', 'ingredients', 'recipe', 'method of preparation']

    is_pest = any(matches_word(w, q_lower) for w in pest_words)
    is_fert = any(matches_word(w, q_lower) for w in fert_words)
    is_variety = any(matches_word(w, q_lower) for w in variety_words)
    is_intercrop = any(matches_word(w, q_lower) for w in intercrop_words)
    is_prep = any(matches_word(w, q_lower) for w in prep_words)

    scored_entries = []

    for item in kb:
        score = 0.0
        item_crop_lower = item['crop'].lower()
        item_title_lower = item['title'].lower()
        item_topic_lower = item['topic'].lower()
        item_content_lower = item['answer'].lower()

        # Strict crop isolation: prevent cross-crop contamination
        crop_matched = False
        is_general_crop = item_crop_lower.startswith('general')

        if detected_crops:
            # Check if this item matches any detected crop
            for detected in detected_crops:
                aliases_for_detected = CROP_ALIASES.get(detected, [detected])
                if (matches_word(detected, item_crop_lower) or
                    any(matches_word(alias, item_crop_lower) for alias in aliases_for_detected) or
                    detected in item_crop_lower):
                    score += 25.0
                    crop_matched = True
                    break
                elif any(matches_word(alias, item_title_lower) for alias in aliases_for_detected):
                    score += 15.0
                    crop_matched = True
                    break

            if not crop_matched and not is_general_crop:
                # User asked about a specific crop (e.g. Ragi) but this item is for another specific crop (e.g. Cotton)
                # Heavily penalize to completely isolate crop dosages and pest recommendations
                score -= 30.0
        else:
            # Query did not specify a crop; check if query contains crop name words
            if any(matches_word(w, query) for w in item_crop_lower.split() if len(w) > 3):
                score += 10.0
                crop_matched = True

        # Topic matching bonuses
        if is_prep and ('preparation' in item_topic_lower or 'preparation' in item_title_lower or 'biostimulants' in item_topic_lower):
            score += 15.0
        if is_pest and ('pest' in item_topic_lower or 'disease' in item_topic_lower or 'protection' in item_topic_lower):
            score += 8.0
        if is_fert and ('fertilizer' in item_topic_lower or 'nutrient' in item_topic_lower or 'organic' in item_topic_lower):
            score += 8.0
        if is_variety and ('varieties' in item_topic_lower or 'spacing' in item_topic_lower or 'season' in item_topic_lower or 'sowing' in item_topic_lower):
            score += 6.0
        if is_intercrop and ('intercrop' in item_topic_lower or 'intercrop' in item_content_lower):
            score += 8.0

        # Token overlap across title, keywords and question (excluding stop words)
        item_tokens = tokenize(f"{item['title']} {item['keywords']} {item['question']}")
        meaningful_q_tokens = q_tokens.difference(STOP_WORDS)
        common = meaningful_q_tokens.intersection(item_tokens)
        score += len(common) * 2.0

        # High-specificity term bonus
        specific_terms = [
            'panchagavya', 'vermiwash', 'bordeaux', 'trichoderma', 'pseudomonas', 'neem oil',
            'koleroga', 'sigatoka', 'ethrel', 'detasseling', 'culantro', 'broad dhaniya',
            'moringa', 'curry leaf', 'elephant foot yam', 'gajendra', 'sweet potato', 'tapioca',
            'rhinoceros beetle', 'red palm weevil', 'ferrolure', 'lucinlure', 'fruit fly',
            'cue lure', 'arka rakshak', 'cari brinjal 1', 'grand naine', 'panniyur', 'rio de janeiro',
            'jeevamrit', 'beejamrit', 'ghanjeevamrit', 'dashaparni', 'agniastra', 'neemastra',
            'saptha dhanya', 'dharwad', 'stcr', 'pre-harvest interval', 'phi', 'chlorosis',
            'nitrogen', 'phosphorus', 'potassium', 'potash', 'npk', 'urea', 'dap', 'mop', 'fertigation'
        ]
        for st in specific_terms:
            if st in q_lower and (st in item_content_lower or st in item_title_lower or st in item_tokens):
                score += 12.0

        if score >= threshold:
            scored_entries.append(RAGMatch(
                entry=item,
                score=score,
                matched_crop=item['crop'],
                relevance_reason=f"Matched crop '{item['crop']}' with score {score:.1f}"
            ))

    scored_entries.sort(key=lambda m: m.score, reverse=True)
    return scored_entries[:top_k]


def format_rag_prompt_context(matches: List[RAGMatch]) -> str:
    """Format retrieved documents into an authoritative context block for Gemini."""
    if not matches:
        return ""

    context_lines = [
        "AUTHORITATIVE AGRICULTURAL REFERENCE (ICAR-CIARI PACKAGE OF PRACTICES):",
        "The following verified scientific package of practices and official agricultural guidelines directly address the user's inquiry:",
        ""
    ]

    for idx, match in enumerate(matches, 1):
        e = match.entry
        ans = (e.get('answer') or '').strip()
        if len(ans) > 2000:
            ans = ans[:2000] + "\n...[truncated for brevity]..."
        context_lines.extend([
            f"--- [Reference #{idx}: {e['title']}] ---",
            f"Crop: {e['crop']} ({e.get('scientific_name', '')})",
            f"Topic: {e['topic']} | Farming System: {e.get('farming_type', 'Conventional').title()}",
            f"Source Document: {e['source']}",
            f"Official Recommendation:",
            ans,
            ""
        ])

    context_lines.extend([
        "CRITICAL INSTRUCTIONS FOR RESPONSE GENERATION:",
        "1. Ground your advisory in the official Package of Practices and recommendations provided above whenever applicable.",
        "2. If the user asks about fertilizers, nutrient dosages (NPK, nitrogen, phosphorus, potassium, potash), pests, or cultivation practices for a crop, ALWAYS provide the complete agricultural advisory. If specific figures or stages are not in the excerpt, provide the standard verified agronomic recommendation for that crop.",
        "3. Explicitly cite the authoritative source (e.g., ICAR-CIARI, UAS Dharwad, TNAU, or MANAGE) when using reference data.",
        "4. Write the ENTIRE answer in the exact same language and script requested by the user.",
        "5. NEVER refuse a crop, fertilizer, pest, or agricultural question! Refusals are strictly and exclusively for non-agricultural topics like politics, movies, or coding.",
        "6. Keep the advice actionable, structured with bullet points, and directly helpful to the farmer."
    ])

    return "\n".join(context_lines)


def format_offline_fallback_reply(matches: List[RAGMatch], query: str) -> str:
    """Provide a comprehensive, authoritative response directly from retrieved agricultural data when Gemini API is unavailable."""
    if not matches:
        return ""

    top_entry = matches[0].entry
    lines = [
        f"**Agricultural Advisory: {top_entry['title']}**\n",
        f"*Source: {top_entry['source']}*\n",
        top_entry['answer']
    ]

    if len(matches) > 1:
        second = matches[1].entry
        lines.extend([
            f"\n\n**Additional Agricultural Recommendation: {second['title']}**\n",
            second['answer']
        ])

    lines.append("\n\n*If you need immediate expert advisory, you can also contact the Kisan Call Centre at toll-free 1800-180-1551.*")
    return "\n".join(lines)
