import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # E2B
    E2B_API_KEY = os.getenv("E2B_API_KEY")

settings = Settings()