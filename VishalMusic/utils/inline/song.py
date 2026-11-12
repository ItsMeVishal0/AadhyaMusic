# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

from typing import List, Dict
from VishalMusic.utils.colored_buttons import styled_button


def song_main_markup(_, vidid: str) -> List[List[Dict]]:
    """Step 1: Choose Audio or Video with primary, success, danger buttons."""
    return [
        [
            styled_button(text="🎵 ᴀᴜᴅɪᴏ", callback_data=f"song_menu audio|{vidid}", style="success"),
            styled_button(text="🎬 ᴠɪᴅᴇᴏ", callback_data=f"song_menu video|{vidid}", style="primary"),
        ],
        [
            styled_button(text="🗑️ ᴄʟᴏsᴇ", callback_data="close", style="danger"),
        ],
    ]


def audio_quality_markup(_, vidid: str) -> List[List[Dict]]:
    """Step 2A: Select Audio Quality."""
    return [
        [
            styled_button(text="🎵 320 ᴋʙᴘs (ʜǫ)", callback_data=f"song_dl audio|320|{vidid}", style="success"),
        ],
        [
            styled_button(text="🎵 192 ᴋʙᴘs (ᴍǫ)", callback_data=f"song_dl audio|192|{vidid}", style="primary"),
            styled_button(text="🎵 128 ᴋʙᴘs (ʟǫ)", callback_data=f"song_dl audio|128|{vidid}", style="primary"),
        ],
        [
            styled_button(text="🔙 ʙᴀᴄᴋ", callback_data=f"song_back main|{vidid}", style="primary"),
            styled_button(text="🗑️ ᴄʟᴏsᴇ", callback_data="close", style="danger"),
        ],
    ]


def video_quality_markup(_, vidid: str) -> List[List[Dict]]:
    """Step 2B: Select Video Quality."""
    return [
        [
            styled_button(text="🎬 1080ᴘ (ғʜᴅ)", callback_data=f"song_dl video|1080|{vidid}", style="success"),
            styled_button(text="🎬 720ᴘ (ʜᴅ)", callback_data=f"song_dl video|720|{vidid}", style="success"),
        ],
        [
            styled_button(text="🎬 480ᴘ (sᴅ)", callback_data=f"song_dl video|480|{vidid}", style="primary"),
            styled_button(text="🎬 360ᴘ (ʟᴏᴡ)", callback_data=f"song_dl video|360|{vidid}", style="primary"),
        ],
        [
            styled_button(text="🎬 ʙᴇsᴛ ǫᴜᴀʟɪᴛʏ", callback_data=f"song_dl video|best|{vidid}", style="primary"),
        ],
        [
            styled_button(text="🔙 ʙᴀᴄᴋ", callback_data=f"song_back main|{vidid}", style="primary"),
            styled_button(text="🗑️ ᴄʟᴏsᴇ", callback_data="close", style="danger"),
        ],
    ]


# Alias for backward compatibility
song_markup = song_main_markup
