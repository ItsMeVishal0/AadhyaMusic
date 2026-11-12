# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import random
from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message
import config
from VishalMusic import app
from VishalMusic.core.call import VISHAL
from VishalMusic.utils import bot_sys_stats
from VishalMusic.utils.decorators.language import language
from VishalMusic.utils.colored_buttons import (
    buttons_to_inline_markup,
    smart_send_photo as send_photo_colored,
    smart_edit_message_caption as edit_message_caption_colored,
)
from VishalMusic.utils.inline import supp_markup
from config import BANNED_USERS




@app.on_message(filters.command("ping", prefixes=["/"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    start = datetime.now()
    ping_photo = random.choice(config.START_IMGS)
    response = await message.reply_photo(
        photo=ping_photo,
        caption=_["ping_1"].format(app.mention),
    )

    pytgping = await VISHAL.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    await edit_message_caption_colored(
        chat_id=response.chat.id,
        message_id=response.id,
        caption=_["ping_2"].format(resp, app.mention, UP, RAM, CPU, DISK, pytgping),
        reply_markup=supp_markup(_),
    )

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
