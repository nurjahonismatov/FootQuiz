from config import XP_CORRECT, XP_HARD, XP_EXPERT, XP_DAILY_BONUS, XP_BATTLE_WIN, LEVELS


def calculate_xp(difficulty: str, is_correct: bool) -> int:
    if not is_correct:
        return 0
    if difficulty == "expert":
        return XP_EXPERT
    if difficulty == "hard":
        return XP_HARD
    return XP_CORRECT


def get_level_for_xp(xp: int) -> str:
    for threshold, name in sorted(LEVELS.items(), reverse=True):
        if xp >= threshold:
            return name
    return "Beginner"


def result_message(score: int, total: int, lang: str = "uz") -> str:
    pct = (score / total * 100) if total else 0
    if lang == "en":
        if pct >= 90:
            return "Outstanding! 🏆"
        if pct >= 70:
            return "Excellent! 🔥"
        if pct >= 50:
            return "Good job! 👍"
        if pct >= 30:
            return "Keep practicing! 💪"
        return "Don't give up! ⚽"
    if lang == "ru":
        if pct >= 90:
            return "Великолепно! 🏆"
        if pct >= 70:
            return "Отлично! 🔥"
        if pct >= 50:
            return "Хорошо! 👍"
        if pct >= 30:
            return "Продолжай тренироваться! 💪"
        return "Не сдавайся! ⚽"
    # uz
    if pct >= 90:
        return "Ajoyib! 🏆"
    if pct >= 70:
        return "Zo‘r! 🔥"
    if pct >= 50:
        return "Yaxshi! 👍"
    if pct >= 30:
        return "Mashq qilishda davom et! 💪"
    return "Taslim bo‘lma! ⚽"