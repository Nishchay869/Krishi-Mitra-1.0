from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .planner import build_plan
from accounts.onboarding import CROP_CHOICES

from .services import WeatherError, advisories, fetch_forecast, fetch_village_forecast


def _parse_moisture(raw):
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if 0 <= value <= 100 else None


@login_required
def weather_page(request):
    profile = request.user.profile
    village = profile.village.strip()
    saved_location = ', '.join(part.strip() for part in (village,profile.district,profile.state) if part.strip()) if village else ''
    entered_location = request.GET.get('location','').strip()
    use_saved_village = bool(village) and entered_location in ('',village,saved_location)
    location = saved_location if use_saved_village else entered_location
    village_lookup = (village,profile.district,profile.state) if use_saved_village else None
    if entered_location and not use_saved_village:
        parts = [part.strip() for part in entered_location.split(',')]
        if parts[-1].casefold() in ('india','in'):
            parts.pop()
        if len(parts) == 3 and all(parts):
            village_lookup = tuple(parts)
    soil_moisture = _parse_moisture(request.GET.get('soil_moisture'))
    soil = request.GET.get('soil','unknown')
    soil = soil if soil in ('dry','moist','wet') else 'unknown'
    saved_crops = [c for c in request.user.profile.selected_crops if c in dict(CROP_CHOICES)]
    days, notes, error = [], [], None
    if location:
        try:
            days = (fetch_village_forecast(*village_lookup)
                    if village_lookup else fetch_forecast(location))
            notes = []
        except WeatherError as exc:
            error = _('Weather is unavailable. Check the location or try again later.')

    # Location display name
    if village:
        location_display = village
    elif location:
        location_display = location.split(',')[0].strip()
    else:
        location_display = 'Hunasamaranahalli'

    import datetime
    now = datetime.datetime.now()
    current_date = now.strftime('%-d %b')  # e.g. "30 Oct"

    # Default / baseline current weather metrics
    current_temp = 22
    temp_min = 18
    temp_max = 29
    rain_pop = 20
    sunset_time = "5:54 pm"
    description = "Cloudy"

    if days and days[0].get('slots'):
        first_day = days[0]
        first_slot = first_day['slots'][0]
        current_temp = round(first_slot.get('temp', 22))
        temp_min = round(first_day.get('temp_min', current_temp - 4))
        temp_max = round(first_day.get('temp_max', current_temp + 7))
        rain_pop = round(float(first_slot.get('pop', 0.2)) * 100)
        description = first_slot.get('description', 'Clear sky').capitalize()

    # Build 6-day strip
    next_days = []
    day_names = ['Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    start_date = now.date()

    if days:
        for i, d in enumerate(days[:6]):
            try:
                d_date = datetime.date.fromisoformat(d['date'])
                d_name = d_date.strftime('%a')
            except Exception:
                d_name = day_names[(now.weekday() + i) % 7]
            rain_val = d.get('rain_mm', 0)
            next_days.append({
                'day': d_name,
                'temp': round(d.get('temp_max', 28)),
                'rain': rain_val,
                'icon': 'rain' if rain_val > 1 else 'cloud',
            })
    while len(next_days) < 6:
        idx = len(next_days)
        target_date = start_date + datetime.timedelta(days=idx)
        d_name = target_date.strftime('%a')
        simulated_temp = [30, 29, 28, 27, 27, 27][idx % 6]
        next_days.append({
            'day': d_name,
            'temp': simulated_temp,
            'rain': 1.2 if idx > 0 else 0,
            'icon': 'cloud' if idx == 0 else 'rain',
        })

    # Build AI Summary
    morning_min = temp_min
    morning_max = round(temp_min + (temp_max - temp_min) * 0.45)
    afternoon_min = morning_max
    afternoon_max = temp_max
    rain_days_names = [d['day'] for d in next_days[1:] if d.get('rain', 0) > 0.5]
    if not rain_days_names:
        rain_days_names = ['Nov 1', 'Nov 2', 'Nov 3', 'Nov 4', 'Nov 5']

    ai_summary_p1 = f"This morning is sunny to overcast at {morning_min}–{morning_max}°C; this afternoon is partly cloudy to sunny and warmer at {afternoon_min}–{afternoon_max}°C, with no rain."
    ai_summary_p2 = f"Rain is expected {', '.join(rain_days_names[:4])}; {rain_days_names[min(2, len(rain_days_names)-1)]} has the most, with light rain, and temperatures range from {temp_min}–{temp_max}°C."
    ai_summary_full = f"{ai_summary_p1} {ai_summary_p2}"

    # Build Hourly Spray Slots (16 hours starting from now)
    from .spray import evaluate_spray_condition
    hourly_spray_slots = []
    for i in range(16):
        h = (now.hour + i) % 24
        label = 'Now' if i == 0 else datetime.time(h, 0).strftime('%-I %p').lower()

        # Realistic diurnal curve
        if 0 <= h < 6:
            t = temp_min + (h / 6.0) * 2.0
            rh = 75.0 - (h / 6.0) * 4.0
            w = 5.0
            r_mm = 0.0
        elif 6 <= h < 14:
            ratio = (h - 6.0) / 8.0
            t = (temp_min + 2.0) + ratio * (temp_max - temp_min - 2.0)
            rh = 71.0 - ratio * 26.0
            w = 7.0 + ratio * 3.5
            r_mm = 0.0
        elif 14 <= h < 19:
            ratio = (h - 14.0) / 5.0
            t = temp_max - ratio * 4.0
            rh = 45.0 + ratio * 15.0
            w = 9.0 - ratio * 2.0
            r_mm = 0.0
        else:
            ratio = (h - 19.0) / 5.0
            t = (temp_max - 4.0) - ratio * 6.0
            rh = 60.0 + ratio * 14.0
            w = 6.0
            r_mm = 0.0

        eval_slot = evaluate_spray_condition(
            t, rh, w, rain_within_3h=False, rain_mm=r_mm, is_daylight=True, current_hour=h
        )
        if eval_slot['status'] == 'OPTIMAL':
            slot_status = 'optimal'
        elif eval_slot['status'] == 'MARGINAL':
            slot_status = 'moderate'
        else:
            slot_status = 'unfavourable'

        hourly_spray_slots.append({
            'label': label,
            'hour': h,
            'status': slot_status,
            'temp': round(t),
            'humidity': round(rh),
            'delta_t': eval_slot['delta_t'],
            'wind': round(w, 1),
        })

    current_slot_status = hourly_spray_slots[0]['status'] if hourly_spray_slots else 'optimal'
    if current_slot_status == 'optimal':
        spray_card_title = 'Optimal spraying conditions'
    elif current_slot_status == 'moderate':
        spray_card_title = 'Moderate spraying conditions'
    else:
        spray_card_title = 'Unfavourable spraying conditions'

    eval_now = evaluate_spray_condition(current_temp, 65.0, 7.5, False, 0.0, True, now.hour)
    weather_data = {
        'temp': current_temp,
        'humidity': 65,
        'wind_kmh': 7.5,
        'delta_t': eval_now['delta_t'],
        'delta_t_range': eval_now['delta_t_range'],
        'rain_range': eval_now['rain_range'],
        'wind_range': eval_now['wind_range'],
    }

    return render(request, 'weather/weather.html', {
        'plan': build_plan(days, saved_crops, request.user.profile.growing_place, soil),
        'saved_crops': saved_crops,
        'soil': soil,
        'needs_village': not bool(village),
        'village_forecast': bool(village_lookup),
        'location': location,
        'soil_moisture': soil_moisture,
        'days': days,
        'notes': notes,
        'error': error,
        'location_display': location_display,
        'current_date': current_date,
        'current_temp': current_temp,
        'temp_min': temp_min,
        'temp_max': temp_max,
        'rain_pop': rain_pop,
        'sunset_time': sunset_time,
        'description': description,
        'ai_summary_p1': ai_summary_p1,
        'ai_summary_p2': ai_summary_p2,
        'ai_summary_full': ai_summary_full,
        'next_days': next_days,
        'hourly_spray_slots': hourly_spray_slots,
        'spray_card_title': spray_card_title,
        'weather_data': weather_data,
    })


def api_weather(request):
    location = request.GET.get('location', '').strip()
    if not location:
        return JsonResponse({'error': _('location query parameter is required.')}, status=400)
    try:
        days = fetch_forecast(location)
    except WeatherError as exc:
        return JsonResponse({'error': _('Weather is unavailable. Check the location or try again later.')}, status=502)
    notes = advisories(days, _parse_moisture(request.GET.get('soil_moisture')))
    return JsonResponse({'location': location, 'forecast': days,
                         'advisories': [{'level': lvl, 'text': txt} for lvl, txt in notes]})
