import os
from dotenv import load_dotenv

load_dotenv()


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    E2B_API_KEY = os.getenv("E2B_API_KEY")
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_API_MODEL = os.getenv("LLM_API_MODEL")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    ALLOW_SERVER_KEY_FALLBACK = _env_bool("ALLOW_SERVER_KEY_FALLBACK", True)
    FRONTEND_ORIGIN = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173",
    )


settings = Settings()