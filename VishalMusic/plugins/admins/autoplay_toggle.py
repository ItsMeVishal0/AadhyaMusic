# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

from pyrogram import filters
from pyrogram.types import CallbackQuery

from VishalMusic import app
from VishalMusic.utils.stream.autoplay import toggle_autoplay
from VishalMusic.utils.decorators import ActualAdminCB
from VishalMusic.utils.colored_buttons import (
    styled_button,
    buttons_to_inline_markup,
    edit_reply_markup_colored,
)
from strings import get_string
from VishalMusic.utils.database import get_lang




from VishalMusic.utils.inline.play import stream_markup


@app.on_callback_query(filters.regex(r"^AUTOPLAY_TOGGLE (.+)$"))
@ActualAdminCB
async def autoplay_toggle_callback(client, callback: CallbackQuery, _):
    try:
        chat_id = int(callback.matches[0].group(1))
    except (IndexError, ValueError):
        return await callback.answer(_["autoplay_5"], show_alert=False)

    new_status = await toggle_autoplay(chat_id)
    alert_text = _["autoplay_3"] if new_status else _["autoplay_4"]

    try:
        new_markup = stream_markup(_, chat_id, autoplay_status=new_status)
        result = await edit_reply_markup_colored(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            reply_markup=new_markup
        )
        if not result:
            await callback.message.edit_reply_markup(
                reply_markup=buttons_to_inline_markup(new_markup)
            )
    except Exception:
        pass

    await callback.answer(alert_text, show_alert=False)

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
