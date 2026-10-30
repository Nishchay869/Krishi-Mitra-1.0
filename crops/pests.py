"""Curated pest/disease references. No generative diagnosis or live outbreak claims."""
import json
from functools import lru_cache
from pathlib import Path
from django.templatetags.static import static
from .models import PestEntry
from .library import catalog as crop_catalog

ROOT = Path(__file__).parent/'data'
STAGES = [
    ('seedling','Seedling stage','bi-flower3','Establishment and nursery checks'),
    ('vegetative','Vegetative stage','bi-flower2','Leaves, roots and new shoots'),
    ('flowering','Flowering stage','bi-flower1','Buds, blossoms and pollinators'),
    ('fruiting','Fruiting stage','bi-basket2','Developing produce and crop filling'),
    ('harvest','Harvesting stage','bi-box-seam','Harvest quality and storage hygiene'),
]
KINDS = ('Fungus','Oomycete','Bacterium','Virus','Disease complex','Insect','Mite','Nematode','Non-infectious disorder')
PEST_KINDS = {'Insect','Mite','Nematode'}
MANAGEMENT = {
    'disease':[
        'Start with healthy planting material. Remove badly affected crop debris using locally recommended disposal practices.',
        'Reduce prolonged leaf wetness where practical, improve spacing and drainage, and avoid working through wet plants.',
        'Confirm the cause before treating. Use the crop-specific guide and local extension advice for a registered treatment and harvest restrictions.',
    ],
    'pest':[
        'Inspect several plants across the plot and check both damaged and apparently healthy plants. Identify the pest and its life stage.',
        'Protect beneficial insects. Remove infested material when practical and use crop-appropriate barriers, sanitation or monitoring traps.',
        'Use locally validated action thresholds. Select any treatment only after confirming the pest, crop label and harvest restrictions.',
    ],
    'virus':[
        'Use certified or healthy planting material and do not propagate from symptomatic plants.',
        'Check for the crop-specific insect vector. Clean tools when handling can transmit the virus and manage alternative hosts using local guidance.',
        'There is no general curative spray for virus-infected plants. Obtain confirmation and follow local guidance on removing affected plants.',
    ],
    'nematode':[
        'Inspect roots and submit a root-and-soil sample for confirmation; symptoms above ground overlap with water and nutrient stress.',
        'Avoid spreading infested soil and planting material. Plan crop-specific rotations or resistant rootstocks using the linked guide.',
        'Discuss local nematode management with extension staff before applying a product; species, soil and crop determine the options.',
    ],
    'disorder':[
        'Check water consistency, drainage and root health before assuming an infection.',
        'Use a soil or tissue test before correcting nutrients. Increasing fertilizer without a confirmed need can worsen stress.',
        'Remove damaged produce and correct the underlying growing conditions. Fungicides do not cure this physiological disorder.',
    ],
}


@lru_cache(maxsize=1)
def sources():
    return json.loads((ROOT/'pest_issues.json').read_text()), json.loads((ROOT/'pest_crops.json').read_text())


@lru_cache(maxsize=1)
def photographs():
    path=ROOT.parent.parent/'static/images/pests/credits.json'
    return json.loads(path.read_text())


def crops():
    _,mapping=sources()
    custom_counts = {}
    for entry in PestEntry.objects.values('crop_slug', 'issue_slug'):
        custom_counts.setdefault(entry['crop_slug'], []).append(entry['issue_slug'])
    return [dict(row, issue_count=len(set(mapping[row['name']]['issues']) | set(custom_counts.get(row['slug'], []))))
            for row in crop_catalog() if row['name'] in mapping]


def stages(crop):
    root_crops={'Onion','Garlic','Potato','Sweet potato','Carrot','Ginger','Turmeric'}
    cereals={'Rice','Wheat','Maize','Bajra','Ragi','Barley','Jowar'}
    perennial=crop['group'] in {'Fruits','Cash crops'}
    result=[]
    for slug,name,icon,note in STAGES:
        if slug=='seedling' and perennial:name='Nursery and establishment'
        if slug=='fruiting':
            if crop['name'] in root_crops:name='Bulb, root and tuber development'
            elif crop['name'] in cereals:name='Heading and grain filling'
            elif crop['group']=='Flowers':name='Bud and flower development'
            elif crop['name'] in {'Cotton','Sugarcane','Jute','Coffee','Arecanut','Cashewnut'}:name='Yield development'
        result.append({'slug':slug,'name':name,'icon':icon,'note':note})
    return result


def issues_for(crop):
    issues,mapping=sources();profile=mapping[crop['name']];photos=photographs()
    result=[]
    saved = {entry.issue_slug: entry for entry in PestEntry.objects.filter(crop_slug=crop['slug'])}
    for slug in dict.fromkeys([*profile['issues'], *saved]):
        row={**issues.get(slug, {'id': slug, 'cause': '', 'early': '', 'progress': '', 'conditions': ''}),
             **profile.get('overrides',{}).get(slug,{})}
        entry = saved.get(slug)
        if entry:
            row.update(name=entry.title, kind=entry.kind, stages=entry.stages,
                       edited=True, updated_at=entry.updated_at,
                       **{field: getattr(entry, field) for field in [
                           'symptoms', 'more_info', 'treat_now', 'organic_control',
                           'chemical_control', 'preventive_measures']})
            row['early'] = entry.symptoms
            row['cause'] = entry.more_info
        row['category']='pest' if row['kind'] in PEST_KINDS else 'disorder' if row['kind']=='Non-infectious disorder' else 'disease'
        # An issue name alone never establishes the photographed crop.
        photo = photos.get(f"{crop['slug']}--{slug}") or photos.get(slug)
        row['photo'] = photo if photo and crop['slug'] in photo.get('verified_crops', []) else None
        row['photo_path']='images/pests/'+row['photo']['file'] if row['photo'] else None
        row['photo_url'] = static(row['photo_path']) if row['photo_path'] else ''
        row['photo_caption'] = row['photo'].get('caption', row['photo']['title']) if row['photo'] else ''
        if entry and entry.photo:
            row.update(photo=None, photo_url=entry.photo.url,
                       photo_caption=entry.photo_caption or entry.title, uploaded_photo=True)
        row['sources'] = ([{'label': 'Administrator reference', 'url': entry.source_url}]
                          if entry and entry.source_url else []) if entry else profile['sources']
        row['stages']=[s for s in stages(crop) if s['slug'] in row['stages']]
        group='nematode' if row['kind']=='Nematode' else 'virus' if row['kind']=='Virus' else row['category']
        row['management']=MANAGEMENT[group]
        result.append(row)
    return result
