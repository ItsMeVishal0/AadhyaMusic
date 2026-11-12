# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import os
import re
from os import getenv
from dotenv import find_dotenv, load_dotenv
from pyrogram import filters

# Ensure project bin directory is in PATH for ffmpeg/ffprobe
_project_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bin"))
if os.path.exists(_project_bin) and _project_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{_project_bin}:{os.environ.get('PATH', '')}"

# Load environment variables from .env file
load_dotenv(find_dotenv())

# ── Core bot config ─────────────────────────────────────────────────────────
API_ID = int(getenv("API_ID", 26493077))
API_HASH = getenv("API_HASH", "6586f0276c7748e54684719bdd247d90")
BOT_TOKEN = getenv("BOT_TOKEN")



OWNER_ID = int(getenv("OWNER_ID", 7044783841))
OWNER_USERNAME = getenv("OWNER_USERNAME", "")
BOT_USERNAME = getenv("BOT_USERNAME", "vaishaliTune_bot")
BOT_NAME = getenv("BOT_NAME", "≽ ^⎚ 𝘃𝗮𝗶𝘀𝗵𝗮𝗹𝗶 𝘅 𝗺𝘂𝘀𝗶𝗰 ⎚^ ≼")
ASSUSERNAME = getenv("ASSUSERNAME", "≽ ^⎚ 𝗮𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁 ⎚^ ≼")

# ── Database & logging ────────────────────────────────────────────────────────
MONGO_DB_URI = getenv("MONGO_DB_URI")
LOGGER_ID = int(getenv("LOGGER_ID", -1002425220992))

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════






# ── Limits (durations in min/sec; sizes in bytes) ──────────────────────────────
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "1200"))


SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "1800"))
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "3221225472"))  # 3 GB
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "3221225472"))  # 3 GB
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "30"))

# ── External & YouTube APIs (Dual API Support) ──────────────────────────────
COOKIE_URL = getenv("COOKIE_URL", "https://batbin.me/cadged")

# API 1 (Primary YouTube API)
YOUTUBE_API_1 = getenv("YOUTUBE_API_1") or getenv("YOUTUBE_API_URL") or getenv("API_URL")
YOUTUBE_API_KEY_1 = getenv("YOUTUBE_API_KEY_1") or getenv("YOUTUBE_API_KEY") or getenv("API_KEY")

# API 2 (Secondary / Fallback YouTube API)
YOUTUBE_API_2 = getenv("YOUTUBE_API_2") or getenv("YOUTUBE_API_URL_2") or getenv("API_URL_2") or getenv("DEEP_API")
YOUTUBE_API_KEY_2 = getenv("YOUTUBE_API_KEY_2") or getenv("YOUTUBE_API_KEY_2") or getenv("API_KEY_2")

# Aliases for backwards compatibility
API_URL = YOUTUBE_API_1
API_KEY = YOUTUBE_API_KEY_1
DEEP_API = YOUTUBE_API_2

# ── Telegram Bot API (Local Server for colored buttons support) ───────────────
# If you run a local Telegram Bot API server, set this to its URL.


# Example: http://localhost:8081  or  http://127.0.0.1:8081
# Without this, button color (style) fields will be ignored by Telegram.
# Setup guide: https://github.com/tdlib/telegram-bot-api
LOCAL_BOT_API_URL = getenv("LOCAL_BOT_API_URL", "").rstrip("/")

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════






# ── Hosting / deployment ───────────────────────────────────────────────────────
PORT = int(getenv("PORT", 2000))
PING_URL = getenv("PING_URL") or getenv("RENDER_EXTERNAL_URL") or getenv("RENDER_URL") or getenv("APP_URL")
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

# ── Git / updates ──────────────────────────────────────────────────────────
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/ItsMeVishal0/VishalMusic.git")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN")  # needed if repo is private



# ── Support links ──────────────────────────────────────────────────────────
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/ItsMeVishalBots")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/ItsMeVishalBots")
# Link used by the /privacy command (set your own privacy-policy post/page)
PRIVACY_LINK = getenv("PRIVACY_LINK", SUPPORT_CHAT)

# ── Assistant auto-leave ───────────────────────────────────────────────────────
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "False").lower() in ("true", "1", "yes")
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "3600"))

# ── Debug ──────────────────────────────────────────────────────────
DEBUG_IGNORE_LOG = True



# ── Spotify (optional) ─────────────────────────────────────────────────────

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════





SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "22b6125bfe224587b722d6815002db2b")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "c9c63c6fbf2f467c8bc68624851e9773")

