"""Regional N–P2O5–K2O references, checked 2026-10-29.

Field values are total kg/ha/crop; tree values are grams/tree/year.
These are regional references, not soil-test prescriptions. Sources also include
organic amendments and split applications, which product mass conversion omits.
"""
from accounts.localization import ui_text

BASE = 'https://agritech.tnau.ac.in/'
PRESETS = {
    'tomato': dict(crop='Tomato', mode='plants', rates=(150, 100, 50),
                   scope='Varieties', source=BASE+'govt_schemes_services/aas/tomato.html'),
    'potato': dict(crop='Potato', mode='plants', rates=(120, 240, 120),
                   scope='Whole crop season', source=BASE+'horticulture/horti_vegetables_potato.html'),
    'cucumber': dict(crop='Cucumber', mode='plants', rates=(150, 75, 75),
                     scope='Hybrids', source=BASE+'horticulture/horti_vegetables_cucumber.html'),
    'okra': dict(crop='Okra', mode='plants', rates=(40, 50, 30),
                 scope='Varieties', source=BASE+'horticulture/horti_vegetables_bhendi_irrigation.html'),
    'onion': dict(crop='Onion', mode='plants', rates=(60, 60, 30),
                  scope='Bellary onion', source=BASE+'horticulture/horti_veg_fert_onion.html'),
    'carrot': dict(crop='Carrot', mode='plants', rates=(135, 135, 135),
                   scope='Whole crop season', source=BASE+'horticulture/horti_veg_fert_carrot.html'),
    'taro': dict(crop='Taro', mode='plants', rates=(40, 60, 120),
                 scope='Whole crop season', source=BASE+'horticulture/horti_veg_fert_colacasia.html'),
    'rice': dict(crop='Rice', mode='plants', rates=(150, 50, 50),
                 scope='Medium and long duration varieties (wet season)',
                 source=BASE+'agriculture/agri_cropproduction_cereals_rice_tranpudlow_mainfield_nutrient_mgmt_inorganic.html'),
    'wheat': dict(crop='Wheat', mode='plants', rates=(80, 40, 40),
                  scope='Whole crop season', source=BASE+'agriculture/agri_nutrientmgt_wheat.html'),
}
for year in range(1, 7):
    factor = min(year, 5)
    PRESETS[f'mango-{year}'] = dict(
        crop='Mango', mode='trees', rates=(200*factor, 200*factor, 300*factor),
        age=str(year) if year < 6 else '6+', scope='Annual total',
        source=BASE+'horticulture/horti_fruits_fert_mango.html')
for year, rates in [(2, (140, 80, 300)), (3, (280, 160, 600)),
                    (4, (420, 240, 900)), (5, (560, 320, 1200))]:
    PRESETS[f'coconut-{year}'] = dict(
        crop='Coconut', mode='trees', rates=rates,
        age=str(year) if year < 5 else '5+', scope='Annual total',
        source=BASE+'expert_system/coconut/coconut/coconut_nutrient_management.html')


def preset_label(preset):
    label = ui_text(preset['crop'])
    if preset.get('age') == 'bearing':
        label += ' · ' + ui_text(preset['scope'])
    elif preset.get('age'):
        from django.utils.translation import gettext as _
        label += ' · ' + (_('Tree age (years): %(age)s') % {'age': preset['age']})
    return label

# Expanded regional references. Rates remain N, P2O5, K2O, never product masses.
VEGETABLE_SOURCE = BASE+'horticulture/FERTILIZER%20SCHEDULE%20FOR%20VEGETABLES.pdf'
FRUIT_SOURCE = BASE+'horticulture/FERTILIZER%20SCHEDULE%20FOR%20FRUIT%20CROPS.pdf'
FLOWER_SOURCE = BASE+'horticulture/FERTILIZER%20SCHEDULE%20FOR%20FLOWER%20CROPS.pdf'
SPICE_SOURCE = BASE+'horticulture/FERTILIZER%20SCHEDULE%20FOR%20SPICES.pdf'
PLANTATION_SOURCE = BASE+'horticulture/FERTILIZER%20SCHEDULE%20FOR%20PLANTATION%20CROPS.pdf'


def _add(key, crop, rates, source, stages=None, **metadata):
    PRESETS[key] = dict(crop=crop, rates=rates, source=source, mode='plants',
                        scope='Whole crop season', **metadata)
    if stages:
        PRESETS[key]['stages'] = stages


