import json
from pathlib import Path
from config import BASE_DIR

LOCALES_DIR = BASE_DIR / "locales"


def load_locale(lang: str) -> dict:
    path = LOCALES_DIR / f"{lang}.json"
    if not path.exists():
        path = LOCALES_DIR / "uz.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def t(key: str, lang: str = "uz", **kwargs) -> str:
    """Simple translation helper."""
    locale = load_locale(lang)
    text = locale.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text


DIFFICULTY_EMOJI = {
    "easy": "🟢",
    "medium": "🟡",
    "hard": "🔴",
    "expert": "⚫"
}


CATEGORY_EMOJI = {
    "general": "⚽",
    "players": "👤",
    "clubs": "🏟",
    "national_teams": "🌍",
    "stadiums": "🏟",
    "world_cup": "🏆",
    "ucl": "🏆",
    "leagues": "📊",
    "transfers": "🔄",
    "records": "📈",
    "awards": "🏅",
    "history": "📜",
    "rules": "📋",
    "tactics": "🎯",
    "legendary": "⭐",
    "modern": "🔥",
}


def format_score(score: int, total: int) -> str:
    return f"{score}/{total}"