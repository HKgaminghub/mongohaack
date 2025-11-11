# --- Add to your Flask app.py ---
from flask import render_template, request, redirect, url_for, flash
from werkzeug.exceptions import BadRequest
import os, sys

# Point this to where you place the 'models' folder (copied from /predictive_pipeline/models)
ML_MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
if ML_MODELS_DIR not in sys.path:
    sys.path.append(ML_MODELS_DIR)

try:
    from predictor import predict_all  # inside models/predictor.py
except Exception as e:
    raise RuntimeError(f"Could not import predictor from models: {e}")

@app.route("/add-personnel", methods=["GET", "POST"])
@login_required
def add_personnel():
    # Choices derived from your dataset
    ROLE_CHOICES = ["Pilot", "Engineer", "Technician", "Radar Operator", "Cybersecurity", "Admin", "Medical"]
    SKILL_CHOICES = ["Technician", "Engineer", "Pilot", "Radar Operator", "Cybersecurity", "Admin", "Medical"]

    if request.method == "POST":
        try:
            role = (request.form.get("role") or "").strip()
            skills = (request.form.get("skills") or "").strip()
            experience_years = int(request.form.get("experience_years") or 0)
            training_completed = (request.form.get("training_completed") == "yes")
            medical_score = float(request.form.get("medical_score") or 0)

            if not role or not skills:
                raise BadRequest("Role and Skills are required.")
            if experience_years < 0 or medical_score < 0:
                raise BadRequest("Experience years and medical score must be non-negative.")

            preds = predict_all(role, skills, experience_years, training_completed, medical_score)

            # If you have a DB model, insert here. Example:
            # new_person = Personnel(
            #     role=role, skills=skills, experience_years=experience_years,
            #     training_completed=training_completed, medical_score=medical_score,
            #     mission_readiness=preds["mission_readiness"],
            #     performance_score=preds["performance_score"],
            #     leadership_potential=preds["leadership_potential"],
            # )
            # db.session.add(new_person); db.session.commit()

            flash("Personnel added. Predictions generated successfully.", "success")
            return render_template("add_personnel.html",
                                   role_choices=ROLE_CHOICES,
                                   skill_choices=SKILL_CHOICES,
                                   preds=preds)
        except Exception as e:
            flash(f"Error: {e}", "error")
            return render_template("add_personnel.html",
                                   role_choices=ROLE_CHOICES,
                                   skill_choices=SKILL_CHOICES,
                                   preds=None)

    return render_template("add_personnel.html",
                           role_choices=ROLE_CHOICES,
                           skill_choices=SKILL_CHOICES,
                           preds=None)