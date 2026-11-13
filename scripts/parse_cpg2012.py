"""
Parse CPG 2012 (Tamil Nadu Crop Production Guide) by crop heading.
Converts tables to Markdown, one chunk per crop per topic.
Output: data/cpg2012_rag_knowledge.json
"""
import json
import re
import pdfplumber
from pathlib import Path

PDF_PATH = '/Users/nishchay/.gemini/antigravity/brain/6cdf87bc-cac4-49e1-871e-a46d582007a0/.user_uploaded/media_1794545089253_1ecb4d17.pdf'
OUTPUT_FILE = Path(__file__).parent.parent / 'data' / 'cpg2012_rag_knowledge.json'

SOURCE = 'Tamil Nadu Crop Production Guide 2012 (Dept. of Agriculture, Govt. of Tamil Nadu & TNAU)'
SOURCE_URL = 'https://tnau.ac.in'

# Known crop headings from the TOC
CROP_HEADINGS = [
    'RICE', 'SORGHUM', 'CUMBU', 'RAGI', 'MAIZE', 'WHEAT',
    'REDGRAM', 'BLACKGRAM', 'GREENGRAM', 'COWPEA', 'HORSEGRAM',
    'BENGALGRAM', 'GROUNDNUT', 'SESAME', 'CASTOR', 'SUNFLOWER',
    'COCONUT', 'COTTON', 'SUGARCANE', 'TOMATO', 'BRINJAL',
    'BHENDI', 'CHILLI', 'CAPSICUM', 'POTATO', 'TAPIOCA',
    'BANANA', 'MANGO', 'TURMERIC', 'GINGER', 'PEPPER',
    'CARDAMOM', 'SOYABEAN', 'SAFFLOWER', 'OILPALM',
    'FODDER CHOLAM', 'FODDER CUMBU', 'FODDER MAIZE', 'GUINEA GRASS',
    'OYSTER MUSHROOM', 'MILKY MUSHROOM', 'JUTE', 'AGAVE',
    'SWEET SORGHUM', 'JATROPHA', 'NIGER', 'SWORD BEAN',
    'GARDEN LAB LAB', 'FIELD LAB LAB', 'LEUCAENA',
    # Aliases to map to canonical
]

CROP_ALIASES = {
    'CUMBU': 'Pearl Millet (Cumbu)',
    'RAGI': 'Finger Millet (Ragi)',
    'SORGHUM': 'Sorghum (Jowar)',
    'REDGRAM': 'Red Gram (Pigeon Pea)',
    'BLACKGRAM': 'Black Gram (Urad)',
    'GREENGRAM': 'Green Gram (Moong)',
    'BENGALGRAM': 'Bengal Gram (Chickpea)',
    'BHENDI': 'Bhendi (Okra)',
    'HORSEGRAM': 'Horse Gram',
    'SESAME': 'Sesame (Gingelly)',
    'CASTOR': 'Castor',
    'SAFFLOWER': 'Safflower',
    'OILPALM': 'Oil Palm',
    'NIGER': 'Niger',
    'TAPIOCA': 'Cassava (Tapioca)',
    'JATROPHA': 'Jatropha Curcas',
    'SWEET SORGHUM': 'Sweet Sorghum',
    'GARDEN LAB LAB': 'Lab Lab (Garden)',
    'FIELD LAB LAB': 'Lab Lab (Field)',
    'GUINEA GRASS': 'Guinea Grass',
    'FODDER CHOLAM': 'Fodder Sorghum (Cholam)',
    'FODDER CUMBU': 'Fodder Pearl Millet (Cumbu)',
    'FODDER MAIZE': 'Fodder Maize',
    'OYSTER MUSHROOM': 'Oyster Mushroom',
    'MILKY MUSHROOM': 'Milky Mushroom',
    'LEUCAENA': 'Leucaena (Soundal)',
}


def table_to_markdown(table_data):
    """Convert pdfplumber table (list of lists) to Markdown."""
    if not table_data or len(table_data) < 1:
        return ''
    # Filter out completely empty rows
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


