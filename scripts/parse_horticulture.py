"""
Parse Horticulture Crop Production Guide 2020 (TNAU + Directorate of Horticulture, Tamil Nadu)
by crop heading. 442 pages covering fruits, vegetables, spices, mushrooms, flowers, medicinal plants.
Output: data/horticulture_rag_knowledge.json
"""
import json
import re
import pdfplumber
from pathlib import Path

PDF_PATH = '/Users/nishchay/.gemini/antigravity/brain/6cdf87bc-cac4-49e1-871e-a46d582007a0/.user_uploaded/media_1794545074017_671e3eec.pdf'
OUTPUT_FILE = Path(__file__).parent.parent / 'data' / 'horticulture_rag_knowledge.json'

SOURCE = 'Crop Production Guide - Horticulture Crops 2020 (Directorate of Horticulture, Tamil Nadu & TNAU)'
SOURCE_URL = 'https://tnau.ac.in'

# Crop headings in this PDF (from TOC)
CROP_HEADINGS = {
    # Fruits
    'Mango': ('fruit_crop', 'Mangifera indica'),
    'Banana': ('fruit_crop', 'Musa spp.'),
    'Acid Lime': ('fruit_crop', 'Citrus aurantiifolia'),
    'Sweet Orange': ('fruit_crop', 'Citrus sinensis'),
    'Mandarin Orange': ('fruit_crop', 'Citrus reticulata'),
    'Grapes': ('fruit_crop', 'Vitis vinifera'),
    'Guava': ('fruit_crop', 'Psidium guajava'),
    'Pineapple': ('fruit_crop', 'Ananas comosus'),
    'Sapota': ('fruit_crop', 'Manilkara zapota'),
    'Papaya': ('fruit_crop', 'Carica papaya'),
    'Pomegranate': ('fruit_crop', 'Punica granatum'),
    'Jack': ('fruit_crop', 'Artocarpus heterophyllus'),
    'Ber': ('fruit_crop', 'Ziziphus mauritiana'),
    'Amla': ('fruit_crop', 'Phyllanthus emblica'),
    'Apple': ('fruit_crop', 'Malus domestica'),
    'Pear': ('fruit_crop', 'Pyrus communis'),
    'Plum': ('fruit_crop', 'Prunus domestica'),
    'Peach': ('fruit_crop', 'Prunus persica'),
    # Vegetables
    'Tomato': ('vegetable_crop', 'Solanum lycopersicum'),
    'Brinjal': ('vegetable_crop', 'Solanum melongena'),
    'Bhendi': ('vegetable_crop', 'Abelmoschus esculentus'),
    'Chilli': ('vegetable_crop', 'Capsicum annuum'),
    'Capsicum': ('vegetable_crop', 'Capsicum annuum'),
    'Potato': ('vegetable_crop', 'Solanum tuberosum'),
    'Tapioca': ('vegetable_crop', 'Manihot esculenta'),
    'Yam': ('vegetable_crop', 'Dioscorea spp.'),
    'Pumpkin': ('vegetable_crop', 'Cucurbita moschata'),
    'Bitter Gourd': ('vegetable_crop', 'Momordica charantia'),
    'Bottle Gourd': ('vegetable_crop', 'Lagenaria siceraria'),
    'Ridge Gourd': ('vegetable_crop', 'Luffa acutangula'),
    'Snake Gourd': ('vegetable_crop', 'Trichosanthes cucumerina'),
    'Ash Gourd': ('vegetable_crop', 'Benincasa hispida'),
    'Cucumber': ('vegetable_crop', 'Cucumis sativus'),
    'Gherkin': ('vegetable_crop', 'Cucumis anguria'),
    'Watermelon': ('vegetable_crop', 'Citrullus lanatus'),
    'Muskmelon': ('vegetable_crop', 'Cucumis melo'),
    'Cluster Bean': ('vegetable_crop', 'Cyamopsis tetragonoloba'),
    'French Bean': ('vegetable_crop', 'Phaseolus vulgaris'),
    'Broad Bean': ('vegetable_crop', 'Vicia faba'),
    'Peas': ('vegetable_crop', 'Pisum sativum'),
    'Annual Moringa': ('vegetable_crop', 'Moringa oleifera'),
    'Baby Corn': ('vegetable_crop', 'Zea mays'),
    'Cabbage': ('vegetable_crop', 'Brassica oleracea'),
    'Cauliflower': ('vegetable_crop', 'Brassica oleracea var. botrytis'),
    'Carrot': ('vegetable_crop', 'Daucus carota'),
    'Beetroot': ('vegetable_crop', 'Beta vulgaris'),
    'Radish': ('vegetable_crop', 'Raphanus sativus'),
    'Turnip': ('vegetable_crop', 'Brassica rapa'),
    'Onion': ('vegetable_crop', 'Allium cepa'),
    'Garlic': ('vegetable_crop', 'Allium sativum'),
    'Amaranthus': ('vegetable_crop', 'Amaranthus spp.'),
    'Spinach': ('vegetable_crop', 'Spinacia oleracea'),
    'Fenugreek': ('vegetable_crop', 'Trigonella foenum-graecum'),
    'Moringa': ('vegetable_crop', 'Moringa oleifera'),
    # Spices
    'Pepper': ('spice_crop', 'Piper nigrum'),
    'Cardamom': ('spice_crop', 'Elettaria cardamomum'),
    'Turmeric': ('spice_crop', 'Curcuma longa'),
    'Ginger': ('spice_crop', 'Zingiber officinale'),
    'Clove': ('spice_crop', 'Syzygium aromaticum'),
    'Nutmeg': ('spice_crop', 'Myristica fragrans'),
    'Cinnamon': ('spice_crop', 'Cinnamomum verum'),
    'Tamarind': ('spice_crop', 'Tamarindus indica'),
    'Coriander': ('spice_crop', 'Coriandrum sativum'),
    # Plantation / Others
    'Coconut': ('plantation_crop', 'Cocos nucifera'),
    'Arecanut': ('plantation_crop', 'Areca catechu'),
    'Cashew': ('plantation_crop', 'Anacardium occidentale'),
    'Coffee': ('plantation_crop', 'Coffea arabica'),
    'Tea': ('plantation_crop', 'Camellia sinensis'),
    'Rubber': ('plantation_crop', 'Hevea brasiliensis'),
    # Flowers
    'Rose': ('flower_crop', 'Rosa spp.'),
    'Jasmine': ('flower_crop', 'Jasminum sambac'),
    'Chrysanthemum': ('flower_crop', 'Chrysanthemum morifolium'),
    'Marigold': ('flower_crop', 'Tagetes erecta'),
    'Crossandra': ('flower_crop', 'Crossandra infundibuliformis'),
    # Medicinal
    'Glory Lilly': ('medicinal_plant', 'Gloriosa superba'),
    'Coleus': ('medicinal_plant', 'Plectranthus barbatus'),
    'Senna': ('medicinal_plant', 'Senna alexandrina'),
    'Periwinkle': ('medicinal_plant', 'Catharanthus roseus'),
    # Aromatic
    'Lemongrass': ('aromatic_plant', 'Cymbopogon citratus'),
    'Mint': ('aromatic_plant', 'Mentha spp.'),
}

