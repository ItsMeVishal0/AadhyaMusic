# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import time
from typing import Dict, List, Optional, Union

import config
from VishalMusic.utils.colored_buttons import styled_button
from VishalMusic.utils.formatters import time_to_seconds

LAST_UPDATE_TIME = {}
UPDATE_INTERVAL = 3  # Fast 3s live color & progress updates


def should_update_progress(chat_id):
    now = time.time()
    last = LAST_UPDATE_TIME.get(chat_id, 0)
    if now - last >= (UPDATE_INTERVAL - 0.5):
        LAST_UPDATE_TIME[chat_id] = now
        return True
    return False


def get_dynamic_control_styles() -> tuple:
    """
    Synchronized dynamic color cycling for all 5 control buttons:
    • ▷  (Resume) : success -> primary -> danger
    • ❚❚ (Pause)  : danger -> success -> primary
    • ↺  (Replay) : primary -> danger -> success
    • ▷▷ (Skip)    : success -> primary -> danger
    • ◼  (Stop)   : danger -> success -> primary
    """
    palette = [
        ("success", "danger", "primary", "success", "danger"),
        ("primary", "success", "danger", "primary", "success"),
        ("danger", "primary", "success", "danger", "primary"),
    ]
    index = int(time.time() // 1.5) % len(palette)
    return palette[index]


def get_replay_button_style() -> str:
    """Backward compatibility alias."""
    return get_dynamic_control_styles()[2]


def generate_progress_bar(played_sec, duration_sec):
    if duration_sec <= 0:
        percentage = 0
    else:
        percentage = min((played_sec / duration_sec) * 100, 100)
    total_bars = 10
    pos = min(int(round((total_bars - 1) * (percentage / 100))), total_bars - 1)
    pos = max(pos, 0)
    left = "—" * pos
    right = "—" * (total_bars - 1 - pos)
    return f"{left}♡{right}"


def control_buttons(_, chat_id):
    """Playback control row with pure symbols (▷, ❚❚, ↺, ▷▷, ◼) and synchronized dynamic colors on all buttons."""
    resume_style, pause_style, replay_style, skip_style, stop_style = get_dynamic_control_styles()
    return [[
        styled_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style=resume_style),
        styled_button("❚❚", callback_data=f"ADMIN Pause|{chat_id}", style=pause_style),
        styled_button("↺", callback_data=f"ADMIN Replay|{chat_id}", style=replay_style),
        styled_button("▷▷", callback_data=f"ADMIN Skip|{chat_id}", style=skip_style),
        styled_button("◼", callback_data=f"ADMIN Stop|{chat_id}", style=stop_style),
    ]]


def autoplay_button(chat_id: int, status: bool) -> dict:
    """Autoplay toggle - clean symbols (⟳), green when ON, red when OFF."""
    if status:
        return styled_button(
            "⟳ AUTOPLAY : ON",
            callback_data=f"AUTOPLAY_TOGGLE {chat_id}",
            style="success",
        )
    return styled_button(
        "⟳ AUTOPLAY : OFF",
        callback_data=f"AUTOPLAY_TOGGLE {chat_id}",
        style="danger",
    )


def bottom_row(_, chat_id: int, autoplay_status: bool = False):
    """Bottom row: [ ⟳ AUTOPLAY : ON/OFF ] | [ ✕ CLOSE ]"""
    return [[
        autoplay_button(chat_id, autoplay_status),
        styled_button("✕ CLOSE", callback_data="close", style="danger"),
    ]]


# Colored aliases (kept for callers that already use the "colored_" name)
colored_control_buttons = control_buttons
colored_autoplay_button = autoplay_button


def track_markup(_, videoid, user_id, channel, fplay):
    """Audio/Video pick after a track search — colored."""
    return [
        [
            styled_button(
                _["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style="primary",
            ),
            styled_button(
                _["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style="success",
            ),
        ],
        [
            styled_button(
                "✖ CLOSE",
                callback_data=f"forceclose {videoid}|{user_id}",
                style="danger",
            )
        ],
    ]


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    """Playlist Audio/Video pick — colored."""
    return [
        [
            styled_button(
                _["P_B_1"],
                callback_data=f"VishalPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
                style="primary",
            ),
            styled_button(
                _["P_B_2"],
                callback_data=f"VishalPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
                style="success",
            ),
        ],
        [
            styled_button(
                "✖ CLOSE",
                callback_data=f"forceclose {videoid}|{user_id}",
                style="danger",
            ),
        ],
    ]


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    """Livestream single-button — colored."""
    return [
        [
            styled_button(
                _["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
                style="success",
            )
        ],
        [
            styled_button(
                "✖ CLOSE",
                callback_data=f"forceclose {videoid}|{user_id}",
                style="danger",
            )
        ],
    ]


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    """Search results slider with nav arrows — colored."""
    short_query = query[:20]
    return [
        [
            styled_button(
                _["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style="primary",
            ),
            styled_button(
                _["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style="success",
            ),
        ],
        [
            styled_button(
                "◁",
                callback_data=f"slider B|{query_type}|{short_query}|{user_id}|{channel}|{fplay}",
                style="primary",
            ),
            styled_button(
                "✖ CLOSE",
                callback_data=f"forceclose {short_query}|{user_id}",
                style="danger",
            ),
            styled_button(
                "▷",
                callback_data=f"slider F|{query_type}|{short_query}|{user_id}|{channel}|{fplay}",
                style="primary",
            ),
        ],
    ]


def stream_markup(_, chat_id, played: str = "00:00", dur: str = "00:00", autoplay_status: bool = False):
    """Now Playing keyboard matching single indicator progress bar."""
    try:
        played_sec = time_to_seconds(str(played)) if str(played) != "-" else 0
        duration_sec = time_to_seconds(str(dur)) if str(dur) != "-" else 0
        bar = generate_progress_bar(played_sec, duration_sec)
    except Exception:
        bar = "♡—————————"
    
    played_display = "00:00" if (not played or played == "-") else str(played)
    dur_display = "00:00" if (not dur or dur == "-") else str(dur)

    return (
        [[styled_button(f"{played_display} {bar} {dur_display}", callback_data="GetTimer", style="primary")]]
        + control_buttons(_, chat_id)
        + bottom_row(_, chat_id, autoplay_status)
    )


def stream_markup_timer(_, chat_id, played, dur, autoplay_status: bool = False):
    """Now Playing keyboard with live progress bar."""
    if not should_update_progress(chat_id):
        return None

    try:
        played_sec = time_to_seconds(str(played)) if str(played) != "-" else 0
        duration_sec = time_to_seconds(str(dur)) if str(dur) != "-" else 0
        bar = generate_progress_bar(played_sec, duration_sec)
    except Exception:
        bar = "—————————————"

    played_display = "00:00" if (not played or played == "-") else str(played)
    dur_display = "00:00" if (not dur or dur == "-") else str(dur)

    return (
        [[styled_button(
            f"{played_display} {bar} {dur_display}",
            callback_data="GetTimer",
            style="primary",
        )]]
        + control_buttons(_, chat_id)
        + bottom_row(_, chat_id, autoplay_status)
    )


# Colored aliases (kept for callers already using the "colored_" name)
colored_stream_markup = stream_markup
colored_stream_markup_timer = stream_markup_timer

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
