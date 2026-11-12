# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

from VishalMusic.core.bot import VISHAL
from VishalMusic.core.dir import dirr
from VishalMusic.core.git import git
from VishalMusic.core.userbot import Userbot
from VishalMusic.misc import dbb, heroku

from .logging import LOGGER

try:
    import shutil
    if not shutil.which("ffprobe") or not shutil.which("ffmpeg"):
        import static_ffmpeg
        static_ffmpeg.add_paths()
except Exception:
    pass

dirr()
git()
dbb()
heroku()



app = VISHAL()
userbot = Userbot()

# ── Kurigram mention fix ──────────────────────────────────────
# Kurigram ka User.mention bina quotes ka anchor banata hai:
#     <a href=tg://user?id=123>Name</a>
# Telegram Bot API usse parse nahi kar pata ("Unexpected end of name
# token") → Bot API path fail → buttons colorless fallback me jaate
# hain. Isliye mention ko QUOTED anchor ke saath override karte hain.

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════





try:
    from pyrogram.types import User as _KurigramUser

    def _quoted_mention(self):


        name = self.first_name or "Deleted Account"
        return f'<a href="tg://user?id={self.id}">{name}</a>'

    _KurigramUser.mention = property(_quoted_mention)
    LOGGER("VishalMusic").info("✔ mention HTML quote fix applied")
except Exception as _e:
    LOGGER("VishalMusic").warning(f"mention fix failed: {_e}")


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
