import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # E2B
    E2B_API_KEY = os.getenv("E2B_API_KEY")
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_API_MODEL = os.getenv("LLM_API_MODEL")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    FRONTEND_ORIGIN = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173",
    )

settings = Settings()