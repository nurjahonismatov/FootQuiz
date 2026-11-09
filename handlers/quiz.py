from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from database.engine import async_session
from database.queries import get_user, get_active_session
from keyboards.quiz import categories_keyboard, difficulty_keyboard, options_keyboard, after_quiz_keyboard
from services.quiz_service import start_quiz, get_current_question_data, submit_answer
from services.xp_service import result_message
from utils.helpers import t, DIFFICULTY_EMOJI
from config import QUESTIONS_PER_GAME

router = Router()


async def get_lang(user_id: int) -> str:
    async with async_session() as session:
        user = await get_user(session, user_id)
        return user.language if user else "uz"


@router.callback_query(F.data == "quiz_start")
async def quiz_start(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(
        t("choose_category", lang),
        reply_markup=categories_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cat:"))
async def choose_category(callback: CallbackQuery):
    category = callback.data.split(":")[1]
    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(
        t("choose_difficulty", lang),
        reply_markup=difficulty_keyboard(lang, category)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("diff:"))
async def choose_difficulty_and_start(callback: CallbackQuery):
    parts = callback.data.split(":")
    difficulty = parts[1]
    category = parts[2] if len(parts) > 2 else "general"
    lang = await get_lang(callback.from_user.id)
    
    async with async_session() as session:
        qs, first_q = await start_quiz(
            session,
            callback.from_user.id,
            mode="quiz",
            category=category,
            difficulty=difficulty,
            count=QUESTIONS_PER_GAME
        )
        if not qs or not first_q:
            await callback.message.edit_text(t("no_questions", lang))
            await callback.answer()
            return
        
        q_data = await get_current_question_data(session, qs, lang)
    
    if not q_data:
        await callback.message.edit_text(t("no_questions", lang))
        await callback.answer()
        return

    diff_emoji = DIFFICULTY_EMOJI.get(q_data["difficulty"], "")
    text = (
        f"{diff_emoji} <b>{q_data['category'].replace('_', ' ').title()}</b>\n"
        f"{t('question_progress', lang, current=1, total=qs.total_questions)}\n"
        f"{t('score', lang, score=0)}\n\n"
        f"<b>{q_data['question']}</b>"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=options_keyboard(q_data["options"], q_data["id"], q_data["correct_index"])
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ans:"))
async def process_answer_callback(callback: CallbackQuery):
    # ans:question_id:selected:correct
    parts = callback.data.split(":")
    if len(parts) != 4:
        await callback.answer("Error")
        return
    
    qid = int(parts[1])
    selected = int(parts[2])
    shown_correct = int(parts[3])
    
    lang = await get_lang(callback.from_user.id)
    
    async with async_session() as session:
        qs = await get_active_session(session, callback.from_user.id)
        if not qs:
            await callback.answer("Session expired", show_alert=True)
            return
        
        result = await submit_answer(session, qs, selected, shown_correct, lang)
    
    if "error" in result:
        await callback.answer("Error processing answer")
        return
    
    # Feedback
    if result["correct"]:
        feedback = t("correct", lang)
    else:
        feedback = t("wrong", lang)
    
    expl = ""
    if result["explanation"]:
        expl = "\n" + t("explanation", lang, text=result["explanation"])
    
    xp_text = ""
    if result["xp_gained"] > 0:
        xp_text = f"\n{t('xp_gained', lang, xp=result['xp_gained'])}"
    
    # Show result briefly then next or finish
    await callback.message.edit_text(
        f"{feedback}{xp_text}{expl}"
    )
    
    if result["finished"]:
        res_msg = result_message(result["score"], result["total"], lang)
        final = t(
            "quiz_finished", lang,
            correct=result["score"],
            total=result["total"],
            xp=result["score"] * 10,  # approximate
            result=res_msg
        )
        await callback.message.answer(final, reply_markup=after_quiz_keyboard(lang))
    else:
        next_q = result["next_question"]
        if next_q:
            diff_emoji = DIFFICULTY_EMOJI.get(next_q["difficulty"], "")
            text = (
                f"{diff_emoji} <b>{next_q['category'].replace('_', ' ').title()}</b>\n"
                f"{t('question_progress', lang, current=result['current']+1, total=result['total'])}\n"
                f"{t('score', lang, score=result['score'])}\n\n"
                f"<b>{next_q['question']}</b>"
            )
            await callback.message.answer(
                text,
                reply_markup=options_keyboard(next_q["options"], next_q["id"], next_q["correct_index"])
            )
    
    await callback.answer()