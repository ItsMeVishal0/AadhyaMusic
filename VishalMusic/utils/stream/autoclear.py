# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import os

from config import autoclean


async def auto_clean(popped):
    if not popped:
        return
    # 1. Clean downloaded file from disk
    try:
        rem = popped.get("file")
        if rem and isinstance(rem, str) and not rem.startswith(("http://", "https://")):
            if rem in autoclean:
                autoclean.remove(rem)
            count = autoclean.count(rem)
            if count == 0:
                if "vid_" not in rem and "live_" not in rem and "index_" not in rem:
                    try:
                        if os.path.exists(rem):
                            os.remove(rem)
                    except Exception:
                        pass
    except Exception:
        pass

    # 2. Delete old Now Playing / Mystic message from group
    try:
        mystic_msg = popped.get("mystic")
        if mystic_msg:
            if hasattr(mystic_msg, "delete"):
                await mystic_msg.delete()
            elif isinstance(mystic_msg, dict) and "message_id" in mystic_msg:
                import aiohttp
                import config
                chat_id = popped.get("chat_id")
                if chat_id and getattr(config, "BOT_TOKEN", None):
                    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/deleteMessage"
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as s:
                        await s.post(url, json={"chat_id": chat_id, "message_id": mystic_msg["message_id"]})
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
