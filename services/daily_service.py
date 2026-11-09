from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from database.queries import (
    get_or_create_daily_challenge, get_user_daily_progress, complete_daily, add_xp
)
from services.question_selector import select_questions
from config import DAILY_CHALLENGE_QUESTIONS, XP_DAILY_BONUS


async def get_today_challenge(session: AsyncSession, user_id: int):
    today = date.today()
    progress = await get_user_daily_progress(session, user_id, today)
    if progress and progress.completed:
        return None, progress  # Already done

    # Ensure challenge exists
    questions = await select_questions(session, user_id=0, count=DAILY_CHALLENGE_QUESTIONS)  # user_id=0 to not exclude
    q_ids = [q.id for q in questions]
    challenge = await get_or_create_daily_challenge(session, today, q_ids)
    return challenge, progress


async def finish_daily(session: AsyncSession, user_id: int, score: int):
    today = date.today()
    bonus = XP_DAILY_BONUS if score >= 3 else 15
    await add_xp(session, user_id, bonus)
    await complete_daily(session, user_id, today, score, bonus)
    return bonus