import json
import random
from sqlalchemy import select, and_, not_
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Question
from database.queries import get_question_ids_shown_to_user


async def select_questions(
    session: AsyncSession,
    user_id: int,
    count: int = 10,
    category: str | None = None,
    difficulty: str | None = None,
    exclude_ids: list[int] | None = None
) -> list[Question]:
    """
    Smart question selector that:
    - Avoids recently shown questions to this user
    - Balances categories if no category specified
    - Respects difficulty
    - Randomizes order
    """
    exclude = set(exclude_ids or [])
    recent = await get_question_ids_shown_to_user(session, user_id, limit=150)
    exclude.update(recent)

    query = select(Question).where(Question.is_active == True)

    if category:
        query = query.where(Question.category == category)
    if difficulty:
        query = query.where(Question.difficulty == difficulty)

    if exclude:
        query = query.where(not_(Question.id.in_(list(exclude))))

    result = await session.execute(query)
    candidates = list(result.scalars().all())

    # If not enough, relax recent exclusion
    if len(candidates) < count:
        query2 = select(Question).where(Question.is_active == True)
        if category:
            query2 = query2.where(Question.category == category)
        if difficulty:
            query2 = query2.where(Question.difficulty == difficulty)
        if exclude_ids:
            query2 = query2.where(not_(Question.id.in_(exclude_ids)))
        result2 = await session.execute(query2)
        candidates = list(result2.scalars().all())

    # Still not enough? Take any
    if len(candidates) < count:
        result3 = await session.execute(select(Question).where(Question.is_active == True))
        candidates = list(result3.scalars().all())

    if not candidates:
        return []

    # Prefer less shown questions
    candidates.sort(key=lambda q: q.times_shown)
    
    # Take more than needed then shuffle for variety
    pool_size = min(len(candidates), count * 3)
    pool = candidates[:pool_size]
    random.shuffle(pool)
    
    selected = pool[:count]
    
    # If we have category balance requirement and no fixed category
    if not category and len(selected) > 3:
        # Try to diversify categories a bit
        categories_seen = set()
        diversified = []
        remaining = []
        for q in selected:
            if q.category not in categories_seen:
                diversified.append(q)
                categories_seen.add(q.category)
            else:
                remaining.append(q)
        selected = (diversified + remaining)[:count]

    random.shuffle(selected)
    return selected


def shuffle_options(options: list[str], correct_index: int) -> tuple[list[str], int]:
    """Shuffle options and return new list + new correct index."""
    indexed = list(enumerate(options))
    random.shuffle(indexed)
    new_options = [opt for _, opt in indexed]
    new_correct = next(i for i, (orig_i, _) in enumerate(indexed) if orig_i == correct_index)
    return new_options, new_correct


def get_localized_question(q: Question, lang: str) -> dict:
    """Return question data in the requested language."""
    if lang == "en":
        question = q.question_en
        options = json.loads(q.options_en)
        explanation = q.explanation_en
    elif lang == "ru":
        question = q.question_ru
        options = json.loads(q.options_ru)
        explanation = q.explanation_ru
    else:
        question = q.question_uz
        options = json.loads(q.options_uz)
        explanation = q.explanation_uz

    options, correct_idx = shuffle_options(options, q.correct_index)
    
    return {
        "id": q.id,
        "question": question,
        "options": options,
        "correct_index": correct_idx,
        "explanation": explanation or "",
        "difficulty": q.difficulty,
        "category": q.category
    }