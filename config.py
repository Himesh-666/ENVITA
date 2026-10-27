import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "envita-secret-key-change-in-prod")
    DEBUG = os.environ.get("DEBUG", "True") == "True"

    # Database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, "databasae", "envita.db")

    # API Keys
    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
    OPENAQ_API_KEY = os.environ.get("OPENAQ_API_KEY", "")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

    # App
    APP_NAME = "ENVITA"
    APP_TAGLINE = "Transforming Climate Data into Healthier Living"



