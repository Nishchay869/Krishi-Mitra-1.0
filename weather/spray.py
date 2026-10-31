"""Crop spraying evaluation based on Stull's wet-bulb temperature, Delta-T, Rain, and Wind thresholds."""
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

    # 3. Wind classification
    if wind_kmh < 3.0:
        wind_range = "<12"
        wind_status = "poor"  # ❌ Inversion risk
        wind_reason = "Inversion risk: zero/calm wind causes dangerous droplet suspension."
    elif 3.0 <= wind_kmh < 12.0:
        wind_range = "<12"
        wind_status = "optimal"  # ✔️
        wind_reason = "Lower wind speeds (< 12 km/h) are ideal for better coverage and less drift."
    elif 12.0 <= wind_kmh <= 25.0:
        wind_range = "12-25"
        wind_status = "marginal"  # ⚠️
        wind_reason = "Moderate wind (12–25 km/h): lower spray boom height and monitor drift."
    else:
        wind_range = ">25"
        wind_status = "poor"  # ❌
        wind_reason = "High wind (> 25 km/h): severe spray drift danger."

    # Night-time check
    is_night = (is_daylight is False) or (current_hour is not None and (current_hour < 6 or current_hour >= 18))

    # Overall Status determination
    if is_night:
        status = "DO_NOT_SPRAY"
        reason = "Night-time: Inversion risk and dew. Spraying is unsafe at night; wait until daylight (06:00–18:00)."
    elif temp > 35.0:
        status = "DO_NOT_SPRAY"
        reason = "High temperature (> 35°C): risk of leaf phytotoxicity and rapid volatilization."
    elif delta_t_status == "poor":
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
        # Pick the most prominent reason
        if delta_t_status == "marginal":
            reason = delta_t_reason
        elif wind_status == "marginal":
            reason = wind_reason
        else:
            reason = rain_reason
    else:
        status = "OPTIMAL"
        reason = "Ideal spraying window: optimal droplet retention, low drift, and steady drying."

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
