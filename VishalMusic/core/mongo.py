# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import re
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI, BOT_TOKEN
from ..logging import LOGGER

LOGGER(__name__).info("ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ʏᴏᴜʀ ᴍᴏɴɢᴏ ᴅᴀᴛᴀʙᴀsᴇ...")

def _get_bot_db_name() -> str:
    db_name = "Vishal"
    if not BOT_TOKEN:
        return db_name
    try:
        resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=5).json()
        if resp.get("ok"):
            uname = resp.get("result", {}).get("username")
            if uname:
                db_name = uname
            else:
                fname = resp.get("result", {}).get("first_name", "")
                db_name = re.sub(r'[\s./\\"\0$]+', '_', fname) or f"bot_{BOT_TOKEN.split(':')[0]}"
        else:
            db_name = f"bot_{BOT_TOKEN.split(':')[0]}"
    except Exception:
        db_name = f"bot_{BOT_TOKEN.split(':')[0]}"
    return db_name

DB_NAME = _get_bot_db_name()

try:
    _mongo_async_ = AsyncIOMotorClient(
        MONGO_DB_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        maxPoolSize=20,
        minPoolSize=1,
        maxIdleTimeMS=45000,
        waitQueueTimeoutMS=5000,
    )
    mongodb = _mongo_async_[DB_NAME]
    LOGGER(__name__).info(f"ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴍᴏɴɢᴏ ᴅᴀᴛᴀʙᴀsᴇ: [{DB_NAME}] (ᴏᴘᴛɪᴍɪᴢᴇᴅ ᴘᴏᴏʟ).")
except Exception as e:
    LOGGER(__name__).error(f"Failed to connect to your Mongo Database: {e}")
    exit()

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