# ── Session strings (optional) ─────────────────────────────────────────────────
STRING1 = getenv("STRING_SESSION")
STRING2 = getenv("STRING_SESSION2")
STRING3 = getenv("STRING_SESSION3")
STRING4 = getenv("STRING_SESSION4")
STRING5 = getenv("STRING_SESSION5")

# ── Media assets ──────────────────────────────────────────────────────────


START_IMGS = [
    "https://iili.io/npe2zmJ.jpg",
    "https://iili.io/npe25qN.jpg",
    "https://iili.io/npe2cdX.jpg",
    "https://iili.io/npe21mG.jpg",
    "https://iili.io/npe2XB2.jpg",
    "https://iili.io/npe2N29.jpg",
    "https://iili.io/npe2ULQ.jpg",
    "https://iili.io/npe2sYF.jpg",
]
WELCOME_IMG_URL = "https://iili.io/npe2zmJ.jpg"
STICKERS = [
    "CAACAgUAAyEFAASQje-AAAI92mkOFHmOlyKv0vEpoJE6S7ZInIuPAALbFQACSZmpVI0wvAnbSnk9HgQ",
    "CAACAgQAAyEFAASQje-AAAI92GkOFFx4j5i7GwlGsRbvXBaZbgquAAIoFQACir5JU9xIMA-J9yY7HgQ",
    "CAACAgQAAyEFAASQje-AAAI91mkOFEeMiZrau4LoUgHQAuhfVUNoAAJbHQACmKWIUVKzS9qKs-juHgQ",
    "CAACAgUAAyEFAASQje-AAAI91GkOFDevrsTZ_JzDdyHdsu2VhsvHAAJ2EwAC_xfYVo5iQw7a3JPfHgQ",
    "CAACAgUAAyEFAASQje-AAAI90mkOFCn95GwjE62nWBG2o9H-FK15AAJgFQACJ_uwVMGj96qQgd3hHgQ",
    "CAACAgQAAyEFAASQje-AAAI90GkOFCDWtQkvBiumJxSoedz0NqvLAAIzFAAC9ED4UX1Ta6URzlyIHgQ",
]

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════







HELP_IMG_URL = "https://iili.io/npe25qN.jpg"
PING_VID_URL = "https://iili.io/npe2cdX.jpg"
PLAYLIST_IMG_URL = "https://iili.io/npe21mG.jpg"
STATS_VID_URL = "https://iili.io/npe2XB2.jpg"
TELEGRAM_AUDIO_URL = "https://iili.io/npe2N29.jpg"
TELEGRAM_VIDEO_URL = "https://iili.io/npe2ULQ.jpg"
STREAM_IMG_URL = "https://iili.io/npe2sYF.jpg"
SOUNCLOUD_IMG_URL = "https://iili.io/npe2zmJ.jpg"
YOUTUBE_IMG_URL = "https://iili.io/npe25qN.jpg"
SPOTIFY_ARTIST_IMG_URL = SPOTIFY_ALBUM_IMG_URL = SPOTIFY_PLAYLIST_IMG_URL = "https://iili.io/npe2cdX.jpg"

# ── Helpers ────────────────────────────────────────────────────────────
def time_to_seconds(time: str) -> int:


    return sum(int(x) * 60**i for i, x in enumerate(reversed(time.split(":"))))

DURATION_LIMIT = time_to_seconds(f"{DURATION_LIMIT_MIN}:00")

# ───── Bot Search Messages (Single Line) ───── #
# {0} = user mention/name
AYU = [
    "𝐅𝐢𝐧𝐝𝐢𝐧𝐠 𝐘𝐨𝐮𝐫 𝐒𝐨𝐧𝐠 ꨄ︎ {0} ",
    "𝐒𝐞𝐚𝐫𝐜𝐡𝐢𝐧𝐠 𝐁𝐞𝐬𝐭 𝐓𝐫𝐚𝐜𝐤 ♡ {0} ",
    "𝐋𝐨𝐚𝐝𝐢𝐧𝐠 𝐌𝐮𝐬𝐢𝐜 ✦ {0} ",
    "𝐘𝐨𝐮𝐫 𝐕𝐢𝐛𝐞 𝐈𝐬 𝐂𝐨𝐦𝐢𝐧𝐠 ꨄ︎ {0} ",
    "𝐏𝐥𝐚𝐲𝐢𝐧𝐠 𝐒𝐨𝐨𝐧 𝐁𝐚𝐛𝐲 ♡ {0} ",
    "𝐆𝐞𝐭𝐭𝐢𝐧𝐠 𝐑𝐞𝐚𝐝𝐲 𝐅𝐨𝐫 𝐘𝐨𝐮 ✦ {0} ",
    "𝐇𝐨𝐥𝐝 𝐎𝐧 𝐁𝐚𝐛𝐞 ꨄ︎ {0} ",
    "𝐌𝐮𝐬𝐢𝐜 𝐋𝐨𝐚𝐝𝐢𝐧𝐠 𝐅𝐨𝐫 ♡ {0} ",
    "𝐀𝐥𝐦𝐨𝐬𝐭 𝐑𝐞𝐚𝐝𝐲 𝐉𝐚𝐚𝐧 ꨄ︎ {0} ",
    "𝐏𝐫𝐞𝐩𝐚𝐫𝐢𝐧𝐠 𝐘𝐨𝐮𝐫 𝐓𝐫𝐚𝐜𝐤 ✦ {0} ",
]

