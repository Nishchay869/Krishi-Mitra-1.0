from django.test import SimpleTestCase

from .services import advisories, summarize


def _entry(ts, temp, humidity=60, rain=0, wind=2):
    item = {'dt': ts, 'main': {'temp_min': temp - 2, 'temp_max': temp + 2, 'humidity': humidity, 'pressure': 1010},
            'wind': {'speed': wind}, 'weather': [{'description': 'clear sky'}]}
    if rain:
        item['rain'] = {'3h': rain}
    return item


class WeatherTests(SimpleTestCase):
    def test_summarize_groups_by_day(self):
        day = 86400
        payload = {'list': [_entry(1_760_000_000 + i * day + h * 10800, 30, rain=2) for i in range(3) for h in range(2)]}
        days = summarize(payload)
        self.assertEqual(len(days), 3)
        self.assertEqual(days[0]['rain_mm'], 4.0)

    def _days(self, **kw):
        base = {'temp_min': 22, 'temp_max': 32, 'humidity': 60, 'wind_speed': 2, 'rain_mm': 0}
        return [{**base, **kw} for _ in range(3)]

    def test_heavy_rain_advisory(self):
        notes = advisories(self._days(rain_mm=10))
        self.assertTrue(any('Heavy rain' in t for _, t in notes))

    def test_smart_irrigation_low_moisture_no_rain(self):
        notes = advisories(self._days(), soil_moisture=15)
        self.assertTrue(any('Irrigate in the next 24 hours' in t for _, t in notes))

    def test_heat_and_humidity_alerts(self):
        notes = advisories(self._days(temp_max=40, humidity=90))
        texts = ' '.join(t for _, t in notes)
        self.assertIn('High temperatures', texts)
        self.assertIn('fungal', texts)