# Build lookup by uppercase name
CROP_LOOKUP = {k.upper(): (k, v[0], v[1]) for k, v in CROP_HEADINGS.items()}
# Also add aliases
CROP_ALIASES_EXTRA = {
    'BHENDI': 'Bhendi',
    'OKRA': 'Bhendi',
    'LADIESFINGER': 'Bhendi',
    'BRINJAL': 'Brinjal',
    'CHOW CHOW': 'Ash Gourd',
    'TINDA': 'Muskmelon',
    'VEGETABLE COWPEA': 'Cluster Bean',
    'LAB LAB': 'Cluster Bean',
    'DOLICHOS BEAN': 'French Bean',
}


def table_to_markdown(table_data):
    if not table_data or len(table_data) < 1:
        return ''
    rows = [r for r in table_data if any(c and str(c).strip() for c in r)]
    if not rows:
        return ''
    md_rows = []
    for i, row in enumerate(rows):
        cells = [str(c or '').strip().replace('\n', ' ') for c in row]
        md_rows.append('| ' + ' | '.join(cells) + ' |')
        if i == 0:
            md_rows.append('| ' + ' | '.join(['---'] * len(cells)) + ' |')
    return '\n'.join(md_rows)


def detect_crop_heading(text):
    """Check if text contains a crop heading. Returns (crop_name, category, sci_name) or None."""
    lines = text.split('\n')
    for line in lines[:6]:
        line_clean = line.strip()
        if not line_clean:
            continue
        # Pattern: "1. Mango (Mangifera indica L.); Family"
        m = re.match(r'^\d+\.\s+(.+?)(?:\s+\(|$)', line_clean)
        if m:
            candidate = m.group(1).strip()
            cu = candidate.upper()
            if cu in CROP_LOOKUP:
                return CROP_LOOKUP[cu]
            # Try partial match
            for key, val in CROP_LOOKUP.items():
                if key in cu and len(key) > 3:
                    return val
        
        # Plain heading: "Mango (Mangifera indica L.)"
        m2 = re.match(r'^([A-Z][a-zA-Z\s]{2,30}?)(?:\s+\(|$|\n)', line_clean)
        if m2:
            candidate = m2.group(1).strip()
            cu = candidate.upper()
            if cu in CROP_LOOKUP:
                return CROP_LOOKUP[cu]
        
        # Check aliases
        line_up = line_clean.upper()
        for alias, real in CROP_ALIASES_EXTRA.items():
            if alias in line_up:
                if real.upper() in CROP_LOOKUP:
                    return CROP_LOOKUP[real.upper()]
    
    return None


