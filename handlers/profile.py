from aiogram import Router, F
from aiogram.types import Message
from database.engine import async_session
from database.queries import get_user, get_user_rank
from keyboards.profile import profile_keyboard
from utils.helpers import t

router = Router()


@router.message(F.text == "/rankings")
async def cmd_rankings(message: Message):
    from services.ranking_service import get_rankings_text
    async with async_session() as session:
        user = await get_user(session, message.from_user.id)
        lang = user.language if user else "uz"
        text = await get_rankings_text(session, message.from_user.id, lang)
    await message.answer(text)