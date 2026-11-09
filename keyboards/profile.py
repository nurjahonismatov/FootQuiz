from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.helpers import t


def settings_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("change_language", lang), callback_data="change_lang")],
        [InlineKeyboardButton(text=t("back", lang), callback_data="back_main")],
    ])


def profile_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("back", lang), callback_data="back_main")],
    ])