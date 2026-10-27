"""Input validation utilities for ENVITA forms and API requests."""

VALID_AGE_GROUPS = {"Child", "Teen", "Adult", "Elderly"}
VALID_OCCUPATIONS = {"Student", "Office Worker", "Outdoor Worker", "Athlete", "Other"}
VALID_LIFESTYLES = {"Mostly Indoor", "Mixed", "Mostly Outdoor"}
VALID_SENSITIVITIES = {"Asthma", "Respiratory Issues", "Heat Sensitive", "None"}


def validate_profile(data: dict) -> tuple[bool, list[str]]:
    """
    Validate user profile form data.
    Returns (is_valid: bool, errors: list[str])
    """
    errors = []

    name = (data.get("name") or "").strip()
    if not name:
        errors.append("Name is required.")
    elif len(name) > 100:
        errors.append("Name must be 100 characters or fewer.")

    age_group = data.get("age_group", "")
    if age_group not in VALID_AGE_GROUPS:
        errors.append(f"Age group must be one of: {', '.join(VALID_AGE_GROUPS)}.")

    occupation = data.get("occupation", "")
    if occupation not in VALID_OCCUPATIONS:
        errors.append(f"Occupation must be one of: {', '.join(VALID_OCCUPATIONS)}.")

    lifestyle = data.get("lifestyle", "")
    if lifestyle not in VALID_LIFESTYLES:
        errors.append(f"Lifestyle must be one of: {', '.join(VALID_LIFESTYLES)}.")

    sensitivities = data.get("sensitivities", [])
    if isinstance(sensitivities, str):
        sensitivities = [sensitivities]
    for s in sensitivities:
        if s not in VALID_SENSITIVITIES:
            errors.append(f"Invalid sensitivity: '{s}'.")

    return len(errors) == 0, errors


def validate_location(location: str) -> tuple[bool, str]:
    """
    Basic sanity-check on location input.
    Returns (is_valid: bool, error_message: str)
    """
    if not location or not location.strip():
        return False, "Location is required."
    if len(location.strip()) > 100:
        return False, "Location name is too long."
    return True, ""
