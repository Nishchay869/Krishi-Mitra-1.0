"""
Parse Farmer's Handbook on Basic Agriculture (154 pages, GIZ/MANAGE/NAVSARI).
Covers: Soil & plant nutrition, pest management, farm management, occupational safety.
Topic-based entries (not crop-specific) with practical tables.
Output: data/farmerbook_rag_knowledge.json
"""
import json
import re
import pdfplumber
from pathlib import Path

PDF_PATH = '/Users/nishchay/.gemini/antigravity/brain/6cdf87bc-cac4-49e1-871e-a46d582007a0/.user_uploaded/media_1794545102960_ce692e75.pdf'
OUTPUT_FILE = Path(__file__).parent.parent / 'data' / 'farmerbook_rag_knowledge.json'

SOURCE = "Farmer's Handbook on Basic Agriculture (MANAGE, Ministry of Agriculture, GoI & GIZ)"
SOURCE_URL = 'https://manage.gov.in'

CHAPTER_HEADINGS = {
    'General Conditions for Cultivation of Crops': 'general_cultivation',
    'Soil and Plant Nutrition': 'fertilizer_management',
    'Plant Protection': 'pest_management',
    'Categories of Pesticides and Precautions': 'pest_management',
    'Farm Management': 'farm_management',
    'Occupational Health and Safety': 'safety',
    "Farmer's Access to Service": 'general',
}


def table_to_markdown(table_data):
    if not table_data:
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


def detect_chapter(line):
    """Return (chapter_title, topic) if line matches a chapter heading."""
    for heading, topic in CHAPTER_HEADINGS.items():
        if heading.lower() in line.lower():
            return (heading, topic)
    return None


