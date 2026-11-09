import json
from datetime import date, datetime
from sqlalchemy import select, update, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import (
    User, Question, UserQuestionHistory, QuizSession, 
    Battle, DailyChallenge, UserDailyProgress
)
from config import LEVELS, XP_CORRECT, XP_HARD, XP_EXPERT


async def get_or_create_user(session: AsyncSession, user_id: int, username: str | None, full_name: str) -> User:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(id=user_id, username=username, full_name=full_name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        # Update username/name if changed
        if username and user.username != username:
            user.username = username
        if full_name and user.full_name != full_name:
            user.full_name = full_name
        await session.commit()
    return user


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_user_language(session: AsyncSession, user_id: int, language: str):
    await session.execute(
        update(User).where(User.id == user_id).values(language=language)
    )
    await session.commit()


async def add_xp(session: AsyncSession, user_id: int, amount: int) -> tuple[int, str]:
    user = await get_user(session, user_id)
    if not user:
        return 0, "Beginner"
    user.xp += amount
    # Update level
    new_level = "Beginner"
    for threshold, level_name in sorted(LEVELS.items(), reverse=True):
        if user.xp >= threshold:
            new_level = level_name
            break
    user.level = new_level
    await session.commit()
    return user.xp, user.level


async def record_answer(session: AsyncSession, user_id: int, question_id: int, was_correct: bool):
    # Check if already answered this question recently (prevent exploit)
    result = await session.execute(
        select(UserQuestionHistory).where(
            and_(
                UserQuestionHistory.user_id == user_id,
                UserQuestionHistory.question_id == question_id
            )
        )
    )
    existing = result.scalar_one_or_none()
    if not existing:
        history = UserQuestionHistory(
            user_id=user_id,
            question_id=question_id,
            was_correct=was_correct
        )
        session.add(history)
    
    user = await get_user(session, user_id)
    if user:
        if was_correct:
            user.correct_answers += 1
        else:
            user.wrong_answers += 1
    await session.commit()


async def get_question_ids_shown_to_user(session: AsyncSession, user_id: int, limit: int = 200) -> list[int]:
    result = await session.execute(
        select(UserQuestionHistory.question_id)
        .where(UserQuestionHistory.user_id == user_id)
        .order_by(desc(UserQuestionHistory.answered_at))
        .limit(limit)
    )
    return [row[0] for row in result.all()]


async def create_quiz_session(
    session: AsyncSession,
    user_id: int,
    mode: str,
    category: str | None,
    difficulty: str | None,
    question_ids: list[int],
    total: int = 10
) -> QuizSession:
    qs = QuizSession(
        user_id=user_id,
        mode=mode,
        category=category,
        difficulty=difficulty,
        total_questions=total,
        question_ids=json.dumps(question_ids),
        answers=json.dumps([])
    )
    session.add(qs)
    await session.commit()
    await session.refresh(qs)
    return qs


async def get_active_session(session: AsyncSession, user_id: int) -> QuizSession | None:
    result = await session.execute(
        select(QuizSession)
        .where(
            and_(
                QuizSession.user_id == user_id,
                QuizSession.is_finished == False
            )
        )
        .order_by(desc(QuizSession.started_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def finish_session(session: AsyncSession, session_id: int, score: int):
    await session.execute(
        update(QuizSession)
        .where(QuizSession.id == session_id)
        .values(
            is_finished=True,
            score=score,
            finished_at=datetime.utcnow()
        )
    )
    user_result = await session.execute(
        select(QuizSession.user_id).where(QuizSession.id == session_id)
    )
    user_id = user_result.scalar_one()
    await session.execute(
        update(User)
        .where(User.id == user_id)
        .values(games_played=User.games_played + 1)
    )
    await session.commit()


async def get_global_rankings(session: AsyncSession, limit: int = 20) -> list[User]:
    result = await session.execute(
        select(User)
        .where(User.is_blocked == False)
        .order_by(desc(User.xp))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_user_rank(session: AsyncSession, user_id: int) -> int:
    user = await get_user(session, user_id)
    if not user:
        return 0
    result = await session.execute(
        select(func.count(User.id)).where(
            and_(User.xp > user.xp, User.is_blocked == False)
        )
    )
    higher = result.scalar() or 0
    return higher + 1


async def get_total_users(session: AsyncSession) -> int:
    result = await session.execute(select(func.count(User.id)))
    return result.scalar() or 0


async def block_user(session: AsyncSession, user_id: int, blocked: bool = True):
    await session.execute(
        update(User).where(User.id == user_id).values(is_blocked=blocked)
    )
    await session.commit()


async def get_all_users(session: AsyncSession) -> list[User]:
    result = await session.execute(select(User).where(User.is_blocked == False))
    return list(result.scalars().all())


async def get_question_by_id(session: AsyncSession, qid: int) -> Question | None:
    result = await session.execute(select(Question).where(Question.id == qid))
    return result.scalar_one_or_none()


async def increment_question_stats(session: AsyncSession, qid: int, was_correct: bool):
    q = await get_question_by_id(session, qid)
    if q:
        q.times_shown += 1
        if was_correct:
            q.times_correct += 1
        await session.commit()


async def get_questions_count(session: AsyncSession) -> int:
    result = await session.execute(select(func.count(Question.id)).where(Question.is_active == True))
    return result.scalar() or 0


async def get_or_create_daily_challenge(session: AsyncSession, challenge_date: date, question_ids: list[int]) -> DailyChallenge:
    result = await session.execute(
        select(DailyChallenge).where(DailyChallenge.challenge_date == challenge_date)
    )
    dc = result.scalar_one_or_none()
    if not dc:
        dc = DailyChallenge(
            challenge_date=challenge_date,
            question_ids=json.dumps(question_ids)
        )
        session.add(dc)
        await session.commit()
        await session.refresh(dc)
    return dc


async def get_user_daily_progress(session: AsyncSession, user_id: int, challenge_date: date) -> UserDailyProgress | None:
    result = await session.execute(
        select(UserDailyProgress).where(
            and_(
                UserDailyProgress.user_id == user_id,
                UserDailyProgress.challenge_date == challenge_date
            )
        )
    )
    return result.scalar_one_or_none()


async def complete_daily(session: AsyncSession, user_id: int, challenge_date: date, score: int, xp: int):
    progress = await get_user_daily_progress(session, user_id, challenge_date)
    if not progress:
        progress = UserDailyProgress(
            user_id=user_id,
            challenge_date=challenge_date,
            score=score,
            completed=True,
            xp_earned=xp
        )
        session.add(progress)
    else:
        progress.score = score
        progress.completed = True
        progress.xp_earned = xp
    user = await get_user(session, user_id)
    if user:
        if user.last_daily and (challenge_date - user.last_daily).days == 1:
            user.daily_streak += 1
        else:
            user.daily_streak = 1
        user.last_daily = challenge_date
    await session.commit()