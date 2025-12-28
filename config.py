import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
DATABASE_PATH: str = "evaluations.db"
CONVERSATIONS_PATH: str = "data/sample_data.json"
MODEL_NAME: str = "llama-3.1-8b-instant"

