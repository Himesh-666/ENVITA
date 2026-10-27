"""
Rule-based Climate Risk Scoring Engine
Score range: 0 – 100
  0–30   → Low Risk
 31–60   → Moderate Risk
 61–80   → High Risk
 81–100  → Very High Risk
"""


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

AQI_THRESHOLDS = [
    (50,  0),
    (100, 15),
    (150, 30),
    (200, 50),
    (300, 70),
    (float("inf"), 90),
]

TEMP_THRESHOLDS = [
    (10,  10),   # Very cold → some risk
    (20,   0),   # Comfortable
    (30,   5),
    (35,  15),
    (38,  30),
    (float("inf"), 50),  # Extreme heat
]

UV_THRESHOLDS = [
    (3,   0),
    (6,   10),
    (8,   20),
    (11,  35),
    (float("inf"), 50),
]

# Multipliers applied on top of base score
AGE_MULTIPLIERS = {
    "Child":   1.25,
    "Teen":    1.05,
    "Adult":   1.00,
    "Elderly": 1.30,
}

OCCUPATION_MULTIPLIERS = {
    "Student":        1.00,
    "Office Worker":  1.00,
    "Outdoor Worker": 1.20,
    "Athlete":        1.15,
    "Other":          1.00,
}

SENSITIVITY_BONUS = {
    "Asthma":             15,
    "Respiratory Issues": 12,
    "Heat Sensitive":     10,
    "None":                0,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lookup(value, thresholds):
    """Return the score for a value based on threshold ladder."""
    for limit, score in thresholds:
        if value <= limit:
            return score
    return thresholds[-1][1]


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

def calculate_climate_score(aqi, temperature, uv_index, age_group, occupation, sensitivities):
    """
    Compute a weighted climate health score.

    Returns a dict with:
        score         – float, 0-100
        risk_category – str
        breakdown     – dict of component contributions
    """
    aqi = float(aqi or 0)
    temperature = float(temperature or 20)
    uv_index = float(uv_index or 0)

    # Base scores from environmental data (weighted sum)
    aqi_score  = _lookup(aqi, AQI_THRESHOLDS)   * 0.45   # AQI carries most weight
    temp_score = _lookup(temperature, TEMP_THRESHOLDS) * 0.30
    uv_score   = _lookup(uv_index, UV_THRESHOLDS) * 0.25

    base = aqi_score + temp_score + uv_score  # 0-100 weighted

    # User-profile multiplier
    age_mult  = AGE_MULTIPLIERS.get(age_group, 1.0)
    occ_mult  = OCCUPATION_MULTIPLIERS.get(occupation, 1.0)
    combined_mult = (age_mult + occ_mult) / 2.0  # average so we don't over-amplify

    adjusted = base * combined_mult

    # Sensitivity bonus (additive)
    sensitivity_bonus = sum(SENSITIVITY_BONUS.get(s, 0) for s in (sensitivities or []))

    raw_score = adjusted + sensitivity_bonus
    score = round(min(max(raw_score, 0), 100), 1)

    risk_category = _get_risk_category(score)

    return {
        "score": score,
        "risk_category": risk_category,
        "breakdown": {
            "aqi_component":   round(aqi_score, 1),
            "temp_component":  round(temp_score, 1),
            "uv_component":    round(uv_score, 1),
            "base_score":      round(base, 1),
            "profile_multiplier": round(combined_mult, 2),
            "sensitivity_bonus": sensitivity_bonus,
        },
    }


def _get_risk_category(score):
    if score <= 30:
        return "Low Risk"
    elif score <= 60:
        return "Moderate Risk"
    elif score <= 80:
        return "High Risk"
    else:
        return "Very High Risk"


def get_risk_color(risk_category):
    colors = {
        "Low Risk":       "#0B6B43",
        "Moderate Risk":  "#F0A500",
        "High Risk":      "#E05C00",
        "Very High Risk": "#C0392B",
    }
    return colors.get(risk_category, "#0B6B43")


def get_risk_icon(risk_category):
    icons = {
        "Low Risk":       "fa-leaf",
        "Moderate Risk":  "fa-exclamation-circle",
        "High Risk":      "fa-exclamation-triangle",
        "Very High Risk": "fa-radiation",
    }
    return icons.get(risk_category, "fa-leaf")
