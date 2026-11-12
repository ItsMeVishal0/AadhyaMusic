# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import config
from VishalMusic import app
from VishalMusic.utils.colored_buttons import styled_button


def _get_bot_username() -> str:
    return getattr(app, "username", "") or getattr(config, "BOT_USERNAME", "") or "AadhyaMusiic_bot"


def _get_owner_url() -> str:
    owner_username = (getattr(config, "OWNER_USERNAME", "") or "").strip().lstrip("@")
    if owner_username:
        return f"https://t.me/{owner_username}"
    if getattr(config, "SUPPORT_CHAT", None):
        return config.SUPPORT_CHAT
    return "https://t.me/ItsMeVishalBots"


def start_panel(_=None):
    # Group start panel buttons
    bot_uname = _get_bot_username()
    buttons = [
        [
            styled_button(
                text="➕ ʌᴅᴅ мє ιη үσυʀ ɢʀσυᴘ ➕",
                url=f"https://t.me/{bot_uname}?startgroup=true",
                style="danger",
            ),
        ],
        [
            styled_button(
                text="🛠️ sᴜᴘᴘᴏʀᴛ",
                url=config.SUPPORT_CHAT or "https://t.me/ItsMeVishalBots",
                style="primary",
            ),
            styled_button(
                text="🌀 ᴜᴘᴅʌᴛєs",
                url=config.SUPPORT_CHANNEL or "https://t.me/ItsMeVishalBots",
                style="primary",
            ),
        ],
    ]
    return buttons


async def private_panel(_=None):
    # Exact button layout:
    # Row 1: [ ➕ ʌᴅᴅ мє ιη үσυʀ ɢʀσυᴘ ➕ ] (Red / Danger)
    # Row 2: [ 📚 ʜєʟᴘ ʌηᴅ cσммʌηᴅs ] (Red / Danger)
    # Row 3: [ 🛠️ sᴜᴘᴘᴏʀᴛ ] (Blue) | [ 🌀 ᴜᴘᴅʌᴛєs ] (Blue)
    # Row 4: [ 👑 σwηєʀ ] (Green)
    bot_uname = _get_bot_username()
    owner_url = _get_owner_url()

    buttons = [
        [
            styled_button(
                text="➕ ʌᴅᴅ мє ιη үσυʀ ɢʀσυᴘ ➕",
                url=f"https://t.me/{bot_uname}?startgroup=true",
                style="danger",
            ),
        ],
        [
            styled_button(
                text="📚 ʜєʟᴘ ʌηᴅ cσммʌηᴅs",
                callback_data="open_help",
                style="danger",
            ),
        ],
        [
            styled_button(
                text="🛠️ sᴜᴘᴘᴏʀᴛ",
                url=config.SUPPORT_CHAT or "https://t.me/ItsMeVishalBots",
                style="primary",
            ),
            styled_button(
                text="🌀 ᴜᴘᴅʌᴛєs",
                url=config.SUPPORT_CHANNEL or "https://t.me/ItsMeVishalBots",
                style="primary",
            ),
        ],
        [
            styled_button(
                text="👑 σwηєʀ",
                url=owner_url,
                style="success",
            ),
        ],
    ]
    return buttons
