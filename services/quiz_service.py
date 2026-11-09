import json
from sqlalchemy.ext.asyncio import AsyncSession
from database.queries import (
    create_quiz_session, get_active_session, finish_session,
    record_answer, add_xp, increment_question_stats, get_question_by_id
)
from services.question_selector import select_questions, get_localized_question
from services.xp_service import calculate_xp
from config import QUESTIONS_PER_GAME


async def start_quiz(
    session: AsyncSession,
    user_id: int,
    mode: str = "quiz",
    category: str | None = None,
    difficulty: str | None = None,
    count: int = QUESTIONS_PER_GAME
) -> tuple:
    """Start a new quiz session. Returns (session_obj, first_question_data) or (None, None)"""
    # End any existing active session
    active = await get_active_session(session, user_id)
    if active:
        active.is_finished = True
        await session.commit()

    questions = await select_questions(
        session, user_id, count=count, category=category, difficulty=difficulty
    )
    if not questions:
        return None, None

    q_ids = [q.id for q in questions]
    qs = await create_quiz_session(
        session, user_id, mode, category, difficulty, q_ids, total=len(q_ids)
    )
    
    # Get first question localized later by handler
    return qs, questions[0]


async def get_current_question_data(session: AsyncSession, quiz_session, lang: str) -> dict | None:
    q_ids = json.loads(quiz_session.question_ids)
    idx = quiz_session.current_question
    if idx >= len(q_ids):
        return None
    q = await get_question_by_id(session, q_ids[idx])
    if not q:
        return None
    return get_localized_question(q, lang)


async def process_answer(
    session: AsyncSession,
    quiz_session,
    selected_index: int,
    lang: str
) -> dict:
    """
    Process answer, return result dict:
    {
        correct: bool,
        correct_index: int,
        explanation: str,
        xp_gained: int,
        finished: bool,
        score: int,
        total: int,
        next_question: dict | None
    }
    """
    q_ids = json.loads(quiz_session.question_ids)
    answers = json.loads(quiz_session.answers)
    idx = quiz_session.current_question
    qid = q_ids[idx]
    
    q = await get_question_by_id(session, qid)
    if not q:
        return {"error": "Question not found"}

    # Get localized to know current correct after shuffle? 
    # Actually we need the correct_index from the version shown to user.
    # For simplicity, we store the shuffled correct in the flow.
    # Here we re-get and assume handler passes the correct_index that was shown.
    
    # The handler should pass the correct_index that was displayed.
    # We'll accept selected_index and compare to the one stored in answers metadata if needed.
    # Simplified: we re-localize (shuffle is random each time - PROBLEM)
    
    # Better approach: store the shown correct_index with the session answers.
    # For this version, we will have the handler send both selected and the expected correct.
    
    return {
        "question_id": qid,
        "difficulty": q.difficulty,
    }


async def submit_answer(
    session: AsyncSession,
    quiz_session,
    selected_index: int,
    shown_correct_index: int,
    lang: str
) -> dict:
    q_ids = json.loads(quiz_session.question_ids)
    answers = json.loads(quiz_session.answers)
    idx = quiz_session.current_question
    qid = q_ids[idx]
    
    q = await get_question_by_id(session, qid)
    if not q:
        return {"error": "not_found"}

    is_correct = (selected_index == shown_correct_index)
    
    # Record
    await record_answer(session, quiz_session.user_id, qid, is_correct)
    await increment_question_stats(session, qid, is_correct)
    
    xp = calculate_xp(q.difficulty, is_correct)
    if xp > 0:
        await add_xp(session, quiz_session.user_id, xp)
    
    answers.append({
        "qid": qid,
        "selected": selected_index,
        "correct": shown_correct_index,
        "is_correct": is_correct
    })
    
    quiz_session.answers = json.dumps(answers)
    if is_correct:
        quiz_session.score += 1
    quiz_session.current_question += 1
    await session.commit()
    
    finished = quiz_session.current_question >= quiz_session.total_questions
    
    next_q = None
    if not finished:
        next_raw = await get_question_by_id(session, q_ids[quiz_session.current_question])
        if next_raw:
            next_q = get_localized_question(next_raw, lang)
    
    if finished:
        await finish_session(session, quiz_session.id, quiz_session.score)
    
    # Get explanation in lang
    if lang == "en":
        expl = q.explanation_en or ""
    elif lang == "ru":
        expl = q.explanation_ru or ""
    else:
        expl = q.explanation_uz or ""
    
    return {
        "correct": is_correct,
        "correct_index": shown_correct_index,
        "explanation": expl,
        "xp_gained": xp,
        "finished": finished,
        "score": quiz_session.score,
        "total": quiz_session.total_questions,
        "current": quiz_session.current_question,
        "next_question": next_q,
        "difficulty": q.difficulty
    }