import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-prod")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{(BASE_DIR / 'instance' / 'iaf.sqlite').as_posix()}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb+srv://<user>:<pass>@<cluster>/?retryWrites=true&w=majority&appName=default')
    DATA_CSV_PATH = os.environ.get(
        "DATA_CSV_PATH",
        (BASE_DIR / 'data' / 'IAF_Human_Management_Synthetic_Dataset.csv').as_posix()
    )
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