HALF_N = [('At planting', ('1/2','1','1')), ('30 days after planting', ('1/2','0','0'))]
ALL_BASAL = [('At sowing', ('1','1','1'))]
_add('brinjal','Brinjal',(100,50,30),VEGETABLE_SOURCE,HALF_N)
_add('pepper-bell','Pepper bell',(160,60,30),VEGETABLE_SOURCE,
     [('At planting',('1/4','1','1'))]+[(label,('1/4','0','0')) for label in
      ('30 days after planting','60 days after planting','90 days after planting')])
_add('garlic','Garlic',(75,75,75),VEGETABLE_SOURCE,
     [('At planting',('8/15','1','1')),('45 days after planting',('7/15','0','0'))])
_add('sweet-potato','Sweet potato',(40,80,120),VEGETABLE_SOURCE,
     [('At planting',('1/2','1/2','1/2')),('30 days after planting',('1/2','1/2','1/2'))])
_add('cabbage','Cabbage',(100,125,25),VEGETABLE_SOURCE,HALF_N)
_add('cauliflower','Cauliflower',(100,100,50),VEGETABLE_SOURCE,
     [('At planting',('1/2','1','1')),('45 days after planting',('1/2','0','0'))])
_add('muskmelon','Muskmelon',(80,60,30),VEGETABLE_SOURCE,
     [('At sowing',('1/2','1','1')),('30 days after sowing',('1/2','0','0'))])
_add('watermelon','Watermelon',(55,55,55),VEGETABLE_SOURCE,
     [('At sowing',('0','1','1')),('30 days after sowing',('1','0','0'))])
_add('pumpkin','Pumpkin',(16,12,12),VEGETABLE_SOURCE,
     [('At planting',('3/8','1','1')),('30 days after planting',('5/8','0','0'))],basis='plant')
# Pumpkin source: 100g of 6:12:12 per pit, then 10g N per pit. Count pits.
PRESETS['pumpkin']['count_pits'] = True
_add('cardamom','Cardamom',(75,75,150),SPICE_SOURCE,
     [('June–July',('1/2','1/2','1/2')),('October–November',('1/2','1/2','1/2'))])
PRESETS['cardamom']['scope']='Annual total'
_add('coriander','Coriander',(20,40,20),SPICE_SOURCE,
     [('At sowing',('1/2','1','1')),('30 days after sowing',('1/2','0','0'))])
_add('ginger','Ginger',(75,50,50),SPICE_SOURCE,
     [('At planting',('0','1','1/2')),('45 days after planting',('1/2','0','1/4')),
      ('90 days after planting',('1/2','0','1/4'))])
# Use the unambiguous narrative schedule: 25:60:18 basal + five 25:0:18 splits.
_add('turmeric','Turmeric',(150,60,108),SPICE_SOURCE,
     [('At planting',('1/6','1','1/6'))]+[(label,('1/6','0','1/6')) for label in
      ('30 days after planting','60 days after planting','90 days after planting',
       '120 days after planting','150 days after planting')])
_add('dry-chillies','Dry chillies',(120,60,30),VEGETABLE_SOURCE,
     [('At planting',('1/4','1','1'))]+[(label,('1/4','0','0')) for label in
      ('30 days after planting','60 days after planting','90 days after planting')])
for key,crop,rates,page,stages in [
    ('bajra','Bajra',(70,35,35),'cumbu', [('At sowing',('1/4','1','1')),
       ('15 days after sowing',('1/2','0','0')),('30 days after sowing',('1/4','0','0'))]),
    ('jowar','Jowar',(90,45,45),'sorghum', [('At sowing',('1/2','1','1')),
       ('15 days after sowing',('1/4','0','0')),('30 days after sowing',('1/4','0','0'))]),
    ('ragi','Ragi',(60,30,30),'ragi',None),
    ('chickpea','Chickpea',(25,50,25),'bengalgram',ALL_BASAL),
    ('cowpea','Cowpea(Lobia)',(25,50,25),'cowpea',ALL_BASAL),
    ('soybean','Soybean',(20,80,40),'soybean',ALL_BASAL),
    ('sunflower','Sunflower',(60,90,60),'sunflower',ALL_BASAL),
    ('jute','Jute',(40,20,20),'jute', [('At sowing',('1/2','1','1')),
       ('20–25 days after sowing',('1/4','0','0')),('35–40 days after sowing',('1/4','0','0'))]),
    ('sugarcane','Sugarcane',(300,100,200),'sugarcane',None),
]:
    _add(key,crop,rates,BASE+f'agriculture/agri_nutrientmgt_{page}.html',stages)
# These scope labels distinguish the source's regime from a universal dose.
for key in ('ragi','chickpea','cowpea','soybean'):
    PRESETS[key]['scope']='Irrigated crop'
PRESETS['sunflower']['scope']='Irrigated hybrids'
PRESETS['bajra']['scope']='Varieties'

