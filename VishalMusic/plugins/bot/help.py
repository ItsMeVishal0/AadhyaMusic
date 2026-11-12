# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀﻟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import re
import random
from typing import Union

from pyrogram import Client, filters, types
from pyrogram.types import Message

import config
from VishalMusic import app
from VishalMusic.utils.database import get_lang
from VishalMusic.utils.decorators.language import LanguageStart, languageCB
from VishalMusic.utils.inline.help import (
    first_page,
    help_back_markup,
    private_help_panel,
    help_p_panel,
)
from VishalMusic.utils.inline.start import private_panel
from VishalMusic.utils.colored_buttons import (
    buttons_to_inline_markup,
    smart_send_photo as send_photo_colored,
    smart_send_message as send_message_colored,
    smart_edit_message_caption as edit_message_caption_colored,
    smart_edit_message_text as edit_message_text_colored,
)
from config import BANNED_USERS, SUPPORT_CHAT
from strings import get_string, helpers


# ────────────────────────────────────────────────  /help entrypoints ──

@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("open_help") & ~BANNED_USERS)
@LanguageStart
async def helper_private(client: Client, update: Union[Message, types.CallbackQuery], _):
    is_cb = isinstance(update, types.CallbackQuery)
    language = await get_lang(update.from_user.id)
    _ = get_string(language)

    keyboard = first_page(_)
    caption = _["help_1"].format(SUPPORT_CHAT)

    if is_cb:
        await update.answer()
        if update.message.photo:
            try:
                await edit_message_caption_colored(
                    chat_id=update.message.chat.id,
                    message_id=update.message.id,
                    caption=caption,
                    reply_markup=keyboard,
                )
                return
            except Exception:
                pass
        await edit_message_text_colored(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=caption,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    else:
        await send_photo_colored(
            chat_id=update.chat.id,
            photo=random.choice(config.START_IMGS),
            caption=caption,
            reply_markup=keyboard,
        )


# ────────────────────────────────────────────────  group /help notice ─

@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client: Client, message: Message, _):
    keyboard = private_help_panel(_)
    await send_message_colored(
        chat_id=message.chat.id,
        text=_["help_2"],
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


# ─────────────────────────────────────────  page navigation handler ───

@app.on_callback_query(filters.regex(r"^help_page\s+(\d+)$") & ~BANNED_USERS)
@languageCB
async def help_page_navigation(client: Client, CallbackQuery: types.CallbackQuery, _):
    await CallbackQuery.answer()
    match = re.match(r"^help_page\s+(\d+)$", CallbackQuery.data)
    page = int(match.group(1)) if match else 1

    keyboard = help_p_panel(_, page)
    caption = _["help_1"].format(SUPPORT_CHAT)

    if CallbackQuery.message.photo:
        try:
            await edit_message_caption_colored(
                chat_id=CallbackQuery.message.chat.id,
                message_id=CallbackQuery.message.id,
                caption=caption,
                reply_markup=keyboard,
            )
            return
        except Exception:
            pass
    await edit_message_text_colored(
        chat_id=CallbackQuery.message.chat.id,
        message_id=CallbackQuery.message.id,
        text=caption,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


# ─────────────────────────────────────────  topic help callback ───────

@app.on_callback_query(filters.regex(r"help_callback hb(\d+)_p(\d+)") & ~BANNED_USERS)
@languageCB
async def helper_cb(client: Client, CallbackQuery: types.CallbackQuery, _):
    await CallbackQuery.answer()
    match = re.match(r"help_callback hb(\d+)_p(\d+)", CallbackQuery.data)
    if not match:
        return await CallbackQuery.answer("Invalid callback.", show_alert=True)

    number = int(match.group(1))
    current_page = int(match.group(2))

    help_text = getattr(helpers, f"HELP_{number}", None)
    if not help_text:
        return await CallbackQuery.answer("Invalid help topic.", show_alert=True)

    markup = help_back_markup(_, current_page)

    if CallbackQuery.message.photo:
        try:
            await edit_message_caption_colored(
                chat_id=CallbackQuery.message.chat.id,
                message_id=CallbackQuery.message.id,
                caption=help_text,
                reply_markup=markup,
            )
            return
        except Exception:
            pass
        await send_message_colored(
            chat_id=CallbackQuery.message.chat.id,
            text=help_text,
            reply_markup=markup,
            disable_web_page_preview=True,
        )
    else:
        await edit_message_text_colored(
            chat_id=CallbackQuery.message.chat.id,
            message_id=CallbackQuery.message.id,
            text=help_text,
            reply_markup=markup,
            disable_web_page_preview=True,
        )


# ─────────────────────────────────────────  back to main menu callback ──

@app.on_callback_query(filters.regex("back_to_main") & ~BANNED_USERS)
@languageCB
async def back_to_main_cb(client: Client, CallbackQuery: types.CallbackQuery, _):
    await CallbackQuery.answer()
    out = await private_panel(_)
    user_mention = (
        f'<a href="tg://user?id={CallbackQuery.from_user.id}">'
        f'{CallbackQuery.from_user.first_name}</a>'
    )
    bot_mention = f'<a href="tg://user?id={app.id}">{app.name}</a>'
    caption = _["start_2"].format(user_mention, bot_mention)

    if CallbackQuery.message.photo:
        try:
            await edit_message_caption_colored(
                chat_id=CallbackQuery.message.chat.id,
                message_id=CallbackQuery.message.id,
                caption=caption,
                reply_markup=out,
            )
            return
        except Exception:
            pass
    await edit_message_text_colored(
        chat_id=CallbackQuery.message.chat.id,
        message_id=CallbackQuery.message.id,
        text=caption,
        reply_markup=out,
        disable_web_page_preview=True,
    )
