# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ParseMode
from VishalMusic import app
import config

@app.on_message(filters.command("privacy"))
async def privacy(client, message: Message):
    bot_mention = getattr(app, "mention", config.BOT_NAME)
    text = f"""
🔒 **Privacy Policy for {bot_mention} !**

Your privacy is important to us. To learn more about how we collect, use, and protect your data, please review our Privacy Policy here: [Privacy Policy]({config.PRIVACY_LINK}).

If you have any questions or concerns, feel free to reach out to our [support team](https://t.me/ItsMeVishalBots).
"""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📜 ᴠɪᴇᴡ ᴘʀɪᴠᴀᴄʏ ᴘᴏʟɪᴄʏ", url=config.PRIVACY_LINK
                )
            ]
        ]
    )

    await message.reply_text(
        text, 
        reply_markup=keyboard, 
        parse_mode=ParseMode.MARKDOWN, 
        disable_web_page_preview=True
    )

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
