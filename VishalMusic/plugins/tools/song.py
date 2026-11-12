# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import os
import re
import asyncio
import subprocess
from pyrogram import filters
from pyrogram.enums import ChatAction
from pyrogram.types import (
    Message,
    CallbackQuery,
)

from VishalMusic import app, YouTube, LOGGER
from VishalMusic.platforms.Youtube import download_audio, download_video
from VishalMusic.utils.colored_buttons import (
    styled_button,
    smart_send_photo,
    smart_send_message,
    smart_edit_message_caption,
    smart_edit_reply_markup,
)
from config import BANNED_USERS, SONG_DOWNLOAD_DURATION_LIMIT, SONG_DOWNLOAD_DURATION
from VishalMusic.utils.decorators.language import language, languageCB
from VishalMusic.utils.errors import capture_err, capture_callback_err
from VishalMusic.utils.formatters import time_to_seconds
from VishalMusic.utils.inline.song import (
    song_main_markup,
    audio_quality_markup,
    video_quality_markup,
)

LOGGER_SONG = LOGGER("VishalMusic.plugins.tools.song")

SONG_COMMANDS = ["song", "music", "mp3", "video", "vsong", "ytmp3", "ytmp4"]


@app.on_message(filters.command(SONG_COMMANDS) & ~BANNED_USERS)
@capture_err
@language
async def song_command_handler(client, message: Message, lang):
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>ᴜsᴀɢᴇ:</b>\n"
            "<code>/song [sᴏɴɢ ɴᴀᴍᴇ ᴏʀ ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋ]</code>"
        )

    mystic = await message.reply_text("🔍 <b>sᴇᴀʀᴄʜɪɴɢ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")

    url = await YouTube.url(message)
    query = url or message.text.split(None, 1)[1]

    try:
        title, dur_min, dur_sec, thumb, vidid = await YouTube.details(query)
    except Exception as e:
        LOGGER_SONG.error(f"Error fetching song details: {e}")
        return await mystic.edit_text("❌ <b>sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɴᴏᴛʜᴇʀ ɴᴀᴍᴇ.</b>")

    if not dur_min:
        return await mystic.edit_text("❌ <b>sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ.</b>")

    if int(dur_sec or 0) > SONG_DOWNLOAD_DURATION_LIMIT:
        return await mystic.edit_text(
            f"❌ <b>ᴛʀᴀᴄᴋ ᴅᴜʀᴀᴛɪᴏɴ ɪs ʟᴏɴɢᴇʀ ᴛʜᴀɴ {SONG_DOWNLOAD_DURATION} ᴍɪɴᴜᴛᴇs.</b>"
        )

    caption = (
        f"🎵 <b>ᴛɪᴛʟᴇ :</b> {title}\n"
        f"⏳ <b>ᴅᴜʀᴀᴛɪᴏɴ :</b> {dur_min} ᴍɪɴ\n\n"
        f"⚡ <b><i>ᴄʜᴏᴏsᴇ ғᴏʀᴍᴀᴛ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ:</i></b>"
    )

    try:
        await mystic.delete()
    except Exception:
        pass

    try:
        if thumb:
            await smart_send_photo(
                chat_id=message.chat.id,
                photo=thumb,
                caption=caption,
                reply_markup=song_main_markup(lang, vidid),
            )
        else:
            await smart_send_message(
                chat_id=message.chat.id,
                text=caption,
                reply_markup=song_main_markup(lang, vidid),
            )
    except Exception as e:
        LOGGER_SONG.error(f"Failed to send song card: {e}")
        await message.reply_text(
            caption,
            reply_markup=song_main_markup(lang, vidid),
        )


