"""Crop spraying evaluation based on Stull's wet-bulb temperature, Delta-T, Rain, and Wind thresholds."""
import datetime
import math
from typing import Dict, Any


def calculate_wet_bulb(temp: float, rh: float) -> float:
    """Calculates Wet-Bulb Temperature using Stull's formula (2011).

    Formula:
    Tw = T * atan(0.151977 * sqrt(rh + 8.313659))
         + atan(T + rh) - atan(rh - 1.676331)
         + 0.00391838 * (rh ** 1.5) * atan(0.023101 * rh)
         - 4.686035

    :param temp: Dry bulb temperature in °C
    :param rh: Relative humidity in % (0 - 100)
    :return: Wet bulb temperature in °C rounded to 2 decimal places
    """
    rh_safe = max(0.0, min(100.0, float(rh)))
    temp_float = float(temp)
    tw = (
        temp_float * math.atan(0.151977 * math.sqrt(rh_safe + 8.313659))
        + math.atan(temp_float + rh_safe)
        - math.atan(rh_safe - 1.676331)
        + 0.00391838 * (rh_safe ** 1.5) * math.atan(0.023101 * rh_safe)
        - 4.686035
    )
    return round(float(tw), 2)


def evaluate_spray_condition(
    temp: float,
    humidity: float,
    wind_speed_kmh: float,
    rain_within_3h: bool = False,
    rain_mm: float = 0.0,
    is_daylight: bool = True,
    current_hour: int = None,
) -> Dict[str, Any]:
    """Evaluates spraying suitability based on Delta-T, Rain, and Wind thresholds:

    Delta T (°C):
      - 0–2: ⚠️ Caution / Marginal (Humidity too high, slow drying, run-off risk)
      - 2–8: ✔️ Optimal (Ideal spraying conditions)
      - 8–10: ⚠️ Caution / Marginal (Air drying, coarse spray recommended)
      - > 10: ❌ Do not spray (Air too dry, rapid droplet evaporation)

    Rain (mm):
      - No rain: ✔️ Optimal (Dry weather prevents wash-off)
      - < 0.1 mm: ⚠️ Caution / Marginal (Trace rain)
      - > 0.1 mm: ❌ Do not spray (Pesticide will wash off)

    Wind (km/h):
      - < 12 km/h: ✔️ Optimal (Ideal coverage and minimal drift, min 3 km/h to avoid inversion)
      - 12–25 km/h: ⚠️ Caution / Marginal (Moderate wind, lower boom height)
      - > 25 km/h: ❌ Do not spray (Severe drift danger)
    """
    wet_bulb = calculate_wet_bulb(temp, humidity)
    delta_t = round(float(temp - wet_bulb), 2)
    wind_kmh = float(wind_speed_kmh)
    rain_val = float(rain_mm) if rain_mm is not None else 0.0
    if rain_within_3h and rain_val == 0.0:
        rain_val = 0.5  # If forecast marks rain imminent, set rain > 0.1 mm

    # 1. Delta T classification
    if delta_t <= 2.0:
        delta_t_range = "0-2"
        delta_t_status = "marginal"  # ⚠️
        delta_t_reason = "Delta T is 0–2°C: slow drying and run-off risk."
    elif 2.0 < delta_t <= 8.0:
        delta_t_range = "2-8"
        delta_t_status = "optimal"  # ✔️
        delta_t_reason = "Delta T is 2–8°C: ideal droplet retention and steady drying."
    elif 8.0 < delta_t <= 10.0:
        delta_t_range = "8-10"
        delta_t_status = "marginal"  # ⚠️
        delta_t_reason = "Delta T is 8–10°C: use coarse spray nozzles to reduce evaporation."
    else:
        delta_t_range = ">10"
        delta_t_status = "poor"  # ❌
        delta_t_reason = "Air too dry (Delta T > 10°C): droplets evaporate before landing."

    # 2. Rain classification
    if rain_val > 0.1 or rain_within_3h:
        rain_range = ">0.1"
        rain_status = "poor"  # ❌
        rain_reason = "Rain imminent (> 0.1 mm): pesticide will wash off."
    elif rain_val > 0.0:
        rain_range = "<0.1"
        rain_status = "marginal"  # ⚠️
        rain_reason = "Trace rain (< 0.1 mm): monitor skies before spraying."
    else:
        rain_range = "no_rain"
        rain_status = "optimal"  # ✔️
        rain_reason = "Dry weather prevents wash-off."

    # 3. Wind classification (Matching exact photo criteria: < 12, 12–25, > 25)
    if wind_kmh < 12.0:
        wind_range = "<12"
        wind_status = "optimal"  # ✔️
        wind_reason = "Lower wind speeds are ideal for better coverage and less spray drift."
    elif 12.0 <= wind_kmh <= 25.0:
        wind_range = "12-25"
        wind_status = "marginal"  # ⚠️
        wind_reason = "Moderate wind (12–25 km/h): lower spray boom height and monitor drift."
    else:
        wind_range = ">25"
        wind_status = "poor"  # ❌
        wind_reason = "High wind (> 25 km/h): severe spray drift danger."

    # Overall Status determination matching exact Plantix logic:
    # Any poor parameter => DO_NOT_SPRAY (Unfavourable)
    # Any marginal parameter => MARGINAL (Moderate)
    # All optimal => OPTIMAL
    if delta_t_status == "poor":
        status = "DO_NOT_SPRAY"
        reason = delta_t_reason
    elif rain_status == "poor":
        status = "DO_NOT_SPRAY"
        reason = rain_reason
    elif wind_status == "poor":
        status = "DO_NOT_SPRAY"
        reason = wind_reason
    elif delta_t_status == "marginal" or rain_status == "marginal" or wind_status == "marginal":
        status = "MARGINAL"
        if delta_t_status == "marginal":
            reason = delta_t_reason
        elif wind_status == "marginal":
            reason = wind_reason
        else:
            reason = rain_reason
    else:
        status = "OPTIMAL"
        reason = "Optimal spraying conditions: ideal Delta T, dry weather, and calm winds."

    is_night = (is_daylight is False) or (current_hour is not None and (current_hour < 6 or current_hour >= 18))

    return {
        "status": status,
        "delta_t": delta_t,
        "wet_bulb": wet_bulb,
        "temp": temp,
        "humidity": humidity,
        "wind_kmh": round(wind_kmh, 1),
        "rain_mm": round(rain_val, 2),
        "delta_t_range": delta_t_range,
        "delta_t_status": delta_t_status,
        "rain_range": rain_range,
        "rain_status": rain_status,
        "wind_range": wind_range,
        "wind_status": wind_status,
        "reason": reason,
        "is_daylight": not is_night,
    }


