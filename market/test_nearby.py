import json
import math
import time
from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth.models import User
from django.core import signing
from django.test import TestCase, SimpleTestCase, override_settings, Client
from .models import MarketFavourite
from .nearby import coordinates, distance_km, identity, market_points
from .provider import parse_record
from .test_provider import ROW


class DistanceTests(SimpleTestCase):
    def test_distance_and_invalid_points(self):
        self.assertEqual(distance_km((13,77),(13,77)),0)
        self.assertAlmostEqual(distance_km((13,77),(14,77)),111.195,places=2)
        for point in [(math.nan,77),(13,math.inf),(91,77),(13,181),(None,77),('x',77)]:
            with self.assertRaises(ValueError):coordinates(*point)

    def test_published_doddaballapur_point_matches_provider_spelling(self):
        row={'state_name':'Karnataka','district_name':'Bengaluru Rural','name':'Doddaballapur APMC'}
        self.assertEqual(market_points()[identity(row)],(13.2881,77.53178))


@override_settings(DATA_GOV_IN_API_KEY='private-test-key')
@patch('market.local_prices.fetch_local_prices')
class NearbyViewTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user('nearby-farmer')
        profile=self.user.profile;profile.state='Karnataka';profile.district='Bengaluru';profile.save()
        self.client.force_login(self.user)
        session=self.client.session;session['mandi_origin']={'lat':13,'lon':77,'label':'My village, Karnataka','saved_at':time.time()};session.save()
        self.rows=[parse_record({**ROW,'market':name,'modal_price':str(price),'max_price':'3000'},'Karnataka','Tomato') for name,price in [('Near APMC',1000),('Far APMC',2000),('Unknown APMC',1500)]]
        self.points=patch('market.nearby.market_points',return_value={identity(self.rows[0]):(13.1,77),identity(self.rows[1]):(14,77)})
        self.points.start();self.addCleanup(self.points.stop)

    def feed(self,mock):mock.return_value={'rows':self.rows,'truncated':False}

    def test_radius_counts_unique_markets_and_excludes_unmapped(self,mock):
        self.rows.append({**self.rows[0],'variety':'Other'})
        self.feed(mock)
        page=self.client.get('/market/',{'radius':'100'})
        self.assertEqual(len(page.context['cards']),2)
        self.assertEqual(page.context['market_count'],1)
        self.assertEqual([x['count'] for x in page.context['radius_counts']],[1,1,2,2])
        self.assertEqual(page.context['unknown_distance_count'],1)
        self.assertEqual(page.context['nearby_origin'],'My village, Karnataka')
        self.assertTrue(all(r['nearest'] for r in page.context['cards']))

    def test_all_distances_keeps_unknown_prices_and_sorts_high(self,mock):
        self.feed(mock)
        page=self.client.get('/market/',{'radius':'all','sort':'high'})
        self.assertEqual([r['modal_price'] for r in page.context['cards']],[Decimal(2000),Decimal(1500),Decimal(1000)])
        self.assertTrue(page.context['cards'][0]['highest'])
        self.assertEqual(page.context['market_count'],3)

    def test_nearest_sort_unknown_last_and_kg_prices(self,mock):
        self.feed(mock)
        page=self.client.get('/market/',{'sort':'nearest','unit':'kg'})
        self.assertEqual([r['name'] for r in page.context['cards']],['Near APMC','Far APMC','Unknown APMC'])
        self.assertEqual(page.context['cards'][0]['modal_price'],Decimal(10))

    def test_radius_without_location_does_not_hide_all_prices(self,mock):
        self.feed(mock)
        session=self.client.session;session.pop('mandi_origin');session.save()
        page=self.client.get('/market/',{'radius':'100'})
        self.assertEqual(len(page.context['cards']),3)
        self.assertTrue(page.context['distance_unavailable'])
        self.assertFalse(page.context['has_origin'])

    def test_favourites_are_per_user_and_stay_filtered_by_crop(self,mock):
        self.feed(mock)
        other=User.objects.create_user('other-farmer')
        for user,row in [(self.user,self.rows[0]),(other,self.rows[1])]:
            MarketFavourite.objects.create(user=user,identity=identity(row),state=row['state_name'],district=row['district_name'],name=row['name'])
        page=self.client.get('/market/',{'favourites':'1'})
        self.assertEqual([r['name'] for r in page.context['cards']],['Near APMC'])
        self.assertEqual(page.context['all_market_count'],1)
        self.assertTrue(page.context['cards'][0]['favourite'])


class MarketActionTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user('favourite-farmer')
        self.client.force_login(self.user)
        self.row=parse_record(ROW,'Karnataka','Tomato')
        self.token=signing.dumps({k:self.row[k] for k in ('name','state_name','district_name')},salt='market-favourite')

    def test_signed_favourite_add_remove_idempotent(self):
        for _ in range(2):
            page=self.client.post('/market/favourite/',{'token':self.token,'action':'add'},HTTP_ACCEPT='application/json')
            self.assertEqual(page.json(),{'favourite':True})
        self.assertEqual(MarketFavourite.objects.filter(user=self.user).count(),1)
        self.client.post('/market/favourite/',{'token':self.token,'action':'remove'})
        self.assertFalse(MarketFavourite.objects.exists())

    def test_tampering_and_get_rejected(self):
        self.assertEqual(self.client.get('/market/favourite/').status_code,405)
        self.assertEqual(self.client.post('/market/favourite/',{'token':self.token+'x','action':'add'}).status_code,400)
        self.assertFalse(MarketFavourite.objects.exists())

    def test_favourite_redirect_cannot_leave_site(self):
        page=self.client.post('/market/favourite/',{'token':self.token,'action':'add','next':'https://evil.example/'})
        self.assertEqual(page.url,'/market/')

    def test_location_validated_saved_temporarily_and_csrf_protected(self):
        for body in [{'latitude':'NaN','longitude':77},{'latitude':13,'longitude':200},[]]:
            self.assertEqual(self.client.post('/market/location/',json.dumps(body),content_type='application/json').status_code,400)
        page=self.client.post('/market/location/',json.dumps({'latitude':13,'longitude':77,'label':'My village'}),content_type='application/json')
        self.assertEqual(page.status_code,200)
        self.assertEqual(self.client.session['mandi_origin']['label'],'My village')
        self.assertGreater(self.client.session['mandi_origin']['saved_at'],time.time()-5)
        strict=Client(enforce_csrf_checks=True);strict.force_login(self.user)
        self.assertEqual(strict.post('/market/location/','{}',content_type='application/json').status_code,403)

    def test_expired_device_location_is_not_reused(self):
        from .nearby import origin
        from django.test import RequestFactory
        request=RequestFactory().get('/market/');request.user=self.user
        request.session={'mandi_origin':{'lat':13,'lon':77,'label':'Old place','saved_at':time.time()-3601}}
        self.assertEqual(origin(request),(None,''))
        self.assertNotIn('mandi_origin',request.session)
