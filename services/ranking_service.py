from sqlalchemy.ext.asyncio import AsyncSession
from database.queries import get_global_rankings, get_user_rank


async def get_rankings_text(session: AsyncSession, user_id: int, lang: str = "uz") -> str:
    rankings = await get_global_rankings(session, limit=15)
    my_rank = await get_user_rank(session, user_id)
    
    if lang == "en":
        header = "🏅 <b>Global Rankings</b>\n\n"
        empty = "No players yet."
    elif lang == "ru":
        header = "🏅 <b>Глобальный рейтинг</b>\n\n"
        empty = "Пока нет игроков."
    else:
        header = "🏅 <b>Global reyting</b>\n\n"
        empty = "Hali o‘yinchilar yo‘q."

    if not rankings:
        return header + empty

    lines = []
    medals = ["🥇", "🥈", "🥉"]
    for i, u in enumerate(rankings):
        medal = medals[i] if i < 3 else f"{i+1}."
        name = u.username or u.full_name or str(u.id)
        lines.append(f"{medal} <b>{name}</b> — {u.xp} XP ({u.level})")

    text = header + "\n".join(lines)
    text += f"\n\n📍 Sizning o‘rningiz: <b>#{my_rank}</b>" if lang == "uz" else ""
    if lang == "en":
        text += f"\n\n📍 Your rank: <b>#{my_rank}</b>"
    elif lang == "ru":
        text += f"\n\n📍 Ваше место: <b>#{my_rank}</b>"
    return text