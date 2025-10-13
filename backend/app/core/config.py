import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(str(ROOT_DIR / '.env'))

class Settings:
    PROJECT_NAME: str = "Delivery App API"
    VERSION: str = "1.0.0"
    MONGO_URL: str = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    DB_NAME: str = os.environ.get("DB_NAME", "delivery_app_db")
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET", "super-secret-jwt-key")
    ALGORITHM: str = os.environ.get("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days

settings = Settings()