@app.on_callback_query(filters.regex(r"song_menu") & ~BANNED_USERS)
@capture_callback_err
@languageCB
async def song_menu_cb(client, cq: CallbackQuery, lang):
    """Step 2: User clicked 🎵 Audio or 🎬 Video -> Show Quality Options."""
    try:
        _ignored, req = cq.data.split(None, 1)
        stype, vidid = req.split("|")

        if stype == "audio":
            caption = (
                "🎵 <b>ᴀᴜᴅɪᴏ ᴅᴏᴡɴʟᴏᴀᴅ</b>\n\n"
                "⚡ <i>sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴘʀᴇғᴇʀʀᴇᴅ ᴀᴜᴅɪᴏ ǫᴜᴀʟɪᴛʏ:</i>"
            )
            markup = audio_quality_markup(lang, vidid)
        else:
            caption = (
                "🎬 <b>ᴠɪᴅᴇᴏ ᴅᴏᴡɴʟᴏᴀᴅ</b>\n\n"
                "⚡ <i>sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴘʀᴇғᴇʀʀᴇᴅ ᴠɪᴅᴇᴏ ǫᴜᴀʟɪᴛʏ:</i>"
            )
            markup = video_quality_markup(lang, vidid)

        await smart_edit_message_caption(
            chat_id=cq.message.chat.id,
            message_id=cq.message.id,
            caption=caption,
            reply_markup=markup,
        )
    except Exception as e:
        LOGGER_SONG.error(f"Error in song_menu_cb: {e}")


@app.on_callback_query(filters.regex(r"song_back") & ~BANNED_USERS)
@capture_callback_err
@languageCB
async def song_back_cb(client, cq: CallbackQuery, lang):
    """Back button: Return to initial format selection screen."""
    try:
        _ignored, req = cq.data.split(None, 1)
        _mode, vidid = req.split("|")

        caption = (
            "🎵 <b>sᴏɴɢ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ</b>\n\n"
            "⚡ <b><i>ᴄʜᴏᴏsᴇ ғᴏʀᴍᴀᴛ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ:</i></b>"
        )
        await smart_edit_message_caption(
            chat_id=cq.message.chat.id,
            message_id=cq.message.id,
            caption=caption,
            reply_markup=song_main_markup(lang, vidid),
        )
    except Exception as e:
        LOGGER_SONG.error(f"Error in song_back_cb: {e}")


@app.on_callback_query(filters.regex(r"song_helper") & ~BANNED_USERS)
@capture_callback_err
@languageCB
async def song_helper_legacy_cb(client, cq: CallbackQuery, lang):
    """Legacy helper fallback."""
    _ignored, req = cq.data.split(None, 1)
    stype, vidid = req.split("|")
    if stype == "video":
        await smart_edit_message_caption(
            chat_id=cq.message.chat.id,
            message_id=cq.message.id,
            caption="🎬 <b>ᴠɪᴅᴇᴏ ᴅᴏᴡɴʟᴏᴀᴅ</b>\n\n⚡ <i>sᴇʟᴇᴄᴛ ᴠɪᴅᴇᴏ ǫᴜᴀʟɪᴛʏ:</i>",
            reply_markup=video_quality_markup(lang, vidid),
        )
    else:
        await smart_edit_message_caption(
            chat_id=cq.message.chat.id,
            message_id=cq.message.id,
            caption="🎵 <b>ᴀᴜᴅɪᴏ ᴅᴏᴡɴʟᴏᴀᴅ</b>\n\n⚡ <i>sᴇʟᴇᴄᴛ ᴀᴜᴅɪᴏ ǫᴜᴀʟɪᴛʏ:</i>",
            reply_markup=audio_quality_markup(lang, vidid),
        )


@app.on_callback_query(filters.regex(r"(song_dl|song_download)") & ~BANNED_USERS)
@capture_callback_err
@languageCB
async def song_download_cb(client, cq: CallbackQuery, lang):
    """Step 3: User selected quality -> Download and deliver file."""
    _ignored, req = cq.data.split(None, 1)
    parts = req.split("|")
    if len(parts) == 3:
        stype, qual, vidid = parts
    elif len(parts) == 2:
        stype, vidid = parts
        qual = "best"
    else:
        return

    await song_download_execute(client, cq, stype, qual, vidid)


