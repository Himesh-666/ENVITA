"""
Google Gemini integration for AI-powered climate health recommendations.
Uses google-generativeai SDK.
"""
import re
import google.generativeai as genai
from config import Config


def _configure():
    genai.configure(api_key=Config.GEMINI_API_KEY)


def _load_prompt_template():
    try:
        with open("prompts/climate_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return _default_prompt_template()


def _default_prompt_template():
    return """You are ENVITA's Climate Health Assistant — an expert in environmental health awareness.

STRICT RULES (you must follow these without exception):
- DO NOT diagnose any disease or medical condition.
- DO NOT predict whether the user will get sick.
- DO NOT recommend any medicines, drugs, or medical treatments.
- DO NOT replace professional medical advice.
- ALWAYS frame responses as awareness and preparedness guidance.
- Keep language simple, warm, and empowering.

CURRENT ENVIRONMENTAL CONDITIONS:
- Location: {location}
- Temperature: {temperature}°C (Feels like {feels_like}°C)
- Humidity: {humidity}%
- UV Index: {uv_index}
- Wind Speed: {wind_speed} m/s
- Weather: {description}
- AQI: {aqi} ({aqi_label})
- PM2.5: {pm25} µg/m³
- PM10: {pm10} µg/m³

USER PROFILE:
- Age Group: {age_group}
- Occupation: {occupation}
- Lifestyle: {lifestyle}
- Health Sensitivities: {sensitivities}

CLIMATE HEALTH SCORE: {score}/100 — {risk_category}

Please provide a personalized climate health report structured EXACTLY as follows (use these exact section headers):

## 🌍 Climate Risk Explanation
Explain in 2-3 sentences what today's environmental conditions mean for this specific user's daily life. Reference their occupation and lifestyle.

## ⚠️ Personalized Precautions
List 4-5 specific, actionable precautions this user should take TODAY based on their profile and the environmental data. Use bullet points.

## ✅ Personalized Recommendations
List 4-5 positive, constructive recommendations for maintaining wellbeing today. Use bullet points.

## 💡 Daily Safety Tips
List 3-4 quick, practical tips this user can act on immediately. Use bullet points.

## 📊 Environmental Insights
Briefly explain 2-3 key environmental metrics (AQI, UV, Temperature) in plain language and what they mean for someone with this user's profile.

Keep the total response under 500 words. Be specific, practical, and encouraging.
"""


def generate_recommendations(
    location, weather, aqi_data, user_profile, score, risk_category
):
    """
    Call Gemini and return the AI-generated climate health report as a string.
    Falls back to a static response if Gemini is unavailable.
    """
    if not Config.GEMINI_API_KEY:
        return _fallback_response(score, risk_category, user_profile)

    try:
        _configure()
        template = _load_prompt_template()

        sensitivities = user_profile.get("sensitivities", [])
        if not sensitivities or sensitivities == ["None"]:
            sens_text = "No specific sensitivities reported"
        else:
            sens_text = ", ".join(sensitivities)

        from services.aqi_service import get_aqi_label
        aqi_label, _ = get_aqi_label(aqi_data.get("aqi", 0))

        prompt = template.format(
            location      = location or "your location",
            temperature   = weather.get("temperature", "N/A"),
            feels_like    = weather.get("feels_like", "N/A"),
            humidity      = weather.get("humidity", "N/A"),
            uv_index      = weather.get("uv_index", "N/A"),
            wind_speed    = weather.get("wind_speed", "N/A"),
            description   = weather.get("description", "N/A"),
            aqi           = aqi_data.get("aqi", 0),
            aqi_label     = aqi_label,
            pm25          = aqi_data.get("pm25", 0),
            pm10          = aqi_data.get("pm10", 0),
            age_group     = user_profile.get("age_group", "Adult"),
            occupation    = user_profile.get("occupation", "Other"),
            lifestyle     = user_profile.get("lifestyle", "Mixed"),
            sensitivities = sens_text,
            score         = score,
            risk_category = risk_category,
        )

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024,
            ),
        )
        return response.text

    except Exception as exc:
        print(f"[Gemini] Error: {exc}")
        return _fallback_response(score, risk_category, user_profile)


def _fallback_response(score, risk_category, user_profile):
    """Static fallback when Gemini API is unavailable or key is missing."""
    name = user_profile.get("name", "there")
    sens = user_profile.get("sensitivities", [])

    precautions = [
        "Stay hydrated — drink water regularly throughout the day.",
        "Check local air quality updates before outdoor activities.",
        "Limit prolonged outdoor exposure during peak UV hours (10am–4pm).",
        "Keep windows closed if air quality is poor in your area.",
    ]

    if "Asthma" in sens or "Respiratory Issues" in sens:
        precautions.append("Keep any prescribed respiratory aids accessible as a precaution.")

    if "Heat Sensitive" in sens:
        precautions.append("Seek cool, shaded environments and avoid strenuous outdoor activity.")

    precaution_list = "\n".join(f"- {p}" for p in precautions)

    return f"""## 🌍 Climate Risk Explanation
Based on today's environmental conditions, your Climate Health Score is **{score}/100** — classified as **{risk_category}**. Your individual profile (age group, occupation, and lifestyle) has been factored into this assessment.

## ⚠️ Personalized Precautions
{precaution_list}

## ✅ Personalized Recommendations
- Start your morning with light indoor exercise if outdoor conditions are poor.
- Eat foods rich in antioxidants (fruits, vegetables) to support respiratory health awareness.
- Monitor local weather and AQI updates through reliable sources.
- Plan outdoor activities in the early morning or evening when conditions are typically better.

## 💡 Daily Safety Tips
- Check the ENVITA dashboard before heading outdoors.
- Wear sunscreen (SPF 30+) on sunny days, especially between 10am and 4pm.
- If you feel discomfort due to air quality, move to a well-ventilated indoor space.

## 📊 Environmental Insights
**Air Quality (AQI):** Measures the concentration of pollutants in the air. Higher values indicate more pollution, which can affect breathing comfort.
**UV Index:** Measures the strength of ultraviolet radiation from the sun. Values above 6 require sun protection measures.
**Temperature:** Extreme temperatures (very hot or very cold) can stress the body's ability to regulate itself, especially during physical activity.

*Note: This is a general awareness response. Configure your Gemini API key for personalized AI-powered recommendations.*
"""


def parse_ai_sections(ai_text: str) -> dict:
    """
    Parse the structured AI response into named sections for the template.
    Returns a dict: {section_name: content}
    """
    sections = {
        "risk_explanation":   "",
        "precautions":        "",
        "recommendations":    "",
        "safety_tips":        "",
        "insights":           "",
        "raw":                ai_text,
    }

    patterns = {
        "risk_explanation": r"##\s*🌍\s*Climate Risk Explanation\s*(.*?)(?=##|\Z)",
        "precautions":      r"##\s*⚠️\s*Personalized Precautions\s*(.*?)(?=##|\Z)",
        "recommendations":  r"##\s*✅\s*Personalized Recommendations\s*(.*?)(?=##|\Z)",
        "safety_tips":      r"##\s*💡\s*Daily Safety Tips\s*(.*?)(?=##|\Z)",
        "insights":         r"##\s*📊\s*Environmental Insights\s*(.*?)(?=##|\Z)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, ai_text, re.DOTALL | re.IGNORECASE)
        if match:
            sections[key] = match.group(1).strip()

    return sections
