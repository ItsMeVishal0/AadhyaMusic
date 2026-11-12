# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import random
import platform
from sys import version as pyver

import psutil
from pyrogram import __version__ as pyrover
from pyrogram import enums, filters
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InputMediaPhoto, InputMediaVideo, Message
try:
    from pytgcalls import __version__ as pytgver
except Exception:
    try:
        from pytgcalls.__version__ import __version__ as pytgver
    except Exception:
        pytgver = "2.2.8"

import config
from VishalMusic import app
from VishalMusic.core.userbot import assistants


from VishalMusic.misc import SUDOERS, mongodb
from VishalMusic.plugins import ALL_MODULES
from VishalMusic.utils.database import get_served_chats, get_served_users, get_sudoers
from VishalMusic.utils.decorators.language import language, languageCB
from VishalMusic.utils.colored_buttons import (
    buttons_to_inline_markup,
    smart_send_message as send_message_colored,
    smart_edit_message_text as edit_message_text_colored,
    edit_message_media_colored,
)

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════





from VishalMusic.utils.inline.stats import back_stats_buttons, stats_buttons
from config import BANNED_USERS




def _get_stats_img() -> str:
    return random.choice(config.START_IMGS)


def _stats_media_kind() -> str:
    return "photo"


def _stats_input_media(text: str, img_url: str = None):
    img = img_url or _get_stats_img()
    return InputMediaPhoto(media=img, caption=text, parse_mode=enums.ParseMode.HTML)


@app.on_message(filters.command(["stats", "gstats"]) & ~BANNED_USERS)
@language
async def stats_global(client, message: Message, _):
    upl = stats_buttons(_, True if message.from_user.id in SUDOERS else False)
    await send_message_colored(
        chat_id=message.chat.id,
        text=_["gstats_2"].format(app.mention),
        reply_markup=upl,
    )


@app.on_callback_query(filters.regex("stats_back") & ~BANNED_USERS)
@languageCB
async def home_stats(client, CallbackQuery, _):
    upl = stats_buttons(_, True if CallbackQuery.from_user.id in SUDOERS else False)
    await edit_message_text_colored(
        chat_id=CallbackQuery.message.chat.id,
        message_id=CallbackQuery.message.id,
        text=_["gstats_2"].format(app.mention),
        reply_markup=upl,
    )


@app.on_callback_query(filters.regex("TopOverall") & ~BANNED_USERS)
@languageCB
async def overall_stats(client, CallbackQuery, _):
    await CallbackQuery.answer()
    upl = back_stats_buttons(_)
    try:
        await CallbackQuery.answer()
    except:
        pass
    await CallbackQuery.edit_message_text(_["gstats_1"].format(app.mention))
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    text = _["gstats_3"].format(
        app.mention,
        len(assistants),
        len(BANNED_USERS),
        served_chats,
        served_users,
        len(ALL_MODULES),
        len(SUDOERS),
        config.AUTO_LEAVING_ASSISTANT,
        config.DURATION_LIMIT_MIN,
    )
    stats_img = _get_stats_img()
    med = {"type": "photo", "media": stats_img, "caption": text}
    botapi_result = await edit_message_media_colored(chat_id=CallbackQuery.message.chat.id, message_id=CallbackQuery.message.id, media=med, reply_markup=upl)
    if not botapi_result:
        try:
            await CallbackQuery.edit_message_media(media=_stats_input_media(text, stats_img), reply_markup=buttons_to_inline_markup(upl))
        except MessageIdInvalid:
            await CallbackQuery.message.reply_photo(
                photo=stats_img, caption=text, parse_mode=enums.ParseMode.HTML, reply_markup=buttons_to_inline_markup(upl)
            )


@app.on_callback_query(filters.regex("bot_stats_sudo"))
@languageCB
async def bot_stats(client, CallbackQuery, _):
    if CallbackQuery.from_user.id not in SUDOERS:
        return await CallbackQuery.answer(_["gstats_4"], show_alert=True)
    upl = back_stats_buttons(_)
    try:
        await CallbackQuery.answer()
    except:
        pass
    await edit_message_text_colored(chat_id=CallbackQuery.message.chat.id, message_id=CallbackQuery.message.id, text=_["gstats_1"].format(app.mention))
    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    ram = str(round(psutil.virtual_memory().total / (1024.0**3))) + " ɢʙ"
    try:
        cpu_freq = psutil.cpu_freq().current
        if cpu_freq >= 1000:
            cpu_freq = f"{round(cpu_freq / 1000, 2)}ɢʜᴢ"
        else:
            cpu_freq = f"{round(cpu_freq, 2)}ᴍʜᴢ"
    except:
        cpu_freq = "ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ"
    hdd = psutil.disk_usage("/")
    total = hdd.total / (1024.0**3)
    used = hdd.used / (1024.0**3)
    free = hdd.free / (1024.0**3)
    call = await mongodb.command("dbstats")
    datasize = call["dataSize"] / 1024
    storage = call["storageSize"] / 1024
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    text = _["gstats_5"].format(
        app.mention,
        len(ALL_MODULES),
        platform.system(),
        ram,
        p_core,
        t_core,
        cpu_freq,
        pyver.split()[0],
        pyrover,
        pytgver,
        str(total)[:4],
        str(used)[:4],
        str(free)[:4],
        served_chats,
        served_users,
        len(BANNED_USERS),
        len(await get_sudoers()),
        str(datasize)[:6],
        storage,
        call["collections"],
        call["objects"],
    )
    stats_img = _get_stats_img()
    med = {"type": "photo", "media": stats_img, "caption": text}
    botapi_result = await edit_message_media_colored(chat_id=CallbackQuery.message.chat.id, message_id=CallbackQuery.message.id, media=med, reply_markup=upl)
    if not botapi_result:
        try:
            await CallbackQuery.edit_message_media(media=_stats_input_media(text, stats_img), reply_markup=buttons_to_inline_markup(upl))
        except MessageIdInvalid:
            await CallbackQuery.message.reply_photo(
                photo=stats_img, caption=text, parse_mode=enums.ParseMode.HTML, reply_markup=buttons_to_inline_markup(upl)
            )

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
