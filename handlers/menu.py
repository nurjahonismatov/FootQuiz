from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.engine import async_session
from database.queries import get_user
from keyboards.main import main_menu_keyboard
from keyboards.quiz import categories_keyboard, difficulty_keyboard
from keyboards.profile import settings_keyboard, profile_keyboard
from utils.helpers import t
from services.ranking_service import get_rankings_text
from database.queries import get_user_rank

router = Router()


async def get_lang(user_id: int) -> str:
    async with async_session() as session:
        user = await get_user(session, user_id)
        return user.language if user else "uz"


@router.message(F.text.in_([
    "⚽ Football Quiz", "🧠 Guess the Player", "🏟 Guess the Club",
    "🌍 National Teams", "🏆 Football History", "🎯 Tactical Quiz",
    "⚔️ 1 vs 1 Battle", "📅 Daily Challenge", "🏅 Rankings",
    "👤 My Profile", "⚙️ Settings"
]))
async def main_menu_handler(message: Message):
    lang = await get_lang(message.from_user.id)
    text = message.text

    if text == t("quiz", lang) or "Football Quiz" in text:
        await message.answer(t("choose_category", lang), reply_markup=categories_keyboard(lang))
    
    elif text == t("guess_player", lang) or "Guess the Player" in text:
        # Start guess player mode with players category
        await message.answer(
            t("choose_difficulty", lang),
            reply_markup=difficulty_keyboard(lang, "players")
        )
    
    elif text == t("guess_club", lang) or "Guess the Club" in text:
        await message.answer(
            t("choose_difficulty", lang),
            reply_markup=difficulty_keyboard(lang, "clubs")
        )
    
    elif text == t("national_teams", lang) or "National Teams" in text:
        await message.answer(
            t("choose_difficulty", lang),
            reply_markup=difficulty_keyboard(lang, "national_teams")
        )
    
    elif text == t("history", lang) or "Football History" in text:
        await message.answer(
            t("choose_difficulty", lang),
            reply_markup=difficulty_keyboard(lang, "history")
        )
    
    elif text == t("tactics", lang) or "Tactical Quiz" in text:
        await message.answer(
            t("choose_difficulty", lang),
            reply_markup=difficulty_keyboard(lang, "tactics")
        )
    
    elif text == t("battle", lang) or "1 vs 1" in text:
        await message.answer(t("battle_soon", lang))
    
    elif text == t("daily", lang) or "Daily Challenge" in text:
        from handlers.daily_challenge import start_daily
        await start_daily(message)
    
    elif text == t("rankings", lang) or "Rankings" in text:
        async with async_session() as session:
            text_rank = await get_rankings_text(session, message.from_user.id, lang)
        await message.answer(text_rank)
    
    elif text == t("profile", lang) or "My Profile" in text:
        await show_profile(message)
    
    elif text == t("settings", lang) or "Settings" in text:
        await message.answer(t("settings_title", lang), reply_markup=settings_keyboard(lang))


@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    await callback.message.answer(
        t("main_menu", lang),
        reply_markup=main_menu_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "change_lang")
async def change_lang(callback: CallbackQuery):
    from keyboards.main import language_keyboard
    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(
        t("choose_language", lang),
        reply_markup=language_keyboard()
    )
    await callback.answer()


async def show_profile(message: Message):
    async with async_session() as session:
        user = await get_user(session, message.from_user.id)
        if not user:
            return
        rank = await get_user_rank(session, user.id)
        lang = user.language
    
    text = (
        f"{t('profile_title', lang)}\n\n"
        f"👤 {user.full_name or user.username or user.id}\n"
        f"{t('xp_label', lang, xp=user.xp)}\n"
        f"{t('level_label', lang, level=user.level)}\n"
        f"{t('rank_label', lang, rank=rank)}\n"
        f"{t('games_label', lang, games=user.games_played)}\n"
        f"{t('correct_label', lang, correct=user.correct_answers)}\n"
        f"{t('wrong_label', lang, wrong=user.wrong_answers)}\n"
        f"{t('streak_label', lang, streak=user.daily_streak)}"
    )
    await message.answer(text, reply_markup=profile_keyboard(lang))


@router.message(F.text == "/profile")
async def cmd_profile(message: Message):
    await show_profile(message)