# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import asyncio
import re
import time
import uuid
from typing import Dict, List, Optional, Tuple

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ParseMode
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import SUPPORT_CHAT, adminlist
from VishalMusic import app
from VishalMusic.misc import SUDOERS
from VishalMusic.utils.colored_buttons import (
    buttons_to_inline_markup,
    send_message_colored,
    smart_send_media,
    smart_send_message,
    smart_send_photo,
    styled_button,
)
from VishalMusic.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from VishalMusic.utils.decorators.language import language
from VishalMusic.utils.formatters import alpha_to_int

IS_BROADCASTING = False
PENDING_BROADCASTS: Dict[str, dict] = {}


def _extract_broadcast_data(text: str) -> Tuple[dict, str, Optional[str], List[List[Dict]]]:
    """Parse target flags, control flags, photo url, button definitions,
    and clean message body.

    Supported Syntax & Examples:
      - /broadcast -user -assistant -pin -btn [ᴍᴇssᴀɢᴇ]/BUTTON/https://example.com
      - /broadcast -group -assistant -pin -btn [ᴍᴇssᴀɢᴇ]/BUTTON/https://example.com
      - /broadcast -user -pin -btn [ᴍᴇssᴀɢᴇ]/BUTTON/https://example.com
      - /broadcast -user -assistant -pin -btn [ᴍᴇssᴀɢᴇ]
      - /broadcast -all -pin -btn [ᴍᴇssᴀɢᴇ]
      - /broadcast -all -pin [ᴍᴇssᴀɢᴇ]/Join/https://t.me/channel/Support/https://t.me/support
      - /broadcast -btn/Website/https://example.com Hello world
    """
    if not text:
        text = ""

    flags = {
        "pin": bool(re.search(r"(?i)(?:^|\s)-pin\b(?!\w)", text)) and not bool(re.search(r"(?i)(?:^|\s)-pinloud\b", text)),
        "pinloud": bool(re.search(r"(?i)(?:^|\s)-pinloud\b", text)),
        "nobot": bool(re.search(r"(?i)(?:^|\s)-nobot\b", text)),
        "forward": bool(re.search(r"(?i)(?:^|\s)-forward\b", text)),
        "groups": False,
        "users": False,
        "assistant": False,
    }

    if re.search(r"(?i)(?:^|\s)-(?:all|allchats)\b", text):
        flags["groups"] = True
        flags["users"] = True
    if re.search(r"(?i)(?:^|\s)-(?:group|groups|gc|chat|chats|wfchat)\b", text):
        flags["groups"] = True
    if re.search(r"(?i)(?:^|\s)-(?:user|users|pm|wfuser)\b", text):
        flags["users"] = True
    if re.search(r"(?i)(?:^|\s)-(?:assistant|assistaint|ass)\b", text):
        flags["assistant"] = True

    # Photo URL extraction
    photo = None
    m_photo = re.search(r"(?i)(?:^|\s)-photo\s+(https?://\S+)", text)
    if m_photo:
        photo = m_photo.group(1).strip()
        text = text[:m_photo.start()] + " " + text[m_photo.end():]

    # Remove target and control flags from text
    flag_pattern = r"(?i)(?:^|\s)-(?:pinloud|pin|nobot|forward|all|allchats|groups?|gc|chats?|wfchat|users?|pm|wfuser|assistaint|assistant|ass)\b"
    cleaned = re.sub(flag_pattern, " ", text).strip()

    buttons: List[List[Dict]] = []

    def add_btn(label: str, url: str):
        label = label.strip().strip("\"").strip("'")
        url = url.strip().strip("\"").strip("'")
        if label and url.startswith(("http://", "https://")):
            if not any(b.get("text") == label and b.get("url") == url for row in buttons for b in row):
                buttons.append([styled_button(label, url=url, style="primary")])

    # 1. Parse explicit -btn/Label/URL or -btn "Label|URL" or -btn Label|URL
    while True:
        m = re.search(r"(?i)(?:^|\s)-btn\/([^\s\n\r]+)", cleaned)
        if not m:
            break
        spec = "/" + m.group(1).strip()
        cleaned = cleaned[:m.start()] + " " + cleaned[m.end():]
        slash_matches = list(re.finditer(r"(?:^|\/)\s*([^\/\n]+?)\s*\/\s*(https?:\/\/[^\s]+?)(?=\s*\/[^\/\n]+\/https?:|\s*$)", spec))
        for sm in slash_matches:
            add_btn(sm.group(1), sm.group(2))

    while True:
        m = re.search(r"(?i)(?:^|\s)-btn\s+(\"[^\"]+\"|[^\s]+)\s*\|\s*(https?:\/\/\S+)", cleaned)
        if not m:
            break
        label = m.group(1).strip()
        url = m.group(2).strip()
        cleaned = cleaned[:m.start()] + " " + cleaned[m.end():]
        add_btn(label, url)

    # Remove any leftover standalone -btn flags
    cleaned = re.sub(r"(?i)(?:^|\s)-btn\b", " ", cleaned).strip()

    # 2. Check for [Message]/Button/URL or [Message]
    m_bracket = re.search(r"\[(.*?)\](.*)$", cleaned, re.DOTALL)
    if m_bracket:
        msg_body = m_bracket.group(1).strip()
        slash_part = m_bracket.group(2).strip()
        if slash_part:
            slash_matches = list(re.finditer(r"(?:^|\/)\s*([^\/\n]+?)\s*\/\s*(https?:\/\/[^\s]+?)(?=\s*\/[^\/\n]+\/https?:|\s*$)", slash_part if slash_part.startswith("/") else "/" + slash_part))
            for sm in slash_matches:
                add_btn(sm.group(1), sm.group(2))
    else:
        # Check if message contains /Label/https://... at the end or inline
        slash_matches = list(re.finditer(r"\/\s*([^\/\n]+?)\s*\/\s*(https?:\/\/[^\s]+?)(?=\s*\/[^\/\n]+\/https?:|\s*$)", cleaned))
        if slash_matches:
            first_start = slash_matches[0].start()
            msg_body = cleaned[:first_start].strip()
            for sm in slash_matches:
                add_btn(sm.group(1), sm.group(2))
        else:
            msg_body = cleaned.strip()

    return flags, msg_body, photo, buttons


