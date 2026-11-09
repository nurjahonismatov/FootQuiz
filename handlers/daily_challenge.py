from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database.engine import async_session
from database.queries import get_user, get_active_session
from services.daily_service import get_today_challenge, finish_daily
from services.quiz_service import start_quiz, get_current_question_data, submit_answer
from services.xp_service import result_message
from keyboards.quiz import options_keyboard, after_quiz_keyboard
from utils.helpers import t, DIFFICULTY_EMOJI
from config import DAILY_CHALLENGE_QUESTIONS

router = Router()


async def get_lang(user_id: int) -> str:
    async with async_session() as session:
        user = await get_user(session, user_id)
        return user.language if user else "uz"


async def start_daily(message: Message):
    lang = await get_lang(message.from_user.id)
    async with async_session() as session:
        challenge, progress = await get_today_challenge(session, message.from_user.id)
        if progress and progress.completed:
            await message.answer(
                t("daily_already", lang, score=progress.score, xp=progress.xp_earned)
            )
            return
        
        # Start quiz with daily questions
        qs, first_q = await start_quiz(
            session,
            message.from_user.id,
            mode="daily",
            category=None,
            difficulty=None,
            count=DAILY_CHALLENGE_QUESTIONS
        )
        if not qs:
            await message.answer(t("no_questions", lang))
            return
        
        q_data = await get_current_question_data(session, qs, lang)
    
    if not q_data:
        await message.answer(t("no_questions", lang))
        return

    await message.answer(t("daily_start", lang))
    
    diff_emoji = DIFFICULTY_EMOJI.get(q_data["difficulty"], "")
    text = (
        f"📅 <b>Daily Challenge</b>\n"
        f"{diff_emoji}\n"
        f"{t('question_progress', lang, current=1, total=qs.total_questions)}\n"
        f"{t('score', lang, score=0)}\n\n"
        f"<b>{q_data['question']}</b>"
    )
    await message.answer(
        text,
        reply_markup=options_keyboard(q_data["options"], q_data["id"], q_data["correct_index"])
    )


# Note: answer processing is shared via the ans: callback in quiz.py
# We can detect mode == "daily" there if needed for bonus XP.