def detect_crop_heading(line):
    """Return canonical crop name if line is a crop heading, else None."""
    line = line.strip()
    if not line:
        return None
    # Match patterns like "RICE (Oryza sativa L.)" or just "RICE" or "RAGI"
    # Remove scientific names in parentheses
    plain = re.sub(r'\(.*?\)', '', line).strip()
    plain_upper = plain.upper()
    
    for crop in CROP_HEADINGS:
        if plain_upper == crop or plain_upper.startswith(crop + ' '):
            return CROP_ALIASES.get(crop, crop.title())
    
    # Check for "MILLETS" section header
    if plain_upper == 'MILLETS':
        return None  # Section, not individual crop
    
    return None


def classify_topic(text_block):
    """Classify RAG topic from text content."""
    text_up = text_block.upper()
    if any(w in text_up for w in ['FERTILIZER', 'MANURE', 'NPK', 'NUTRIENT', 'UREA', 'DAP', 'PHOSPHO']):
        return 'fertilizer_management'
    if any(w in text_up for w in ['PEST', 'INSECT', 'APHID', 'BORER', 'MITE', 'WHITEFLY', 'SPRAY', 'INSECTICIDE']):
        return 'pest_management'
    if any(w in text_up for w in ['DISEASE', 'FUNGAL', 'BLIGHT', 'ROT', 'RUST', 'MILDEW', 'WILT', 'FUNGICIDE']):
        return 'disease_management'
    if any(w in text_up for w in ['VARIET', 'HYBRID', 'CULTIVAR', 'SEASON', 'ZONE']):
        return 'varieties_and_seasons'
    if any(w in text_up for w in ['HARVEST', 'YIELD', 'STORAGE', 'POST-HARVEST']):
        return 'harvesting_and_yield'
    if any(w in text_up for w in ['IRRIGATION', 'WATER', 'DRAINAGE']):
        return 'irrigation'
    if any(w in text_up for w in ['WEED', 'HERBICIDE']):
        return 'weed_management'
    if any(w in text_up for w in ['SEED', 'SOWING', 'PLANTING', 'SPACING', 'NURSERY']):
        return 'sowing_and_planting'
    return 'general_cultivation'