async def _execute_broadcast(
    target_groups: bool,
    target_users: bool,
    target_assistant: bool,
    query: str,
    photo: Optional[str],
    buttons: List[List[Dict]],
    reply_msg: Optional[Message],
    flags: dict,
    status_msg: Message,
):
    global IS_BROADCASTING
    IS_BROADCASTING = True
    start_time = time.time()

    is_forward = flags.get("forward", False)
    is_pin = flags.get("pin", False)
    is_pinloud = flags.get("pinloud", False)
    no_bot = flags.get("nobot", False)

    async def _send_single_target(target_id: int):
        if is_forward and reply_msg:
            return await app.forward_messages(
                chat_id=target_id,
                from_chat_id=reply_msg.chat.id,
                message_ids=reply_msg.id,
            )
        if photo:
            return await smart_send_photo(
                chat_id=target_id,
                photo=photo,
                caption=query or (reply_msg.caption if reply_msg else None),
                reply_markup=buttons or None,
            )
        if reply_msg:
            caption_text = query or reply_msg.caption
            if reply_msg.photo:
                return await smart_send_photo(
                    chat_id=target_id,
                    photo=reply_msg.photo.file_id,
                    caption=caption_text,
                    reply_markup=buttons or None,
                )
            if reply_msg.video:
                return await smart_send_media(
                    chat_id=target_id,
                    method="sendVideo",
                    media_field="video",
                    media_value=reply_msg.video.file_id,
                    caption=caption_text,
                    reply_markup=buttons or None,
                )
            if reply_msg.document:
                return await smart_send_media(
                    chat_id=target_id,
                    method="sendDocument",
                    media_field="document",
                    media_value=reply_msg.document.file_id,
                    caption=caption_text,
                    reply_markup=buttons or None,
                )
            if reply_msg.audio:
                return await smart_send_media(
                    chat_id=target_id,
                    method="sendAudio",
                    media_field="audio",
                    media_value=reply_msg.audio.file_id,
                    caption=caption_text,
                    reply_markup=buttons or None,
                )
            if reply_msg.animation:
                return await smart_send_media(
                    chat_id=target_id,
                    method="sendAnimation",
                    media_field="animation",
                    media_value=reply_msg.animation.file_id,
                    caption=caption_text,
                    reply_markup=buttons or None,
                )
            if reply_msg.voice:
                return await smart_send_media(
                    chat_id=target_id,
                    method="sendVoice",
                    media_field="voice",
                    media_value=reply_msg.voice.file_id,
                    caption=caption_text,
                    reply_markup=buttons or None,
                )
            if reply_msg.sticker:
                return await app.send_sticker(
                    chat_id=target_id,
                    sticker=reply_msg.sticker.file_id,
                )
            if buttons:
                return await smart_send_message(
                    chat_id=target_id,
                    text=query or reply_msg.text or reply_msg.caption or "\u200b",
                    reply_markup=buttons,
                )
            if not query:
                return await reply_msg.copy(target_id)
            return await smart_send_message(
                chat_id=target_id,
                text=query,
                reply_markup=buttons or None,
            )

        if buttons:
            return await smart_send_message(
                chat_id=target_id,
                text=query or "\u200b",
                reply_markup=buttons,
            )
        return await app.send_message(target_id, text=query or "📢")

    chats_sent = 0
    chats_failed = 0
    chats_pinned = 0
    users_sent = 0
    users_failed = 0
    total_chats = 0
    total_users = 0
    last_edit_time = 0

    # 1. Broadcast to Groups
    if target_groups and not no_bot:
        try:
            served_chats = await get_served_chats()
            chat_ids = [int(c["chat_id"]) for c in served_chats]
            total_chats = len(chat_ids)
            await status_msg.edit_text(
                f"🚀 <b>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴛᴏ ɢʀᴏᴜᴘs...</b>\n\n"
                f"🎯 <b>ᴛᴀʀɢᴇᴛ :</b> {total_chats} ɢʀᴏᴜᴘs\n"
                f"✅ <b>sᴜᴄᴄᴇss :</b> 0\n"
                f"❌ <b>ғᴀɪʟᴇᴅ :</b> 0\n"
                f"📊 <b>ᴘʀᴏɢʀᴇss :</b> 0%\n"
                f"⏳ <i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</i>"
            )
            for idx, cid in enumerate(chat_ids, 1):
                try:
                    m = await _send_single_target(cid)
                    if m:
                        chats_sent += 1
                        if is_pin or is_pinloud:
                            try:
                                await m.pin(disable_notification=not is_pinloud)
                                chats_pinned += 1
                            except Exception:
                                pass
                    else:
                        chats_failed += 1
                except FloodWait as fw:
                    wait_time = int(fw.value)
                    if wait_time > 60:
                        chats_failed += 1
                        continue
                    await asyncio.sleep(wait_time)
                    try:
                        m = await _send_single_target(cid)
                        if m:
                            chats_sent += 1
                        else:
                            chats_failed += 1
                    except Exception:
                        chats_failed += 1
                except Exception:
                    chats_failed += 1

                now = time.time()
                if now - last_edit_time >= 3 or idx == total_chats:
                    last_edit_time = now
                    pct = round((idx / total_chats) * 100) if total_chats else 100
                    try:
                        await status_msg.edit_text(
                            f"🚀 <b>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴛᴏ ɢʀᴏᴜᴘs...</b>\n\n"
                            f"🎯 <b>ᴛᴀʀɢᴇᴛ :</b> {total_chats} ɢʀᴏᴜᴘs\n"
                            f"✅ <b>sᴜᴄᴄᴇss :</b> {chats_sent}\n"
                            f"❌ <b>ғᴀɪʟᴇᴅ :</b> {chats_failed}\n"
                            f"📊 <b>ᴘʀᴏɢʀᴇss :</b> {pct}%\n"
                            f"⏳ <i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</i>"
                        )
                    except Exception:
                        pass
                await asyncio.sleep(0.15)
        except Exception:
            pass

    # 2. Broadcast to Users
    if target_users and not no_bot:
        try:
            served_users = await get_served_users()
            user_ids = [int(u["user_id"]) for u in served_users]
            total_users = len(user_ids)
            await status_msg.edit_text(
                f"🚀 <b>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴛᴏ ᴜsᴇʀs...</b>\n\n"
                f"🎯 <b>ᴛᴀʀɢᴇᴛ :</b> {total_users} ᴜsᴇʀs\n"
                f"✅ <b>sᴜᴄᴄᴇss :</b> 0\n"
                f"❌ <b>ғᴀɪʟᴇᴅ :</b> 0\n"
                f"📊 <b>ᴘʀᴏɢʀᴇss :</b> 0%\n"
                f"⏳ <i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</i>"
            )
            for idx, uid in enumerate(user_ids, 1):
                try:
                    m = await _send_single_target(uid)
                    if m:
                        users_sent += 1
                    else:
                        users_failed += 1
                except FloodWait as fw:
                    wait_time = int(fw.value)
                    if wait_time > 60:
                        users_failed += 1
                        continue
                    await asyncio.sleep(wait_time)
                    try:
                        m = await _send_single_target(uid)
                        if m:
                            users_sent += 1
                        else:
                            users_failed += 1
                    except Exception:
                        users_failed += 1
                except (UserIsBlocked, InputUserDeactivated):
                    users_failed += 1
                except Exception:
                    users_failed += 1

                now = time.time()
                if now - last_edit_time >= 3 or idx == total_users:
                    last_edit_time = now
                    pct = round((idx / total_users) * 100) if total_users else 100
                    try:
                        await status_msg.edit_text(
                            f"🚀 <b>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴛᴏ ᴜsᴇʀs...</b>\n\n"
                            f"🎯 <b>ᴛᴀʀɢᴇᴛ :</b> {total_users} ᴜsᴇʀs\n"
                            f"✅ <b>sᴜᴄᴄᴇss :</b> {users_sent}\n"
                            f"❌ <b>ғᴀɪʟᴇᴅ :</b> {users_failed}\n"
                            f"📊 <b>ᴘʀᴏɢʀᴇss :</b> {pct}%\n"
                            f"⏳ <i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</i>"
                        )
                    except Exception:
                        pass
                await asyncio.sleep(0.15)
        except Exception:
            pass

    # 3. Broadcast to Assistants
    assistant_stats = ""
    if target_assistant:
        from VishalMusic.core.userbot import assistants

        await status_msg.edit_text(
            f"🤖 <b>sᴛᴀʀᴛɪɴɢ ᴀssɪsᴛᴀɴᴛ ʙʀᴏᴀᴅᴄᴀsᴛ...</b>\n⏳ <i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</i>"
        )
        for num in assistants:
            ass_sent = 0
            ass_failed = 0
            try:
                client = await get_client(num)
                async for dialog in client.get_dialogs():
                    try:
                        m = None
                        if is_forward and reply_msg:
                            m = await client.forward_messages(
                                chat_id=dialog.chat.id,
                                from_chat_id=reply_msg.chat.id,
                                message_ids=reply_msg.id,
                            )
                        elif photo:
                            try:
                                m = await client.send_photo(
                                    dialog.chat.id,
                                    photo,
                                    caption=query or (reply_msg.caption if reply_msg else None),
                                    reply_markup=buttons_to_inline_markup(buttons) if buttons else None,
                                )
                            except Exception:
                                caption_with_links = query or (reply_msg.caption if reply_msg else "")
                                if buttons:
                                    link_lines = [f"• <a href='{b['url']}'>{b['text']}</a>" for row in buttons for b in row if 'url' in b]
                                    if link_lines:
                                        caption_with_links = (caption_with_links + "\n\n" + "\n".join(link_lines)).strip()
                                m = await client.send_photo(
                                    dialog.chat.id,
                                    photo,
                                    caption=caption_with_links or None,
                                )
                        elif buttons:
                            try:
                                m = await client.send_message(
                                    dialog.chat.id,
                                    text=query or "\u200b",
                                    reply_markup=buttons_to_inline_markup(buttons),
                                )
                            except Exception:
                                text_with_links = query or "📢"
                                link_lines = [f"• <a href='{b['url']}'>{b['text']}</a>" for row in buttons for b in row if 'url' in b]
                                if link_lines:
                                    text_with_links = (text_with_links + "\n\n" + "\n".join(link_lines)).strip()
                                m = await client.send_message(
                                    dialog.chat.id,
                                    text=text_with_links,
                                )
                        elif reply_msg:
                            m = await reply_msg.copy(dialog.chat.id)
                        else:
                            m = await client.send_message(dialog.chat.id, text=query or "📢")

                        if m:
                            ass_sent += 1
                            if is_pin or is_pinloud:
                                try:
                                    await m.pin(disable_notification=not is_pinloud)
                                except Exception:
                                    pass
                        else:
                            ass_failed += 1
                        await asyncio.sleep(1.0)
                    except FloodWait as fw:
                        wait_t = int(fw.value)
                        if wait_t > 60:
                            ass_failed += 1
                            continue
                        await asyncio.sleep(wait_t)
                    except Exception:
                        ass_failed += 1
                        continue
                assistant_stats += f"\n• 🤖 <b>ᴀssɪsᴛᴀɴᴛ {num} :</b> {ass_sent} sᴜᴄᴄᴇss | {ass_failed} ғᴀɪʟᴇᴅ"
            except Exception:
                continue

    time_taken = round(time.time() - start_time, 2)
    IS_BROADCASTING = False

    result_text = "✅ <b><u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ !</u></b> 🎉\n"
    result_text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    if target_groups and not no_bot:
        result_text += f"• 👥 <b>ɢʀᴏᴜᴘs :</b> {chats_sent} sᴜᴄᴄᴇss | {chats_failed} ғᴀɪʟᴇᴅ ({total_chats} ᴛᴏᴛᴀʟ)\n"
        if is_pin or is_pinloud:
            result_text += f"• 📌 <b>ᴘɪɴɴᴇᴅ :</b> {chats_pinned}\n"
    if target_users and not no_bot:
        result_text += f"• 👤 <b>ᴜsᴇʀs :</b> {users_sent} sᴜᴄᴄᴇss | {users_failed} ғᴀɪʟᴇᴅ ({total_users} ᴛᴏᴛᴀʟ)\n"
    if target_assistant:
        result_text += f"• 🤖 <b>ᴀssɪsᴛᴀɴᴛ(s) :</b>{assistant_stats or ' None'}\n"
    result_text += f"• ⏱️ <b>ᴛɪᴍᴇ ᴛᴀᴋᴇɴ :</b> {time_taken}s\n"
    result_text += "━━━━━━━━━━━━━━━━━━━━━━"

    try:
        await status_msg.edit_text(result_text)
    except Exception:
        pass


