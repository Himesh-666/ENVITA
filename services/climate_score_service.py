"""
Orchestration service: fetches all environmental data and computes the
climate health score for a given location and user profile.
"""
from services.weather_service import get_weather_for_city
from services.aqi_service      import get_aqi_data, get_aqi_label
from models.risk_engine        import calculate_climate_score, get_risk_color, get_risk_icon


def get_full_climate_assessment(city: str, user_profile: dict) -> dict:
    """
    Full pipeline:
      1. Fetch weather data (OpenWeatherMap)
      2. Fetch AQI data (OpenAQ)
      3. Compute climate health score (rule engine)
      4. Return structured result dict

    Raises ValueError if the city is not found.
    """
    # 1. Weather
    weather = get_weather_for_city(city)

    # 2. AQI
    aqi_data = get_aqi_data(weather["lat"], weather["lon"])

    # 3. Score
    sensitivities = user_profile.get("sensitivities", [])
    result = calculate_climate_score(
        aqi          = aqi_data.get("aqi", 0),
        temperature  = weather.get("temperature", 20),
        uv_index     = weather.get("uv_index", 0),
        age_group    = user_profile.get("age_group", "Adult"),
        occupation   = user_profile.get("occupation", "Other"),
        sensitivities = sensitivities,
    )

    # 4. AQI label
    aqi_label, aqi_badge = get_aqi_label(aqi_data.get("aqi", 0))

    # 5. Early-warning flags
    warnings = _check_warnings(weather, aqi_data)

    return {
        "weather":       weather,
        "aqi_data":      aqi_data,
        "aqi_label":     aqi_label,
        "aqi_badge":     aqi_badge,
        "score":         result["score"],
        "risk_category": result["risk_category"],
        "breakdown":     result["breakdown"],
        "risk_color":    get_risk_color(result["risk_category"]),
        "risk_icon":     get_risk_icon(result["risk_category"]),
        "warnings":      warnings,
        "location":      weather.get("display_name", city),
    }


def _check_warnings(weather: dict, aqi_data: dict) -> list:
    """Return a list of warning message strings for the early-warning banner."""
    warnings = []

    aqi = aqi_data.get("aqi", 0)
    temp = weather.get("temperature", 20)
    uv   = weather.get("uv_index", 0)

    if aqi > 150:
        warnings.append(
            f"⚠️ Air Quality Alert: AQI is {aqi} — considered Unhealthy. "
            "Limit outdoor exposure and keep windows closed."
        )
    if temp > 38:
        warnings.append(
            f"🌡️ Extreme Heat Alert: Temperature is {temp}°C. "
            "Stay in cool environments, hydrate frequently, and avoid outdoor exertion."
        )
    if uv > 8:
        warnings.append(
            f"☀️ High UV Alert: UV Index is {uv}. "
            "Wear SPF 50+ sunscreen, sunglasses, and protective clothing if outdoors."
        )

    return warnings
