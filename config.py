import os

ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
DATABASE_PATH: str = "evaluations.db"
CONVERSATIONS_PATH: str = "data/sample_data.json"
MODEL_NAME: str = "claude-sonnet-4-20250514"

