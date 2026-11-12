# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import math
from VishalMusic import app
from VishalMusic.utils.colored_buttons import styled_button

# 14 Clean Music & Management Categories
MUSIC_SECTIONS = [19, 20, 21, 23, 24, 25, 26, 2, 3, 4, 5, 6, 8, 15]
TOTAL_SECTIONS = len(MUSIC_SECTIONS)
ITEMS_PER_PAGE = 7
TOTAL_PAGES = math.ceil(TOTAL_SECTIONS / ITEMS_PER_PAGE)

HELP_BUTTON_TITLES = {
    19: "📈 ᴘɪηɢ",
    20: "🎵 ᴘʟʌʏ",
    21: "⊕ ʀєᴘσ",
    23: "⏩ sєєᴋ",
    24: "⇌ sʜᴜғғʟє",
    25: "♬ sσηɢ",
    26: "⚡ sᴘєєᴅ",
    2: "👥 ʌᴅᴍɪη",
    3: "⊞ ʌᴜᴛʜ",
    4: "⌬ ʙʟ-ᴄʜʌᴛ",
    5: "⊘ ʙʟ-ᴜsєʀ",
    6: "♫ ᴄ-ᴘʟʌʏ",
    8: "⊗ ɢ-ʙʌη",
    15: "⟳ ʟσσᴘ",
}

# Alternate button colors across green (success), blue (primary), and red (danger)
_STYLE_CYCLE = ["success", "primary", "danger"]


def help_p_panel(_, current_page: int = 1):
    """
    Return category buttons arranged in exactly 4 lines:
    Row 1: [ 3 Buttons ] (Ping, Play, Repo)
    Row 2: [ 2 Buttons ] (Seek, Shuffle)
    Row 3: [ 2 Buttons ] (Song, Speed)
    Row 4: Navigation: [ ⬅️ ʙʌᴄᴋ ] [ 🏠 ᴍєηᴜ ] [ ➡️ ηєxᴛ ] [ ✘ ᴄʟσsє ]
    """
    start = (current_page - 1) * ITEMS_PER_PAGE
    end = min(current_page * ITEMS_PER_PAGE, TOTAL_SECTIONS)
    items = MUSIC_SECTIONS[start:end]

    buttons = []
    idx = 0

    # Exactly 3 category rows (3 + 2 + 2 = 7 items)
    row_counts = [3, 2, 2]
    for count in row_counts:
        row = []
        for _i in range(count):
            if idx < len(items):
                num = items[idx]
                style = _STYLE_CYCLE[idx % len(_STYLE_CYCLE)]
                btn_text = _[f"H_B_{num}"] if isinstance(_, dict) and f"H_B_{num}" in _ else HELP_BUTTON_TITLES.get(num, f"Category {num}")
                row.append(
                    styled_button(
                        text=btn_text,
                        callback_data=f"help_callback hb{num}_p{current_page}",
                        style=style,
                    )
                )
                idx += 1
        if row:
            buttons.append(row)

    # Row 4: Navigation Row
    prev_page = TOTAL_PAGES if current_page <= 1 else current_page - 1
    next_page = 1 if current_page >= TOTAL_PAGES else current_page + 1

    close_btn = _["CLOSE_BUTTON"] if isinstance(_, dict) and "CLOSE_BUTTON" in _ else "✘ ᴄʟσsє"

    buttons.append([
        styled_button(text="⬅️ ʙʌᴄᴋ", callback_data=f"help_page {prev_page}", style="primary"),
        styled_button(text="🏠 ᴍєηᴜ", callback_data="back_to_main", style="primary"),
        styled_button(text="➡️ ηєxᴛ", callback_data=f"help_page {next_page}", style="success"),
        styled_button(text=close_btn, callback_data="close", style="danger"),
    ])

    return buttons


def first_page(_):
    return help_p_panel(_, 1)


def second_page(_):
    return help_p_panel(_, 2)


def help_back_markup(_, current_page: int = 1):
    close_btn = _["CLOSE_BUTTON"] if isinstance(_, dict) and "CLOSE_BUTTON" in _ else "✘ ᴄʟσsє"
    return [
        [
            styled_button(text="⬅️ ʙʌᴄᴋ", callback_data=f"help_page {current_page}", style="primary"),
            styled_button(text="🏠 ᴍєηᴜ", callback_data="back_to_main", style="success"),
            styled_button(text=close_btn, callback_data="close", style="danger"),
        ]
    ]


def private_help_panel(_):
    return [
        [
            styled_button(text=_["S_B_3"], url=f"https://t.me/{app.username}?start=help", style="success"),
        ],
    ]