@app.on_message(filters.command(["broadcast", "bcast", "gcast", "ucast", "pcast"]) & SUDOERS)
@language
async def broadcast_command_handler(client, message: Message, _):
    global IS_BROADCASTING

    if IS_BROADCASTING:
        return await message.reply_text(
            "⚠️ <b>ᴀ ʙʀᴏᴀᴅᴄᴀsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ɪɴ ᴘʀᴏɢʀᴇss.</b>\n<i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴜɴᴛɪʟ ɪᴛ ᴄᴏᴍᴘʟᴇᴛᴇs.</i>"
        )

    cmd = message.command[0].lower()
    full_text = message.text or ""

    # Check for direct command shortcuts
    direct_groups = False
    direct_users = False
    if cmd == "gcast":
        direct_groups = True
    elif cmd in ("ucast", "pcast"):
        direct_users = True

    # Extract query text and parse flags + buttons
    raw_query = ""
    if len(message.command) > 1:
        raw_query = full_text.split(None, 1)[1]

    flags, query, photo, buttons = _extract_broadcast_data(raw_query)

    # Check photo from reply if not explicitly given via -photo
    reply = message.reply_to_message
    if not photo and reply and reply.photo:
        photo = reply.photo.file_id

    # Resolve target flags
    target_groups = direct_groups or flags["groups"]
    target_users = direct_users or flags["users"]
    target_assistant = flags["assistant"]

    # Auto support button if needed
    if not buttons and SUPPORT_CHAT and (photo or "-btn" in full_text):
        buttons.append(
            [styled_button("💬 sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}", style="primary")]
        )

    # Validation: need either text, reply message, photo or buttons
    if not reply and not photo and not query and not buttons and not target_groups and not target_users and not target_assistant:
        return await message.reply_text(
            "📢 <b><u>ʙʀᴏᴀᴅᴄᴀsᴛ ɢᴜɪᴅᴇ</u></b>\n\n"
            "• <b>ᴛᴀʀɢᴇᴛs :</b> <code>-user</code> | <code>-group</code> | <code>-all</code> | <code>-assistant</code>\n"
            "• <b>ғʟᴀɢs :</b> <code>-pin</code> | <code>-nobot</code> | <code>-forward</code> | <code>-btn</code>\n\n"
            "💡 <b>ᴇxᴀᴍᴘʟᴇ :</b>\n"
            "<code>/broadcast -all -pin [ᴍᴇssᴀɢᴇ]/BUTTON/https://example.com</code>\n\n"
            "<i>(ʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴏʀ ᴍᴇᴅɪᴀ)</i>"
        )

    # If any target is specified, run immediately
    if target_groups or target_users or target_assistant:
        target_labels = []
        if target_groups and not flags["nobot"]:
            target_labels.append("GROUPS")
        if target_users and not flags["nobot"]:
            target_labels.append("USERS")
        if target_assistant:
            target_labels.append("ASSISTANT")

        status = await message.reply_text(
            f"🚀 <b>sᴛᴀʀᴛɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ ({' + '.join(target_labels) if target_labels else 'BROADCAST'})...</b>"
        )
        asyncio.create_task(
            _execute_broadcast(
                target_groups=target_groups,
                target_users=target_users,
                target_assistant=target_assistant,
                query=query,
                photo=photo,
                buttons=buttons,
                reply_msg=reply,
                flags=flags,
                status_msg=status,
            )
        )
        return

    # No target specified → Show Interactive Selection Panel!
    token = str(uuid.uuid4())[:8]
    PENDING_BROADCASTS[token] = {
        "user_id": message.from_user.id if message.from_user else 0,
        "query": query,
        "photo": photo,
        "buttons": buttons,
        "reply": reply,
        "flags": flags,
        "time": time.time(),
    }

    # Clean old tokens
    now = time.time()
    for t, data in list(PENDING_BROADCASTS.items()):
        if now - data.get("time", 0) > 300:
            PENDING_BROADCASTS.pop(t, None)

    preview_text = query if query else ("📸 [Photo Attached]" if photo else ("📩 [Replied Message]" if reply else "No text"))
    if len(preview_text) > 80:
        preview_text = preview_text[:77] + "..."

    panel_text = (
        "📢 <b><u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ</u></b>\n\n"
        f"📝 <b>ᴘʀᴇᴠɪᴇᴡ :</b> <code>{preview_text}</code>\n\n"
        "🎯 <b>ᴊɪsᴋᴏ ʙʜᴇᴊɴᴀ ʜᴀɪ sᴇʟᴇᴄᴛ ᴋᴀʀᴇɪɴ :</b>"
    )

    markup = [
        [
            styled_button("👥 ᴏɴʟʏ ɢʀᴏᴜᴘs", callback_data=f"bcast_tgt:groups:{token}", style="primary"),
            styled_button("👤 ᴏɴʟʏ ᴜsᴇʀs", callback_data=f"bcast_tgt:users:{token}", style="primary"),
        ],
        [
            styled_button("🌐 ɢʀᴏᴜᴘs + ᴜsᴇʀs", callback_data=f"bcast_tgt:all:{token}", style="success"),
            styled_button("🤖 ᴀssɪsᴛᴀɴᴛ", callback_data=f"bcast_tgt:assistant:{token}", style="primary"),
        ],
        [
            styled_button("🚀 ᴀʟʟ (ɢᴄ + ᴜsᴇʀ + ᴀssɪsᴛᴀɴᴛ)", callback_data=f"bcast_tgt:all_with_ass:{token}", style="success"),
        ],
        [
            styled_button("❌ ᴄᴀɴᴄᴇʟ", callback_data=f"bcast_cancel:{token}", style="danger"),
        ],
    ]

    res = await send_message_colored(
        chat_id=message.chat.id,
        text=panel_text,
        reply_markup=markup,
    )
    if not res:
        await message.reply_text(
            text=panel_text,
            reply_markup=buttons_to_inline_markup(markup),
        )


