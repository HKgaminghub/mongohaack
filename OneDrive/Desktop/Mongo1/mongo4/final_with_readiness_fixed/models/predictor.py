import joblib
import os
import pandas as pd

MODELS_DIR = os.path.dirname(__file__)

MODELS = {
    "mission_readiness": os.path.join(MODELS_DIR, "classifier_readiness.joblib"),
    "performance_score": os.path.join(MODELS_DIR, "classifier_performance.joblib"),
    "leadership_potential": os.path.join(MODELS_DIR, "classifier_leadership.joblib"),
}

_CACHED = {}

def _load(name):
    if name not in _CACHED:
        _CACHED[name] = joblib.load(MODELS[name])
    return _CACHED[name]

def predict_all(role: str, skills: str, experience_years: int, training_completed: bool, medical_score: float):
    df = pd.DataFrame([{
        "role": role,
        "skills": skills,
        "experience_years": int(experience_years),
        "training_completed": 1 if training_completed else 0,
        "medical_score": float(medical_score),
    }])
    readiness = _load("mission_readiness").predict(df)[0]
    performance = _load("performance_score").predict(df)[0]
    leadership = _load("leadership_potential").predict(df)[0]
    return {
        "mission_readiness": str(readiness),
        "performance_score": str(performance),
        "leadership_potential": str(leadership),
    }