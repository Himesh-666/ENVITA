from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user       import create_user
from utils.validators  import validate_profile

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        # Collect form data
        data = {
            "name":       request.form.get("name", "").strip(),
            "age_group":  request.form.get("age_group", ""),
            "occupation": request.form.get("occupation", ""),
            "lifestyle":  request.form.get("lifestyle", ""),
            # Checkboxes come back as a list
            "sensitivities": request.form.getlist("sensitivities"),
        }

        is_valid, errors = validate_profile(data)
        if not is_valid:
            for err in errors:
                flash(err, "danger")
            return render_template("profile.html", form_data=data)

        # Default empty sensitivities to ["None"]
        if not data["sensitivities"]:
            data["sensitivities"] = ["None"]

        user_id = create_user(
            name         = data["name"],
            age_group    = data["age_group"],
            occupation   = data["occupation"],
            lifestyle    = data["lifestyle"],
            sensitivities = data["sensitivities"],
        )

        session["user_id"] = user_id
        session["user_name"] = data["name"]
        flash(f"Welcome, {data['name']}! Your profile has been saved.", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("profile.html", form_data={})