_add('marigold','Marigold',(90,90,75),FLOWER_SOURCE,
     [('At planting',('1/2','1','1')),('45 days after planting',('1/2','0','0'))])
_add('tuberose','Tuberose',(200,200,200),FLOWER_SOURCE)
_add('rose','Rose',(12,24,24),FLOWER_SOURCE,
     [('After pruning in October',('1/2','1/2','1/2')),('July',('1/2','1/2','1/2'))],basis='plant')
PRESETS['rose']['scope']='Annual total'
_add('jasmine','Jasmine',(60,120,120),
     'https://egovernance.vikaspedia.in/viewcontent/agriculture/crop-production/package-of-practices/flowers/jasmine?lgn=en',
     [('June–July',('1/2','1/2','1/2')),('November, after pruning',('1/2','1/2','1/2'))],basis='plant')
PRESETS['jasmine']['scope']='Jasminum sambac · annual total'
_add('aster','Aster',(70,175,75),FLOWER_SOURCE,ALL_BASAL)
_add('chrysanthemum','Chrysanthemum',(125,120,25),FLOWER_SOURCE,HALF_N)
_add('gladiolus','Gladiolus',(120,150,150),FLOWER_SOURCE)
_add('crossandra','Crossandra',(75,50,125),FLOWER_SOURCE,
     [('3 months after planting',('1','1','1'))])
PRESETS['crossandra']['scope']='One application; repeat at six-month intervals as directed by the source'
_add('banana','Banana',(110,35,330),FRUIT_SOURCE,
     [('3 months after planting',('1/3','1','1/3')),('5 months after planting',('1/3','0','1/3')),
      ('7 months after planting',('1/3','0','1/3'))],basis='plant')
PRESETS['banana']['scope']='Garden land; non-Nendran varieties'
_add('papaya','Papaya',(50,50,50),FRUIT_SOURCE,
     [('Every two months, from month 3',('1','1','1'))],basis='plant')
PRESETS['papaya']['scope']='One application, not an annual total'
_add('pineapple','Pineapple',(16,4,12),FRUIT_SOURCE,
     [('6 months after planting',('1/2','1/2','1/2')),('12 months after planting',('1/2','1/2','1/2'))],basis='plant')
for key,crop,rates,scope,source,stages in [
    ('orange-bearing','Orange',(600,200,300),'Bearing sweet orange',FRUIT_SOURCE,
     [('March',('1/2','0','0')),('October',('1/2','1','1'))]),
    ('guava-bearing','Guava',(1000,1000,1000),'Bearing tree',FRUIT_SOURCE,
     [('March',('1/2','1/2','1/2')),('October',('1/2','1/2','1/2'))]),
    ('pomegranate-bearing','Pomegranate',(600,500,1200),'Age 6 years and above',FRUIT_SOURCE,None),
    ('apple-bearing','Apple',(500,1000,1000),'Bearing tree',FRUIT_SOURCE,None),
    ('peach-bearing','Peach',(500,1000,1000),'Bearing tree',FRUIT_SOURCE,None),
    ('litchi-bearing','Litchi',(100,40,400),'Age 10 years',FRUIT_SOURCE,
     [('December',('0','1','1')),('February',('1/2','0','0')),('April',('1/2','0','0'))]),
    ('jackfruit-bearing','Jackfruit',(750,400,500),'Age 6 years and above',FRUIT_SOURCE,
     [('May–June',('1/2','1/2','1/2')),('September–October',('1/2','1/2','1/2'))]),
    ('arecanut-bearing','Arecanut',(100,40,150),'Age 5 years and above',PLANTATION_SOURCE,
     [('January–February',('1','1','1'))]),
    ('cashewnut-bearing','Cashewnut',(500,200,300),'Age 5 years and above',PLANTATION_SOURCE,
     [('June–July',('1/2','1/2','1/2')),('October–November',('1/2','1/2','1/2'))]),
]:
    _add(key,crop,rates,source,stages)
    PRESETS[key].update(mode='trees',age='bearing',scope=scope)

# Keep crop category names consistent with onboarding and the crop library.
from accounts.onboarding import CROP_GROUPS
_groups = {name: group for group, crops in CROP_GROUPS for name, _ in crops}
for _preset in PRESETS.values():
    _preset['group'] = _groups.get(_preset['crop'], 'Flowers' if _preset['crop'] in
        {'Aster','Chrysanthemum','Gladiolus','Crossandra'} else 'Vegetables')

for _key in ('cabbage','cauliflower'):
    PRESETS[_key]['scope'] = 'Plains'
PRESETS['orange-bearing']['scope'] = 'Sweet orange, age 6 years and above'
PRESETS['jasmine'].update(source_org='Vikaspedia',source_region='India')