def classify_topic(text):
    text_up = text.upper()
    if any(w in text_up for w in ['MANURES AND FERTILIZER', 'FERTILIZER', 'NPK', 'UREA', 'DAP', 'FERTIGATION', 'NUTRIENT']):
        return 'fertilizer_management'
    if any(w in text_up for w in ['PLANT PROTECTION', 'PESTS', 'INSECT', 'APHID', 'MITE', 'BORER', 'SPRAY', 'INSECTICIDE']):
        return 'pest_management'
    if any(w in text_up for w in ['DISEASES', 'FUNGAL', 'BLIGHT', 'ROT', 'MILDEW', 'WILT', 'FUNGICIDE', 'POWDERY']):
        return 'disease_management'
    if any(w in text_up for w in ['VARIET', 'HYBRID', 'CULTIVAR', 'ROOTSTOCK']):
        return 'varieties'
    if any(w in text_up for w in ['HARVEST', 'YIELD', 'POST-HARVEST', 'STORAGE', 'GRADING']):
        return 'harvesting_and_yield'
    if any(w in text_up for w in ['IRRIGATION', 'WATER', 'DRIP', 'SCHEDULE']):
        return 'irrigation'
    if any(w in text_up for w in ['WEED', 'HERBICIDE']):
        return 'weed_management'
    if any(w in text_up for w in ['NURSERY', 'PROPAGATION', 'SEED', 'CUTTING', 'GRAFTING']):
        return 'propagation'
    return 'general_cultivation'


def build_entries(crop_name, category, sci_name, pages_data):
    entries = []
    
    # Accumulate text and tables
    all_text = []
    all_tables_raw = []
    for text, tables in pages_data:
        if text:
            all_text.append(text.strip())
        all_tables_raw.extend(tables)
    
    full_text = '\n'.join(all_text)
    if not full_text.strip() and not all_tables_raw:
        return entries
    
    # Build topic buckets
    topic_buckets = {}
    
    # Split by section headers in text
    section_patterns = [
        ('fertilizer_management', [r'Manures\s+and\s+Fertilizer', r'Fertigation\s+[Ss]chedule', r'FERTILIZER\s+SCHEDULE']),
        ('pest_management', [r'Plant\s+Protection', r'(?:^|\n)Pests?\n', r'1\.\s+Pests?']),
        ('disease_management', [r'(?:^|\n)Diseases?\n', r'2\.\s+Diseases?']),
        ('varieties', [r'Varieties\b', r'Cultivars?\b']),
        ('harvesting_and_yield', [r'Harvest', r'Yield', r'Post.harvest']),
        ('propagation', [r'Nursery', r'Propagation', r'Planting']),
    ]
    
    for topic, patterns in section_patterns:
        combined = []
        for pat in patterns:
            m = re.search(pat, full_text, re.IGNORECASE | re.MULTILINE)
            if m:
                chunk = full_text[m.start():m.start()+2000].strip()
                combined.append(chunk)
                break
        if combined:
            topic_buckets[topic] = '\n'.join(combined)
    
    # Sort tables into buckets
    fert_tables, pest_tables, gen_tables = [], [], []
    for t in all_tables_raw:
        if not t:
            continue
        t_str = ' '.join(str(c or '') for row in t[:3] for c in row).upper()
        if any(w in t_str for w in ['FYM', 'UREA', 'DAP', 'NPK', 'N ', 'P ', 'K ', 'KG/TREE', 'KG/HA', 'DOSE', 'FERTILIZER', 'MANURE']):
            fert_tables.append(t)
        elif any(w in t_str for w in ['INSECTICIDE', 'FUNGICIDE', 'PESTICIDE', 'SPRAY', 'DOSE', 'ML/L']):
            pest_tables.append(t)
        else:
            gen_tables.append(t)
    
    # Create entries per topic
    crop_key = crop_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
    
    topic_data = []
    if 'fertilizer_management' in topic_buckets or fert_tables:
        topic_data.append(('fertilizer_management', topic_buckets.get('fertilizer_management', ''), fert_tables))
    if 'pest_management' in topic_buckets or pest_tables:
        topic_data.append(('pest_management', topic_buckets.get('pest_management', ''), pest_tables))
    if 'disease_management' in topic_buckets:
        topic_data.append(('disease_management', topic_buckets['disease_management'], []))
    if 'varieties' in topic_buckets:
        topic_data.append(('varieties', topic_buckets['varieties'], []))
    if 'harvesting_and_yield' in topic_buckets:
        topic_data.append(('harvesting_and_yield', topic_buckets['harvesting_and_yield'], gen_tables[:2]))
    if 'propagation' in topic_buckets:
        topic_data.append(('propagation', topic_buckets['propagation'], []))
    
    # Fallback: general cultivation
    if not topic_data:
        topic_data.append(('general_cultivation', full_text[:3000], all_tables_raw[:3]))
    
    for topic, text, tables in topic_data:
        answer_parts = [text.strip()] if text.strip() else []
        for t in tables:
            md = table_to_markdown(t)
            if md:
                answer_parts.append('\n\n**Table:**\n' + md)
        answer = '\n'.join(answer_parts).strip()
        
        if len(answer) < 40:
            continue
        
        topic_label = topic.replace('_', ' ').title()
        entry = {
            "id": f"hort_{crop_key}_{topic}",
            "crop": crop_name,
            "scientific_name": sci_name,
            "category": category,
            "farming_type": "conventional",
            "topic": topic,
            "title": f"{crop_name} - {topic_label}",
            "question": generate_question(crop_name, topic),
            "answer": answer,
            "keywords": extract_keywords(crop_name, topic, answer),
            "source": SOURCE,
            "source_url": SOURCE_URL,
        }
        entries.append(entry)
    
    return entries


