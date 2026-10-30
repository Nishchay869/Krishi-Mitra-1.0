"""Product reference photos and user-initiated map searches; no stock claims."""
from urllib.parse import urlencode

PRODUCT_PHOTOS = {
    'UREA': dict(photo='images/fertilizers/urea.png', photo_label='Bharat Urea · SPIC',
                 photo_source='https://www.spic.in/products/primary-nutrients/'),
    'DAP': dict(photo='images/fertilizers/dap.png', photo_label='Bharat DAP · SPIC',
                photo_source='https://www.spic.in/products/primary-nutrients/'),
    'MOP': dict(photo='images/fertilizers/mop.png', photo_label='Bharat MOP · SPIC',
                photo_source='https://www.spic.in/productcms/bharat-mop-spic-mop-muriate-of-potash/'),
    'TSP': dict(photo='images/fertilizers/tsp.png', photo_label='Jai Kisaan Navratna TSP · Paradeep Phosphates',
                photo_source='https://jaikisaan.online/fertilizer?location=tsp'),
}


def shop_search_url(location, product=''):
    query = ' '.join(part for part in (product, 'fertilizer shops', 'near', location or 'me') if part)
    return 'https://www.google.com/maps/search/?' + urlencode({'api': '1', 'query': query})


def shop_context(profile):
    location = ', '.join(part.strip() for part in (profile.village, profile.district, profile.state) if part.strip())
    if location:
        location += ', India'
    return {'shop_location': location, 'shop_search_url': shop_search_url(location)}


def decorate_products(result, location):
    if not result:
        return
    for combination in result['combinations']:
        for product in combination['products']:
            product.update(PRODUCT_PHOTOS[product['code']])
            product['shop_search_url'] = shop_search_url(location, product['short_name'])

# Branded alternatives share the calculator's standard grade. Packaging photos
# identify products; they never establish local availability or price.
PRODUCT_VARIANTS = {
    'MOP': [
        dict(PRODUCT_PHOTOS['MOP'], id='spic-mop', pack_kg=50),
        dict(id='jai-kisaan-mop', photo='images/fertilizers/jai-kisaan-mop.jpg',
             photo_label='Bharat MOP · Jai Kisaan Navratna', pack_kg=50,
             photo_source='https://jaikisaan.online/fertilizer?location=zincated-dap'),
    ],
    'DAP': [
        dict(PRODUCT_PHOTOS['DAP'], id='spic-dap', pack_kg=50),
        dict(id='iffco-dap', photo='images/fertilizers/iffco-dap.png',
             photo_label='Bharat DAP · IFFCO', pack_kg=50,
             photo_source='https://www.iffco.in/en/dap-18-46-0'),
        dict(id='jai-kisaan-dap', photo='images/fertilizers/jai-kisaan-dap.png',
             photo_label='Bharat DAP · Jai Kisaan Navratna', pack_kg=50,
             photo_source='https://jaikisaan.online/fertilizer?location=zincated-dap'),
    ],
    'UREA': [
        dict(PRODUCT_PHOTOS['UREA'], id='spic-urea', pack_kg=45),
        dict(id='iffco-urea', photo='images/fertilizers/iffco-urea.jpeg',
             photo_label='Bharat Neem Coated Urea · IFFCO', pack_kg=45,
             photo_source='https://www.iffco.in/en/urea-fertilizer'),
    ],
    'TSP': [dict(PRODUCT_PHOTOS['TSP'], id='jai-kisaan-tsp', pack_kg=50)],
}


def relevant_products(products, location):
    variants = []
    for product in products:
        for variant in PRODUCT_VARIANTS[product['code']]:
            item = dict(product, **variant)
            item['shop_query'] = variant['photo_label'].replace('·', ' ').strip()
            item['shop_search_url'] = shop_search_url(location, item['shop_query'])
            variants.append(item)
    return variants
