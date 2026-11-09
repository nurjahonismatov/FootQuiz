from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database.engine import async_session
from database.queries import get_total_users, get_questions_count, get_all_users, block_user
from config import ADMIN_IDS
from utils.helpers import t

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Admin only.")
        return
    
    async with async_session() as session:
        users = await get_total_users(session)
        questions = await get_questions_count(session)
    
    text = (
        "🔧 <b>Admin Panel</b>\n\n"
        f"👥 Users: {users}\n"
        f"❓ Questions: {questions}\n\n"
        "Commands:\n"
        "/stats — Statistics\n"
        "/broadcast <text> — Send to all users\n"
        "/block <user_id> — Block user\n"
        "/unblock <user_id> — Unblock user"
    )
    await message.answer(text)


@router.message(Command("stats"))
async def admin_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    async with async_session() as session:
        users = await get_total_users(session)
        questions = await get_questions_count(session)
    await message.answer(f"👥 Users: {users}\n❓ Active questions: {questions}")


@router.message(Command("broadcast"))
async def broadcast(message: Message):
    if not is_admin(message.from_user.id):
        return
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.answer("Usage: /broadcast Your message here")
        return
    
    async with async_session() as session:
        users = await get_all_users(session)
    
    success = 0
    for u in users:
        try:
            await message.bot.send_message(u.id, f"📢 <b>FootballIQ</b>\n\n{text}")
            success += 1
        except Exception:
            pass
    await message.answer(f"✅ Sent to {success}/{len(users)} users.")


@router.message(Command("block"))
async def cmd_block(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Usage: /block <user_id>")
        return
    try:
        uid = int(parts[1])
        async with async_session() as session:
            await block_user(session, uid, True)
        await message.answer(f"🚫 User {uid} blocked.")
    except ValueError:
        await message.answer("Invalid user_id")


@router.message(Command("unblock"))
async def cmd_unblock(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Usage: /unblock <user_id>")
        return
    try:
        uid = int(parts[1])
        async with async_session() as session:
            await block_user(session, uid, False)
        await message.answer(f"✅ User {uid} unblocked.")
    except ValueError:
        await message.answer("Invalid user_id")