def generate_question(crop_name, topic):
    questions = {
        'fertilizer_management': f'What is the fertilizer and manure schedule for {crop_name}?',
        'pest_management': f'How to control pests in {crop_name}?',
        'disease_management': f'How to manage diseases in {crop_name}?',
        'varieties': f'What are the recommended varieties of {crop_name}?',
        'harvesting_and_yield': f'When and how to harvest {crop_name}?',
        'irrigation': f'What is the irrigation schedule for {crop_name}?',
        'weed_management': f'How to control weeds in {crop_name}?',
        'propagation': f'How to propagate or plant {crop_name}?',
        'general_cultivation': f'What are the cultivation practices for {crop_name}?',
    }
    return questions.get(topic, f'How to grow {crop_name}?')


def extract_keywords(crop_name, topic, answer):
    keywords = [crop_name.lower()]
    topic_kw = {
        'fertilizer_management': ['fertilizer', 'manure', 'npk', 'urea', 'dap', 'nutrient', 'fertigation'],
        'pest_management': ['pest', 'insect', 'spray', 'control', 'insecticide', 'neem'],
        'disease_management': ['disease', 'fungicide', 'blight', 'rot', 'mildew', 'wilt'],
        'varieties': ['variety', 'hybrid', 'cultivar', 'recommended'],
        'harvesting_and_yield': ['harvest', 'yield', 'storage', 'post-harvest'],
        'irrigation': ['irrigation', 'drip', 'water'],
        'propagation': ['nursery', 'propagation', 'grafting', 'seedling'],
        'general_cultivation': ['cultivation', 'farming', 'practices'],
    }
    keywords.extend(topic_kw.get(topic, []))
    doses = re.findall(r'\d+[\s]?(?:kg|g|ml|l)/(?:ha|acre|plant|tree|litre)', answer, re.IGNORECASE)
    keywords.extend([d.lower() for d in doses[:3]])
    return list(dict.fromkeys(keywords))


def main():
    print('Parsing Horticulture PDF (442 pages)...')
    all_entries = []
    
    crop_pages = {}
    current_crop = None
    current_cat = 'general'
    current_sci = ''
    
    with pdfplumber.open(PDF_PATH) as pdf:
        print(f'Total pages: {len(pdf.pages)}')
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ''
            tables = page.extract_tables() or []
            
            # Detect crop heading on this page
            detected = detect_crop_heading(text)
            if detected:
                crop_name, cat, sci = detected
                if crop_name != current_crop:
                    current_crop = crop_name
                    current_cat = cat
                    current_sci = sci
                    print(f'  P.{page_num+1}: {crop_name}')
            
            if current_crop:
                key = current_crop
                if key not in crop_pages:
                    crop_pages[key] = {'pages': [], 'cat': current_cat, 'sci': current_sci}
                crop_pages[key]['pages'].append((text, tables))
    
    print(f'\nDetected {len(crop_pages)} crops')
    
    for crop_name, data in crop_pages.items():
        entries = build_entries(crop_name, data['cat'], data['sci'], data['pages'])
        all_entries.extend(entries)
        print(f'  {crop_name}: {len(entries)} entries')
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, indent=2, ensure_ascii=False)
    
    print(f'\nSaved {len(all_entries)} entries to {OUTPUT_FILE}')


if __name__ == '__main__':
    main()