AYUV = [
    "💌✨ ʜᴇʏ {0} 💞🌸\n\n🎶 ɪ'ᴍ {1} 💖 ʏᴏᴜʀ ᴘᴏᴡᴇʀꜰᴜʟ ᴍᴜꜱɪᴄ ʙᴏᴛ 🎧🔥\n\n┣━━━━━━━━━━━━━━━⧫\n┃ 🌟 ꜱᴛʀᴇᴀᴍ ᴍᴜꜱɪᴄ ɪɴ ᴠᴄ\n┃ 🎵 ʏᴏᴜᴛᴜʙᴇ • ꜱᴘᴏᴛɪꜰʏ • ᴊɪᴏꜱᴀᴀᴠɴ\n┃ ⚡ ꜰᴀꜱᴛ & ꜱᴍᴏᴏᴛʜ ᴘʟᴀʏʙᴀᴄᴋ\n┃ 💫 24x7 ᴍᴜꜱɪᴄ ᴠɪʙᴇꜱ\n┗━━━━━━━━━━━━━━━⧫\n\n💖 ᴊᴜꜱᴛ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ & ꜱᴛᴀʀᴛ ᴛʜᴇ ᴘᴀʀᴛʏ 🎉",

    "🌹✨ ᴡᴇʟᴄᴏᴍᴇ {0} 💕\n\n🎧 {1} ɪꜱ ʜᴇʀᴇ ᴛᴏ ᴍᴀᴋᴇ ʏᴏᴜʀ ᴠᴄ ᴀᴡᴇꜱᴏᴍᴇ 💫🔥\n\n┣━━━━━━━━━━━━━━━⧫\n┃ 🎶 ʜɪɢʜ Qᴜᴀʟɪᴛʏ ᴍᴜꜱɪᴄ\n┃ 🚀 ꜰᴀꜱᴛ ꜱᴛʀᴇᴀᴍɪɴɢ\n┃ 💞 ᴍᴜʟᴛɪ-ᴘʟᴀᴛꜰᴏʀᴍ ꜱᴜᴘᴘᴏʀᴛ\n┃ 🌸 ꜱᴍᴀʀᴛ & ᴇᴀꜱʏ ᴄᴏᴍᴍᴀɴᴅꜱ\n┗━━━━━━━━━━━━━━━⧫\n\n✨ ᴛʏᴘᴇ /play ᴀɴᴅ ᴇɴᴊᴏʏ ɴᴏɴ-ꜱᴛᴏᴘ ᴍᴜꜱɪᴄ 🎵🦋"
]

# ── Runtime structures ──────────────────────────────────────────────────────
BANNED_USERS = filters.user()
adminlist, lyrical, votemode, autoclean, confirmer = {}, {}, {}, [], {}

# ── Minimal validation ──────────────────────────────────────────────────────
if SUPPORT_CHANNEL and not re.match(r"^https?://", SUPPORT_CHANNEL):
    raise SystemExit("[ERROR] - Invalid SUPPORT_CHANNEL URL. Must start with https://")

if SUPPORT_CHAT and not re.match(r"^https?://", SUPPORT_CHAT):
    raise SystemExit("[ERROR] - Invalid SUPPORT_CHAT URL. Must start with https://")

if not COOKIE_URL:
    COOKIE_URL = None

# Cookie link validation
if COOKIE_URL and not re.match(r"^https?://", COOKIE_URL):
    raise SystemExit("[ERROR] - Invalid COOKIE_URL. Must start with http:// or https://")
    
    
print("""
╔════════════════════════════════════╗
║🎵 𝗩𝗜𝗦𝗛𝗔𝗟 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗘𝗗𝗜𝗧𝗜𝗢𝗡  
║       ✦ 𝗖𝗼𝗻𝗳𝗶𝗴 𝗟𝗼𝗮𝗱𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀! ✦   
╚════════════════════════════════════╝
""")

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
