from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session
from database.queries import get_or_create_user, update_user_language, get_user
from keyboards.main import language_keyboard, main_menu_keyboard
from utils.helpers import t
from config import ADMIN_IDS

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    async with async_session() as session:
        user = await get_or_create_user(
            session,
            message.from_user.id,
            message.from_user.username,
            message.from_user.full_name or ""
        )
        if user.is_blocked:
            await message.answer(t("blocked", user.language))
            return

        # Always show language choice on /start for new or returning
        await message.answer(
            t("choose_language", user.language),
            reply_markup=language_keyboard()
        )


@router.callback_query(F.data.startswith("lang:"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split(":")[1]
    async with async_session() as session:
        await update_user_language(session, callback.from_user.id, lang)
        user = await get_user(session, callback.from_user.id)
    
    await callback.message.edit_text(t("language_set", lang))
    await callback.message.answer(
        t("welcome", lang),
        reply_markup=main_menu_keyboard(lang)
    )
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
    async with async_session() as session:
        user = await get_user(session, message.from_user.id)
        lang = user.language if user else "uz"
    text = (
        "⚽ <b>FootballIQ</b>\n\n"
        "Futbol bilimlaringni sinab ko‘r, XP to‘pla va reytingda yuqoriga ko‘taril!\n\n"
        "/start — Botni ishga tushirish\n"
        "/profile — Profilingiz\n"
        "/rankings — Reytinglar"
    )
    if lang == "en":
        text = (
            "⚽ <b>FootballIQ</b>\n\n"
            "Test your football knowledge, earn XP and climb the rankings!\n\n"
            "/start — Start the bot\n"
            "/profile — Your profile\n"
            "/rankings — Rankings"
        )
    elif lang == "ru":
        text = (
            "⚽ <b>FootballIQ</b>\n\n"
            "Проверьте свои футбольные знания, зарабатывайте XP и поднимайтесь в рейтинге!\n\n"
            "/start — Запустить бота\n"
            "/profile — Ваш профиль\n"
            "/rankings — Рейтинг"
        )
    await message.answer(text)