def build_entries_for_crop(crop_name, pages_data):
    """Build RAG entries from crop data (list of (text, tables) tuples)."""
    entries = []
    
    # Combine all text and tables for this crop
    full_text_parts = []
    full_tables = []
    for text, tables in pages_data:
        if text:
            full_text_parts.append(text.strip())
        full_tables.extend(tables)
    
    full_text = '\n'.join(full_text_parts)
    
    # Split into topic sections
    topic_sections = split_into_topic_sections(full_text, full_tables)
    
    crop_key = crop_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
    
    for i, (topic, text, tables) in enumerate(topic_sections):
        if len(text.strip()) < 50 and not tables:
            continue  # Skip trivially short sections
        
        # Build answer with tables embedded
        answer_parts = [text.strip()]
        for t in tables:
            md = table_to_markdown(t)
            if md:
                answer_parts.append('\n\n' + md)
        answer = '\n'.join(answer_parts).strip()
        
        if len(answer) < 30:
            continue
        
        topic_label = topic.replace('_', ' ').title()
        entry = {
            "id": f"cpg2012_{crop_key}_{topic}_{i}",
            "crop": crop_name,
            "scientific_name": "",
            "category": get_category(crop_name),
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


def split_into_topic_sections(full_text, all_tables):
    """Split crop text into topic sections."""
    # Try to find section markers
    section_markers = {
        'fertilizer_management': [
            r'(?:MANURES?\s+AND\s+FERTILIZER|FERTILIZER\s+MANAGEMENT|NUTRIENT\s+MANAGEMENT|BASAL\s+APPLICATION|NPK)',
        ],
        'pest_management': [
            r'(?:PEST\s+MANAGEMENT|INSECT\s+PEST|CROP\s+PROTECTION.*PEST|PLANT\s+PROTECTION)',
        ],
        'disease_management': [
            r'(?:DISEASE\s+MANAGEMENT|DISEASES?\s+AND|FUNGAL\s+DISEASE)',
        ],
        'varieties_and_seasons': [
            r'(?:SEASON\s+AND\s+VARIETIES|VARIETIES\s+AND\s+HYBRIDS|CROP\s+IMPROVEMENT|IMPROVED\s+VARIETIES)',
        ],
        'weed_management': [
            r'WEED\s+MANAGEMENT',
        ],
        'irrigation': [
            r'(?:WATER\s+MANAGEMENT|IRRIGATION)',
        ],
        'harvesting_and_yield': [
            r'(?:HARVEST|POST.HARVEST|YIELD)',
        ],
        'sowing_and_planting': [
            r'(?:SOWING|SEED\s+RATE|NURSERY|PLANTING|SPACING)',
        ],
    }
    
    # For simplicity, return one combined section per topic detected
    sections = []
    
    # Chunk by content type
    vartext = extract_section(full_text, [
        r'SEASON\s+AND\s+VARIETIES', r'CROP\s+IMPROVEMENT', r'I\.\s+SEASON',
        r'VARIETIES.*HYBRIDS'
    ])
    ferttext = extract_section(full_text, [
        r'MANURES?\s+AND\s+FERTILIZER', r'FERTILIZER\s+MANAGEMENT',
        r'NUTRIENT\s+MANAGEMENT', r'II\.\s+NUTRIENT', r'III\.\s+FERTILIZER',
        r'SOIL\s+FERTILITY', r'APPLICATION.*FERTILIZER'
    ])
    pesttext = extract_section(full_text, [
        r'PEST\s+MANAGEMENT', r'INSECT\s+PEST', r'PLANT\s+PROTECTION',
        r'CROP\s+PROTECTION', r'A\.\s+PEST'
    ])
    distext = extract_section(full_text, [
        r'DISEASE\s+MANAGEMENT', r'DISEASES', r'B\.\s+DISEASE',
        r'FUNGAL\s+DISEASE'
    ])
    sowtext = extract_section(full_text, [
        r'SEED\s+RATE', r'SOWING', r'NURSERY', r'PLANTING\s+MATERIAL',
        r'LAND\s+PREPARATION'
    ])
    
    # Collect tables by guessing their topic
    fert_tables = []
    pest_tables = []
    gen_tables = []
    var_tables = []
    for t in all_tables:
        if not t:
            continue
        t_str = ' '.join(str(c or '') for row in t[:3] for c in row).upper()
        if any(w in t_str for w in ['N ', 'P2O5', 'K2O', 'UREA', 'DAP', 'FERTILIZER', 'NPK', 'FYM', 'DOSE', 'KG/HA']):
            fert_tables.append(t)
        elif any(w in t_str for w in ['PEST', 'INSECT', 'APHID', 'BORER', 'ETL', 'SPRAY', 'INSECTICIDE', 'EC ', 'WP ']):
            pest_tables.append(t)
        elif any(w in t_str for w in ['VARIET', 'HYBRID', 'DURATION', 'PARENTAGE', 'ZONE', 'SEASON', 'MONTH']):
            var_tables.append(t)
        else:
            gen_tables.append(t)
    
    if vartext or var_tables:
        sections.append(('varieties_and_seasons', vartext or '', var_tables))
    if ferttext or fert_tables:
        sections.append(('fertilizer_management', ferttext or '', fert_tables))
    if pesttext or pest_tables:
        sections.append(('pest_management', pesttext or '', pest_tables))
    if distext:
        sections.append(('disease_management', distext, []))
    if sowtext:
        sections.append(('sowing_and_planting', sowtext, []))
    
    # If nothing was classified, dump everything as general
    if not sections:
        sections.append(('general_cultivation', full_text, all_tables))
    
    return sections


def extract_section(text, patterns):
    """Extract text that follows one of the given section header patterns."""
    # Find the earliest match
    best_start = None
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            if best_start is None or m.start() < best_start:
                best_start = m.start()
    if best_start is None:
        return ''
    # Extract up to 2000 chars from that point
    return text[best_start:best_start + 2500].strip()


def get_category(crop_name):
    cn = crop_name.upper()
    if any(w in cn for w in ['MANGO', 'BANANA', 'PAPAYA', 'GUAVA', 'COCONUT', 'JACK']):
        return 'fruit_crop'
    if any(w in cn for w in ['TOMATO', 'BRINJAL', 'CHILLI', 'BHENDI', 'OKRA', 'CAPSICUM', 'POTATO']):
        return 'vegetable_crop'
    if any(w in cn for w in ['RICE', 'WHEAT', 'RAGI', 'SORGHUM', 'MAIZE', 'CUMBU', 'MILLET']):
        return 'cereal_crop'
    if any(w in cn for w in ['REDGRAM', 'BLACKGRAM', 'GREENGRAM', 'COWPEA', 'BENGALGRAM', 'HORSEGRAM', 'SOYABEAN', 'LAB LAB']):
        return 'pulse_crop'
    if any(w in cn for w in ['GROUNDNUT', 'SESAME', 'CASTOR', 'SUNFLOWER', 'SAFFLOWER', 'OILPALM', 'NIGER']):
        return 'oilseed_crop'
    if any(w in cn for w in ['TURMERIC', 'GINGER', 'PEPPER', 'CARDAMOM']):
        return 'spice_crop'
    if any(w in cn for w in ['COTTON', 'JUTE']):
        return 'fibre_crop'
    if any(w in cn for w in ['SUGARCANE']):
        return 'sugar_crop'
    if any(w in cn for w in ['FODDER', 'GUINEA GRASS', 'LEUCAENA', 'NAPIER']):
        return 'fodder_crop'
    if any(w in cn for w in ['MUSHROOM']):
        return 'mushroom'
    return 'field_crop'


def generate_question(crop_name, topic):
    questions = {
        'fertilizer_management': f'What is the fertilizer dose and schedule for {crop_name}?',
        'pest_management': f'How to control pests in {crop_name}?',
        'disease_management': f'How to manage diseases in {crop_name}?',
        'varieties_and_seasons': f'What are the recommended varieties and seasons for {crop_name}?',
        'weed_management': f'How to control weeds in {crop_name}?',
        'irrigation': f'What is the irrigation schedule for {crop_name}?',
        'harvesting_and_yield': f'When and how to harvest {crop_name}?',
        'sowing_and_planting': f'What is the seed rate and sowing method for {crop_name}?',
        'general_cultivation': f'What are the cultivation practices for {crop_name}?',
    }
    return questions.get(topic, f'How to grow {crop_name}?')


def extract_keywords(crop_name, topic, answer):
    keywords = [crop_name.lower()]
    # Add common topic keywords
    topic_kw = {
        'fertilizer_management': ['fertilizer', 'npk', 'urea', 'dap', 'manure', 'nutrient'],
        'pest_management': ['pest', 'insect', 'spray', 'control', 'insecticide'],
        'disease_management': ['disease', 'fungicide', 'blight', 'rust', 'rot', 'mildew'],
        'varieties_and_seasons': ['variety', 'hybrid', 'season', 'duration', 'yield'],
        'weed_management': ['weed', 'herbicide'],
        'irrigation': ['irrigation', 'water', 'schedule'],
        'harvesting_and_yield': ['harvest', 'yield', 'storage'],
        'sowing_and_planting': ['seed rate', 'sowing', 'spacing', 'nursery'],
        'general_cultivation': ['cultivation', 'farming', 'practices'],
    }
    keywords.extend(topic_kw.get(topic, []))
    # Extract dose patterns from answer
    doses = re.findall(r'\d+[\s]?(?:kg|g|ml|l|t)/(?:ha|acre|plant|tree)', answer, re.IGNORECASE)
    keywords.extend([d.lower() for d in doses[:3]])
    return list(dict.fromkeys(keywords))  # deduplicate


def main():
    print('Parsing CPG 2012...')
    all_entries = []
    
    # Map: crop_name -> list of (text, tables)
    crop_pages = {}
    current_crop = None
    
    with pdfplumber.open(PDF_PATH) as pdf:
        print(f'Total pages: {len(pdf.pages)}')
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ''
            tables = page.extract_tables() or []
            
            # Check if page starts a new crop
            lines = text.split('\n')
            new_crop = None
            for line in lines[:5]:  # Check first 5 lines for heading
                detected = detect_crop_heading(line)
                if detected:
                    new_crop = detected
                    break
            
            if new_crop:
                current_crop = new_crop
                print(f'  P.{page_num+1}: Crop heading → {current_crop}')
            
            if current_crop:
                if current_crop not in crop_pages:
                    crop_pages[current_crop] = []
                crop_pages[current_crop].append((text, tables))
    
    print(f'\nDetected {len(crop_pages)} crops: {list(crop_pages.keys())}')
    
    # Build entries per crop
    for crop_name, pages_data in crop_pages.items():
        entries = build_entries_for_crop(crop_name, pages_data)
        all_entries.extend(entries)
        print(f'  {crop_name}: {len(entries)} entries')
    
    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, indent=2, ensure_ascii=False)
    
    print(f'\nSaved {len(all_entries)} entries to {OUTPUT_FILE}')
    return all_entries


if __name__ == '__main__':
    main()

