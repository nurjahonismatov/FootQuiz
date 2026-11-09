from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from utils.helpers import t


CATEGORIES = [
    ("general", "⚽ General Football"),
    ("players", "👤 Football Players"),
    ("clubs", "🏟 Football Clubs"),
    ("national_teams", "🌍 National Teams"),
    ("stadiums", "🏟 Stadiums"),
    ("world_cup", "🏆 World Cup"),
    ("ucl", "🏆 UEFA Champions League"),
    ("leagues", "📊 European Leagues"),
    ("transfers", "🔄 Transfers"),
    ("records", "📈 Football Records"),
    ("awards", "🏅 Football Awards"),
    ("history", "📜 Football History"),
    ("rules", "📋 Football Rules"),
    ("tactics", "🎯 Football Tactics"),
    ("legendary", "⭐ Legendary Players"),
    ("modern", "🔥 Modern Football"),
]


def categories_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for i, (cat_id, cat_name) in enumerate(CATEGORIES):
        row.append(InlineKeyboardButton(text=cat_name, callback_data=f"cat:{cat_id}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text=t("back", lang), callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def difficulty_keyboard(lang: str = "uz", category: str = "general") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("easy", lang), callback_data=f"diff:easy:{category}"),
            InlineKeyboardButton(text=t("medium", lang), callback_data=f"diff:medium:{category}"),
        ],
        [
            InlineKeyboardButton(text=t("hard", lang), callback_data=f"diff:hard:{category}"),
            InlineKeyboardButton(text=t("expert", lang), callback_data=f"diff:expert:{category}"),
        ],
        [InlineKeyboardButton(text=t("back", lang), callback_data="quiz_start")]
    ])


def options_keyboard(options: list[str], question_id: int, correct_index: int) -> InlineKeyboardMarkup:
    letters = ["A", "B", "C", "D"]
    buttons = []
    for i, opt in enumerate(options):
        # Encode selected index and correct index for verification
        buttons.append([
            InlineKeyboardButton(
                text=f"{letters[i]}) {opt}",
                callback_data=f"ans:{question_id}:{i}:{correct_index}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def after_quiz_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("play_again", lang), callback_data="quiz_start")],
        [InlineKeyboardButton(text=t("main_menu_btn", lang), callback_data="back_main")],
    ])