def build_hourly_spray_forecast(
    temp_min: float,
    temp_max: float,
    current_temp: float = None,
    now_hour: int = None,
    rain_mm: float = 0.0,
) -> Dict[str, Any]:
    """Generates 16 hourly spray slots and current evaluation using diurnal curves.

    Guarantees synchronization between Home dashboard and Weather page spraying condition.
    """
    if now_hour is None:
        now_hour = datetime.datetime.now().hour

    t_min = float(temp_min)
    t_max = float(temp_max)
    r_val = float(rain_mm or 0.0)

    hourly_spray_slots = []
    for i in range(16):
        h = (now_hour + i) % 24
        label = 'Now' if i == 0 else datetime.time(h, 0).strftime('%-I %p').lower()

        # Realistic diurnal curve matching meteorological dawn peaks and afternoon evaporation
        if h == 5:
            t = t_min
            rh = 90.0
            w = 5.0
            r_mm = 0.0
        elif 0 <= h < 6:
            t = t_min + (h / 6.0) * 1.5
            rh = 70.0 + (h / 6.0) * 10.0
            w = 5.0
            r_mm = 0.0
        elif 6 <= h < 14:
            ratio = (h - 6.0) / 8.0
            t = (t_min + 1.5) + ratio * (t_max - t_min - 1.5)
            rh = 76.0 - ratio * 28.0
            w = 6.0 + ratio * 3.5
            r_mm = 0.0
        elif 14 <= h < 19:
            ratio = (h - 14.0) / 5.0
            t = t_max - ratio * 4.0
            rh = 48.0 + ratio * 16.0
            w = 9.0 - ratio * 2.5
            r_mm = 0.0
        else:
            ratio = (h - 19.0) / 5.0
            t = (t_max - 4.0) - ratio * 6.0
            rh = 64.0 + ratio * 6.0
            w = 5.5
            r_mm = 0.0

        # Slot 0 reflects actual current rainfall if rain is falling (> 0.1 mm)
        slot_rain = r_val if (i == 0 and r_val > 0.1) else r_mm
        slot_rain_3h = slot_rain > 0.1

        eval_slot = evaluate_spray_condition(
            t, rh, w, rain_within_3h=slot_rain_3h, rain_mm=slot_rain, is_daylight=True, current_hour=h
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
            'delta_t_range': eval_slot['delta_t_range'],
            'rain_range': eval_slot['rain_range'],
            'wind_range': eval_slot['wind_range'],
            'wind': round(w, 1),
            'rain': round(slot_rain, 1),
            'reason': eval_slot['reason'],
        })

    current_slot = hourly_spray_slots[0]
    current_slot_status = current_slot['status']

    if current_slot_status == 'optimal':
        spray_card_title = 'Optimal spraying conditions'
    elif current_slot_status == 'moderate':
        spray_card_title = 'Moderate spraying conditions'
    else:
        spray_card_title = 'Unfavourable spraying conditions'

    curr_rh = current_slot['humidity']
    curr_wind = current_slot['wind']
    curr_temp = round(current_temp) if current_temp is not None else current_slot['temp']

    eval_now = evaluate_spray_condition(
        curr_temp, curr_rh, curr_wind,
        rain_within_3h=(r_val > 0.1),
        rain_mm=r_val,
        is_daylight=True,
        current_hour=now_hour
    )

    delta_t = eval_now['delta_t']
    now_status = eval_now['status']

    if now_status == 'OPTIMAL':
        status_label = 'Optimal'
        badge_class = 'is-optimal'
        badge_icon = 'check'
        time_text = f"ΔT {delta_t}°C · Ideal window"
    elif now_status == 'MARGINAL':
        status_label = 'Moderate'
        badge_class = 'is-marginal'
        badge_icon = 'alert'
        time_text = f"ΔT {delta_t}°C · Monitor drift"
    else:
        status_label = 'Avoid'
        badge_class = 'is-avoid'
        badge_icon = 'x'
        if r_val > 0.1 or eval_now.get('rain_status') == 'poor':
            time_text = 'Rain imminent'
        elif eval_now.get('wind_status') == 'poor':
            time_text = 'High wind drift'
        elif curr_temp > 35:
            time_text = 'High temperature'
        else:
            time_text = f"ΔT {delta_t}°C · Do not spray"

    weather_data = {
        'temp': curr_temp,
        'temp_str': f"{curr_temp} °C",
        'humidity': round(curr_rh),
        'wind_kmh': round(curr_wind, 1),
        'delta_t': delta_t,
        'rain_mm': round(r_val, 2),
        'rain_within_3h': r_val > 0.1,
        'is_daylight': True,
        'status': now_status,
        'status_label': status_label,
        'badge_class': badge_class,
        'badge_icon': badge_icon,
        'time_text': time_text,
        'reason': eval_now['reason'],
        'delta_t_range': eval_now.get('delta_t_range', '2-8'),
        'delta_t_status': eval_now.get('delta_t_status', 'optimal'),
        'rain_range': eval_now.get('rain_range', 'no_rain'),
        'rain_status': eval_now.get('rain_status', 'optimal'),
        'wind_range': eval_now.get('wind_range', '<12'),
        'wind_status': eval_now.get('wind_status', 'optimal'),
    }

    return {
        'hourly_spray_slots': hourly_spray_slots,
        'current_slot_status': current_slot_status,
        'spray_card_title': spray_card_title,
        'eval_now': eval_now,
        'weather_data': weather_data,
    }