def main():
    print('Parsing Farmer Book (154 pages)...')
    all_entries = []
    
    with pdfplumber.open(PDF_PATH) as pdf:
        print(f'Total pages: {len(pdf.pages)}')
        
        # Read all pages
        chapter_data = {}
        current_chapter = 'General Conditions for Cultivation of Crops'
        current_topic = 'general_cultivation'
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ''
            tables = page.extract_tables() or []
            
            # Detect chapter heading in first few lines
            lines = text.split('\n')
            for line in lines[:3]:
                detected = detect_chapter(line)
                if detected:
                    current_chapter, current_topic = detected
                    print(f'  P.{page_num+1}: Chapter → {current_chapter}')
                    break
            
            if current_chapter not in chapter_data:
                chapter_data[current_chapter] = {'text': [], 'tables': [], 'topic': current_topic}
            chapter_data[current_chapter]['text'].append(text)
            chapter_data[current_chapter]['tables'].extend(tables)
        
        print(f'\nDetected {len(chapter_data)} chapters')
        
        # Build entries per chapter with sub-topic splitting
        for chapter_title, data in chapter_data.items():
            full_text = '\n'.join(data['text'])
            topic = data['topic']
            tables_md = []
            for t in data['tables'][:8]:
                md = table_to_markdown(t)
                if md:
                    tables_md.append(md)
            
            if topic == 'general_cultivation':
                # Split into sub-topics
                subtopics = extract_cultivation_subtopics(full_text)
                for sub_title, sub_text in subtopics:
                    if len(sub_text) < 50:
                        continue
                    crop_key = sub_title.lower().replace(' ', '_').replace('/', '_')
                    all_entries.append({
                        "id": f"farmerbook_{crop_key}",
                        "crop": "General",
                        "scientific_name": "",
                        "category": "general",
                        "farming_type": "general",
                        "topic": "general_cultivation",
                        "title": f"Basic Agriculture - {sub_title}",
                        "question": f"What are the factors for {sub_title.lower()} in agriculture?",
                        "answer": sub_text[:3000].strip(),
                        "keywords": ["basic agriculture", "farming", sub_title.lower(), "india"],
                        "source": SOURCE,
                        "source_url": SOURCE_URL,
                    })
            
            elif topic == 'fertilizer_management':
                # Soil & Plant Nutrition - very valuable tables
                entry_text = full_text[:4000]
                if tables_md:
                    entry_text += '\n\n**Nutrient Reference Tables:**\n\n' + '\n\n'.join(tables_md[:4])
                all_entries.append({
                    "id": "farmerbook_soil_plant_nutrition",
                    "crop": "General",
                    "scientific_name": "",
                    "category": "general",
                    "farming_type": "general",
                    "topic": "fertilizer_management",
                    "title": "Soil and Plant Nutrition - Macro & Micronutrients Guide",
                    "question": "What are soil nutrient requirements and how to manage plant nutrition?",
                    "answer": entry_text.strip(),
                    "keywords": ["soil nutrition", "plant nutrition", "macronutrient", "micronutrient", "nitrogen", "phosphorus", "potassium", "deficiency", "fertilizer"],
                    "source": SOURCE,
                    "source_url": SOURCE_URL,
                })
                
                # Also create NPK specific entry
                npk_m = re.search(r'[Nn]itrogen|[Pp]hosphorus|[Pp]otassium|NPK', full_text)
                if npk_m:
                    npk_text = full_text[npk_m.start():npk_m.start()+3000]
                    all_entries.append({
                        "id": "farmerbook_npk_nutrients",
                        "crop": "General",
                        "scientific_name": "",
                        "category": "general",
                        "farming_type": "general",
                        "topic": "fertilizer_management",
                        "title": "NPK and Micronutrient Functions and Deficiency Symptoms",
                        "question": "What are deficiency symptoms of nitrogen, phosphorus, potassium and micronutrients in plants?",
                        "answer": npk_text.strip(),
                        "keywords": ["nitrogen deficiency", "phosphorus deficiency", "potassium deficiency", "npk", "micronutrient", "iron deficiency", "zinc deficiency", "chlorosis"],
                        "source": SOURCE,
                        "source_url": SOURCE_URL,
                    })
                
                # Organic matter entry
                org_m = re.search(r'[Oo]rganic\s+matter|[Cc]ompost|[Mm]anure|FYM', full_text)
                if org_m:
                    org_text = full_text[org_m.start():org_m.start()+2000]
                    all_entries.append({
                        "id": "farmerbook_organic_matter",
                        "crop": "General",
                        "scientific_name": "",
                        "category": "organic_farming",
                        "farming_type": "organic",
                        "topic": "fertilizer_management",
                        "title": "Organic Matter, Compost and Manure Management",
                        "question": "How to improve soil organic matter using compost, FYM and green manure?",
                        "answer": org_text.strip(),
                        "keywords": ["organic matter", "compost", "FYM", "farm yard manure", "green manure", "soil health", "humus"],
                        "source": SOURCE,
                        "source_url": SOURCE_URL,
                    })
            
            elif topic == 'pest_management':
                # Plant Protection section
                pest_text = full_text[:3000]
                if tables_md:
                    pest_text += '\n\n**Pesticide Reference Tables:**\n\n' + '\n\n'.join(tables_md[:3])
                all_entries.append({
                    "id": "farmerbook_plant_protection",
                    "crop": "General",
                    "scientific_name": "",
                    "category": "general",
                    "farming_type": "general",
                    "topic": "pest_management",
                    "title": "Plant Protection - IPM and Pesticide Management",
                    "question": "What are the plant protection methods and IPM practices for controlling pests and diseases?",
                    "answer": pest_text.strip(),
                    "keywords": ["ipm", "integrated pest management", "pesticide", "insecticide", "fungicide", "biological control", "plant protection"],
                    "source": SOURCE,
                    "source_url": SOURCE_URL,
                })
                
                # Pesticide categories
                cat_m = re.search(r'[Cc]ategories\s+of\s+[Pp]esticide|[Pp]esticide\s+[Ss]afety|[Pp]recaution', full_text)
                if cat_m:
                    cat_text = full_text[cat_m.start():cat_m.start()+2000]
                    if tables_md:
                        cat_text += '\n\n' + '\n\n'.join(tables_md[:2])
                    all_entries.append({
                        "id": "farmerbook_pesticide_categories",
                        "crop": "General",
                        "scientific_name": "",
                        "category": "general",
                        "farming_type": "general",
                        "topic": "pest_management",
                        "title": "Categories of Pesticides, Safety Precautions and PHI",
                        "question": "What are the categories of pesticides and what precautions should farmers take?",
                        "answer": cat_text.strip(),
                        "keywords": ["pesticide category", "pesticide safety", "preharvest interval", "phi", "toxicity", "label reading", "protective gear"],
                        "source": SOURCE,
                        "source_url": SOURCE_URL,
                    })
            
            elif topic == 'farm_management':
                farm_text = full_text[:3000]
                if tables_md:
                    farm_text += '\n\n' + '\n\n'.join(tables_md[:2])
                all_entries.append({
                    "id": "farmerbook_farm_management",
                    "crop": "General",
                    "scientific_name": "",
                    "category": "general",
                    "farming_type": "general",
                    "topic": "general_cultivation",
                    "title": "Farm Management - Planning, Record Keeping and Market Access",
                    "question": "What are the key farm management practices for profitability?",
                    "answer": farm_text.strip(),
                    "keywords": ["farm management", "planning", "record keeping", "market access", "cost benefit", "profitability"],
                    "source": SOURCE,
                    "source_url": SOURCE_URL,
                })
        
        print(f'\nTotal entries: {len(all_entries)}')
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_entries, f, indent=2, ensure_ascii=False)
        
        print(f'Saved {len(all_entries)} entries to {OUTPUT_FILE}')
        for e in all_entries:
            print(f"  {e['title'][:70]}")


def extract_cultivation_subtopics(text):
    """Extract subtopics from general cultivation chapter."""
    subtopics = []
    
    sub_patterns = [
        ('Crop Selection Factors', r'[Ff]actors\s+influencing\s+decisions|[Cc]rop\s+selection'),
        ('Climate and Cropping Patterns', r'[Cc]limate.*cropping\s+pattern|[Cc]ropping\s+pattern.*climate'),
        ('Pest and Disease from Climate Change', r'[Cc]hange\s+in\s+pest|[Cc]limate\s+change.*pest'),
        ('Coping Options for Farmers', r'[Cc]oping\s+options?\s+for\s+farmers'),
        ('Crop Rotation Benefits', r'[Cc]rop\s+rotation'),
        ('Seed Selection and Treatment', r'[Ss]eed\s+(?:selection|treatment|quality)'),
        ('Soil Preparation and Tillage', r'[Ss]oil\s+preparation|[Tt]illage|[Ll]and\s+preparation'),
        ('Irrigation and Water Management', r'[Ii]rrigation|[Ww]ater\s+management'),
    ]
    
    for sub_title, pat in sub_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            sub_text = text[m.start():m.start()+1500]
            subtopics.append((sub_title, sub_text))
    
    return subtopics


if __name__ == '__main__':
    main()

