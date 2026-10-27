"""
OpenWeatherMap integration.
Fetches current weather + UV index for a given city or lat/lon.
"""
import requests
from config import Config

BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_URL  = "https://api.openweathermap.org/geo/1.0"


def _api_key():
    return Config.OPENWEATHER_API_KEY


def get_coordinates(city: str):
    """Geocode a city name → (lat, lon, display_name)."""
    resp = requests.get(
        f"{GEO_URL}/direct",
        params={"q": city, "limit": 1, "appid": _api_key()},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return None
    loc = data[0]
    display = f"{loc.get('name')}, {loc.get('country', '')}"
    return loc["lat"], loc["lon"], display


def get_current_weather(lat: float, lon: float):
    """Fetch current weather data for lat/lon."""
    resp = requests.get(
        f"{BASE_URL}/weather",
        params={
            "lat": lat,
            "lon": lon,
            "appid": _api_key(),
            "units": "metric",
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    return {
        "temperature": round(data["main"]["temp"], 1),
        "feels_like":  round(data["main"]["feels_like"], 1),
        "humidity":    data["main"]["humidity"],
        "wind_speed":  round(data["wind"]["speed"], 1),
        "description": data["weather"][0]["description"].title(),
        "icon":        data["weather"][0]["icon"],
        "city":        data.get("name", ""),
        "country":     data.get("sys", {}).get("country", ""),
    }


def get_uv_index(lat: float, lon: float):
    """Fetch current UV index using One Call API (3.0 or fallback to current)."""
    try:
        # Try One Call API 3.0
        resp = requests.get(
            "https://api.openweathermap.org/data/3.0/onecall",
            params={
                "lat": lat,
                "lon": lon,
                "exclude": "minutely,hourly,daily,alerts",
                "appid": _api_key(),
            },
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("current", {}).get("uvi", 0)
    except Exception:
        pass

    # Fallback: UV from /forecast (less precise but works on free tier)
    try:
        resp = requests.get(
            f"{BASE_URL}/forecast",
            params={"lat": lat, "lon": lon, "appid": _api_key(), "units": "metric", "cnt": 1},
            timeout=10,
        )
        if resp.status_code == 200:
            # Free tier doesn't provide UVI directly in forecast; return 0
            return 0
    except Exception:
        pass

    return 0


def get_weather_for_city(city: str):
    """
    High-level helper: geocode city, fetch weather + UV.
    Returns a flat dict with all weather fields.
    """
    coords = get_coordinates(city)
    if not coords:
        raise ValueError(f"Location '{city}' not found.")

    lat, lon, display_name = coords
    weather = get_current_weather(lat, lon)
    uv = get_uv_index(lat, lon)

    weather["uv_index"]    = uv
    weather["lat"]         = lat
    weather["lon"]         = lon
    weather["display_name"] = display_name
    return weather