async def song_download_execute(client, cq: CallbackQuery, stype: str, qual: str, vidid: str):
    try:
        await cq.answer(f"📥 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ {stype.upper()} ({qual.upper()})...", show_alert=False)
    except Exception:
        pass

    chat_id = cq.message.chat.id
    yturl = f"https://www.youtube.com/watch?v={vidid}"

    try:
        await smart_edit_message_caption(
            chat_id=chat_id,
            message_id=cq.message.id,
            caption=f"⏳ <b>ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ {stype.upper()} ({qual.upper()})...</b>\n\n⚡ <i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</i>",
            reply_markup=None,
        )
    except Exception:
        pass

    file_path = None
    converted_path = None
    try:
        info, _ = await YouTube.track(yturl)
        raw_title = info.get("title") or "Song"
        title = re.sub(r"\s+", " ", re.sub(r"[^\w\s\-\.\(\)\[\]]+", " ", raw_title)).strip()[:200]
        performer = info.get("uploader") or "Vishal Music"
        duration_sec = time_to_seconds(info.get("duration_min")) if info.get("duration_min") else 0

        if stype == "audio":
            await app.send_chat_action(chat_id, ChatAction.UPLOAD_AUDIO)
            file_path = await download_audio(vidid)
            if not file_path or not os.path.exists(file_path):
                raise RuntimeError("Failed to download audio")

            target_file = file_path
            # Optional ffmpeg bitrate optimization if specific rate requested
            if qual in ("128", "192") and file_path.endswith((".mp3", ".webm", ".m4a")):
                try:
                    out_name = os.path.join("downloads", f"{vidid}_{qual}k.mp3")
                    cmd = ["ffmpeg", "-y", "-i", file_path, "-b:a", f"{qual}k", "-vn", out_name]
                    proc = await asyncio.create_subprocess_exec(
                        *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
                    )
                    await proc.wait()
                    if os.path.exists(out_name) and os.path.getsize(out_name) > 0:
                        converted_path = out_name
                        target_file = converted_path
                except Exception as conv_err:
                    LOGGER_SONG.warning(f"Audio bitrate conversion failed, using original: {conv_err}")

            await app.send_audio(
                chat_id=chat_id,
                audio=target_file,
                caption=f"🎵 <b>{title}</b>\n👤 <b>ᴀʀᴛɪsᴛ :</b> {performer}\n⚡ <b>ǫᴜᴀʟɪᴛʏ :</b> {qual.upper()} ᴋʙᴘs",
                title=title,
                performer=performer,
                duration=int(duration_sec),
            )
        else:
            await app.send_chat_action(chat_id, ChatAction.UPLOAD_VIDEO)
            file_path = await download_video(vidid)
            if not file_path or not os.path.exists(file_path):
                raise RuntimeError("Failed to download video")

            target_file = file_path
            # Optional ffmpeg resolution scaling if lower resolution requested
            if qual in ("360", "480") and file_path.endswith(".mp4"):
                try:
                    out_name = os.path.join("downloads", f"{vidid}_{qual}p.mp4")
                    height_val = "360" if qual == "360" else "480"
                    cmd = ["ffmpeg", "-y", "-i", file_path, "-vf", f"scale=-2:{height_val}", "-c:v", "libx264", "-crf", "28", "-preset", "ultrafast", "-c:a", "copy", out_name]
                    proc = await asyncio.create_subprocess_exec(
                        *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
                    )
                    await proc.wait()
                    if os.path.exists(out_name) and os.path.getsize(out_name) > 0:
                        converted_path = out_name
                        target_file = converted_path
                except Exception as conv_err:
                    LOGGER_SONG.warning(f"Video resolution scaling failed, using original: {conv_err}")

            await app.send_video(
                chat_id=chat_id,
                video=target_file,
                caption=f"🎬 <b>{title}</b>\n⚡ <b>ǫᴜᴀʟɪᴛʏ :</b> {qual.upper()}",
                duration=int(duration_sec),
                supports_streaming=True,
            )

        try:
            await cq.message.delete()
        except Exception:
            pass

    except Exception as e:
        LOGGER_SONG.error(f"Download failed for {vidid}: {e}")
        try:
            await smart_edit_message_caption(
                chat_id=chat_id,
                message_id=cq.message.id,
                caption=f"❌ <b>ᴅᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.</b>\n<code>{e}</code>",
                reply_markup=None,
            )
        except Exception:
            pass
    finally:
        for p in (file_path, converted_path):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