@app.on_callback_query(filters.regex(r"^bcast_") & SUDOERS)
async def broadcast_callback_handler(client, query: CallbackQuery):
    global IS_BROADCASTING

    data = query.data.split(":")
    action = data[0]

    if action == "bcast_cancel":
        token = data[1] if len(data) > 1 else ""
        PENDING_BROADCASTS.pop(token, None)
        await query.answer("Broadcast Cancelled ❌")
        return await query.message.edit_text("❌ <b>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>")

    if action == "bcast_tgt":
        if len(data) < 3:
            return await query.answer("Invalid request.", show_alert=True)
        target = data[1]
        token = data[2]

        if IS_BROADCASTING:
            return await query.answer(
                "A broadcast is already running! Please wait.",
                show_alert=True,
            )

        bcast_data = PENDING_BROADCASTS.pop(token, None)
        if not bcast_data:
            return await query.answer("Broadcast session expired! Please try again.", show_alert=True)

        target_groups = target in ("groups", "all", "all_with_ass")
        target_users = target in ("users", "all", "all_with_ass")
        target_assistant = target in ("assistant", "all_with_ass")

        await query.answer(f"Starting broadcast to {target.upper()}...")
        status_msg = await query.message.edit_text(
            f"🚀 <b>sᴛᴀʀᴛɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ ({target.upper()})...</b>\n⏳ <i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</i>"
        )

        asyncio.create_task(
            _execute_broadcast(
                target_groups=target_groups,
                target_users=target_users,
                target_assistant=target_assistant,
                query=bcast_data["query"],
                photo=bcast_data["photo"],
                buttons=bcast_data["buttons"],
                reply_msg=bcast_data["reply"],
                flags=bcast_data["flags"],
                status_msg=status_msg,
            )
        )


async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if getattr(user.privileges, 'can_manage_video_chats', False):
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except Exception:
            continue


try:
    asyncio.get_running_loop().create_task(auto_clean())
except RuntimeError:
    pass

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
