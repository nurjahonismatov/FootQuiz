import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///footballiq.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# XP values
XP_CORRECT = 10
XP_HARD = 15
XP_EXPERT = 20
XP_DAILY_BONUS = 30
XP_BATTLE_WIN = 30

# Quiz settings
QUESTIONS_PER_GAME = 10
DAILY_CHALLENGE_QUESTIONS = 5

# Levels
LEVELS = {
    0: "Beginner",
    100: "Amateur",
    300: "Professional",
    600: "Expert",
    1000: "Legend",
    2000: "Football Master",
}

SUPPORTED_LANGUAGES = ["uz", "en", "ru"]
DEFAULT_LANGUAGE = "uz"