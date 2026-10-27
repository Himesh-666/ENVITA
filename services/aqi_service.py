"""
OpenAQ v3 integration.
Fetches latest AQI, PM2.5, PM10 readings near a lat/lon coordinate.
"""
import requests
from config import Config

OPENAQ_BASE = "https://api.openaq.org/v3"

print("OpenAQ Key:", Config.OPENAQ_API_KEY)
print("URL:", OPENAQ_BASE)

def _headers():
    key = Config.OPENAQ_API_KEY
    if key:
        return {"X-API-Key": key}
    return {}


def get_aqi_data(lat: float, lon: float, radius_km: int = 25):
    """
    Query OpenAQ for the nearest station within radius_km and return
    the most recent PM2.5, PM10 readings plus a computed AQI.
    """
    try:
        resp = requests.get(
            f"{OPENAQ_BASE}/locations",
            params={
                "coordinates": f"{lat},{lon}",
                "radius": radius_km * 1000,   # metres
                "limit": 5,
                "order_by": "distance",
            },
            headers=_headers(),
            timeout=10,
        )
        resp.raise_for_status()
        locations = resp.json().get("results", [])

        if not locations:
            return _fallback()

        # Try each nearby location until we get usable readings
        for location in locations:
            loc_id = location["id"]
            readings = _get_latest_readings(loc_id)
            if readings:
                return readings

        return _fallback()

    except Exception as exc:
        print(f"[AQI] OpenAQ error: {exc}")
        return _fallback()


def _get_latest_readings(location_id: int):
    """Fetch latest sensor readings for a location."""
    try:
        resp = requests.get(
            f"{OPENAQ_BASE}/locations/{location_id}/latest",
            headers=_headers(),
            timeout=10,
        )
        if resp.status_code != 200:
            return None

        results = resp.json().get("results", [])
        pm25 = pm10 = None

        for r in results:
            param = r.get("parameter", {})
            name  = param.get("name", "") if isinstance(param, dict) else str(param)
            value = r.get("value")

            if value is None:
                continue
            if "pm25" in name.lower() or "pm2.5" in name.lower():
                pm25 = round(float(value), 1)
            elif "pm10" in name.lower():
                pm10 = round(float(value), 1)

        if pm25 is None and pm10 is None:
            return None

        aqi = _compute_aqi(pm25, pm10)
        return {
            "aqi":  aqi,
            "pm25": pm25 if pm25 is not None else 0.0,
            "pm10": pm10 if pm10 is not None else 0.0,
            "source": "OpenAQ",
        }
    except Exception:
        return None


def _compute_aqi(pm25, pm10):
    """
    Simplified US EPA AQI calculation.
    Uses PM2.5 as primary, PM10 as fallback.
    """
    if pm25 is not None:
        return _pm25_to_aqi(pm25)
    if pm10 is not None:
        return _pm10_to_aqi(pm10)
    return 0


def _pm25_to_aqi(pm25):
    """US EPA breakpoints for PM2.5 (µg/m³) → AQI."""
    breakpoints = [
        (0.0,   12.0,   0,   50),
        (12.1,  35.4,  51,  100),
        (35.5,  55.4, 101,  150),
        (55.5, 150.4, 151,  200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]
    return _interpolate_aqi(pm25, breakpoints)


def _pm10_to_aqi(pm10):
    """US EPA breakpoints for PM10 (µg/m³) → AQI."""
    breakpoints = [
        (0,   54,   0,  50),
        (55,  154,  51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 504, 301, 400),
        (505, 604, 401, 500),
    ]
    return _interpolate_aqi(pm10, breakpoints)


def _interpolate_aqi(value, breakpoints):
    for c_lo, c_hi, i_lo, i_hi in breakpoints:
        if c_lo <= value <= c_hi:
            aqi = (i_hi - i_lo) / (c_hi - c_lo) * (value - c_lo) + i_lo
            return round(aqi)
    return 500 if value > breakpoints[-1][1] else 0


def _fallback():
    """Return a safe default when API is unavailable."""
    return {
        "aqi":    0,
        "pm25":   0.0,
        "pm10":   0.0,
        "source": "unavailable",
    }


def get_aqi_label(aqi: float):
    if aqi <= 50:   return ("Good",            "success")
    if aqi <= 100:  return ("Moderate",         "warning")
    if aqi <= 150:  return ("Unhealthy for Sensitive Groups", "orange")
    if aqi <= 200:  return ("Unhealthy",        "danger")
    if aqi <= 300:  return ("Very Unhealthy",   "purple")
    return              ("Hazardous",           "dark")
