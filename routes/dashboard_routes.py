from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models.user               import get_user, save_assessment
from services.climate_score_service import get_full_climate_assessment
from services.gemini_service   import generate_recommendations, parse_ai_sections
from utils.validators          import validate_location
from utils.helpers             import markdown_to_html, format_datetime

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # Must have a profile
    user_id = session.get("user_id")
    if not user_id:
        flash("Please create your profile first.", "warning")
        return redirect(url_for("profile.profile"))

    user = get_user(user_id)
    if not user:
        session.clear()
        flash("Profile not found. Please create a new one.", "warning")
        return redirect(url_for("profile.profile"))

    context = {
        "user": user,
        "now":  format_datetime(),
    }

    if request.method == "POST":
        location = request.form.get("location", "").strip()
        valid, err = validate_location(location)
        if not valid:
            flash(err, "danger")
            return render_template("dashboard.html", **context)

        try:
            # 1. Environmental + score data
            assessment = get_full_climate_assessment(location, user)

            # 2. AI recommendations
            ai_raw = generate_recommendations(
                location     = assessment["location"],
                weather      = assessment["weather"],
                aqi_data     = assessment["aqi_data"],
                user_profile = user,
                score        = assessment["score"],
                risk_category = assessment["risk_category"],
            )

            # 3. Parse & convert AI response to HTML
            ai_sections = parse_ai_sections(ai_raw)
            ai_html = {k: markdown_to_html(v) for k, v in ai_sections.items() if k != "raw"}
            ai_html["raw"] = ai_raw

            # 4. Persist assessment
            save_assessment(
                user_id       = user_id,
                location      = assessment["location"],
                weather       = assessment["weather"],
                aqi_data      = assessment["aqi_data"],
                score         = assessment["score"],
                risk_category = assessment["risk_category"],
                ai_response   = ai_raw,
            )

            context.update({
                "assessment":  assessment,
                "ai_sections": ai_html,
                "location":    assessment["location"],
            })

        except ValueError as exc:
            flash(str(exc), "danger")
        except Exception as exc:
            flash(f"Unable to fetch data: {exc}", "danger")

    return render_template("dashboard.html", **context)
