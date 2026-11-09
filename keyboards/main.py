from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from utils.helpers import t


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O‘zbekcha", callback_data="lang:uz"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
        ],
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        ]
    ])


def main_menu_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("quiz", lang)), KeyboardButton(text=t("guess_player", lang))],
            [KeyboardButton(text=t("guess_club", lang)), KeyboardButton(text=t("national_teams", lang))],
            [KeyboardButton(text=t("history", lang)), KeyboardButton(text=t("tactics", lang))],
            [KeyboardButton(text=t("battle", lang)), KeyboardButton(text=t("daily", lang))],
            [KeyboardButton(text=t("rankings", lang)), KeyboardButton(text=t("profile", lang))],
            [KeyboardButton(text=t("settings", lang))],
        ],
        resize_keyboard=True
    )


def back_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("back", lang))]],
        resize_keyboard=True
    )