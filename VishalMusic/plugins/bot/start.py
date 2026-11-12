# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import time
import asyncio
import random
from pyrogram import enums, filters
from pyrogram.enums import ChatType
from pyrogram.types import Message
from py_yt import VideosSearch

import config
from VishalMusic import app
from VishalMusic.misc import _boot_
from VishalMusic.plugins.sudo.sudoers import sudoers_list
from VishalMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from VishalMusic.utils.decorators.language import LanguageStart
from VishalMusic.utils.formatters import get_readable_time
from VishalMusic.utils.inline.help import first_page
from VishalMusic.utils.inline.start import private_panel, start_panel
from VishalMusic.utils.colored_buttons import (
    styled_button,
    buttons_to_inline_markup,
    smart_send_photo as send_photo_colored,
)
from config import BANNED_USERS
from strings import get_string

# 🔥 Love, Kiss, Cute stickers
STICKERS = [
    "CAACAgUAAxkBAAEQI1RlTLnRAy4h9lOS6jgS5FYsQoruOAAC1gMAAg6ryVcldUr_lhPexzME",
    "CAACAgQAAxkBAAMraaaBHm27-Wy2uQoptU3WZAAB6j3PAALEFQACIPCZUR1h3KoW6nItHgQ",
    "CAACAgQAAxkBAAMtaaaBKyjqLW8aBukB-vtOy-pUCxwAAoIOAAIF9AFSd_QCdbkZVqAeBA",
    "CAACAgQAAxkBAAMvaaaBNyAKbOtk05em_J8gQTmqotsAAhELAAIbGgABUuUNZ1V7LfMMHgQ",
    "CAACAgQAAxkBAAMxaaaBTZjH9A31Qdrb_xgKnrd4700AArgaAAJLO-hR8MN1DY1xe2ceBA",
    "CAACAgQAAxkBAAM5aaaB7A7JfXbtkO7b8ubX6_IjDdIAAhoVAAKRIKFRpathP0j9IIYeBA",
    "CAACAgQAAxkBAAMzaaaBUYNDr2RENDvdHTkz5tg-lVcAAmkaAAIIeUlRllAUMDa5YOoeBA",
    "CAACAgQAAxkBAAM7aaaB-elXM9UEYY4OIo4eTCIbgigAAuUVAALryRlQRN37BBGYPgYeBA",
    "CAACAgQAAxkBAAM_aaaCCjmuL6EkqSBKpYbYzK3xKCcAAqYTAAK9jHlQ6vzt6mbH8-ceBA",
]

REACTIONS = ["❤️", "🔥", "🥰", "😍", "😘", "👍", "👏", "🎉", "✨", "⭐️", "🎵", "🎶", "💖", "💗", "💓"]


async def delete_message_after_delay(message: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    try:
        await add_served_user(message.from_user.id)
    except Exception:
        pass

    # Quick reaction
    try:
        await message.react(random.choice(REACTIONS))
    except Exception:
        pass
    
    # Make sure _ is language dict
    if isinstance(_, int):
        language = await get_lang(message.chat.id)
        _ = get_string(language)
    
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = first_page(_)
            start_photo = random.choice(config.START_IMGS)
            caption = _["help_1"].format(config.SUPPORT_CHAT)
            try:
                res = await send_photo_colored(
                    chat_id=message.chat.id,
                    photo=start_photo,
                    caption=caption,
                    reply_markup=keyboard,
                )
                if not res:
                    await message.reply_photo(
                        photo=start_photo,
                        caption=caption,
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=buttons_to_inline_markup(keyboard),
                    )
            except Exception:
                await message.reply_photo(
                    photo=start_photo,
                    caption=caption,
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=buttons_to_inline_markup(keyboard),
                )
            return

        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                username = f"@{message.from_user.username}" if message.from_user.username else "None"
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> {username}",
                )
            return

        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            res_data = await results.next()
            if res_data and res_data.get("result"):
                result = res_data["result"][0]
                title = result.get("title", "")
                duration = result.get("duration", "")
                views = result.get("viewCount", {}).get("short", "")
                thumbnail = result.get("thumbnails", [{}])[0].get("url", "").split("?")[0]
                channellink = result.get("channel", {}).get("link", "")
                channel = result.get("channel", {}).get("name", "")
                link = result.get("link", "")
                published = result.get("publishedTime", "")
            else:
                title = duration = views = thumbnail = channellink = channel = link = published = ""
            
            bot_mention = f'<a href="tg://user?id={app.id}">{app.name}</a>'
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, bot_mention
            )
            key = [
                [
                    styled_button(text=_["S_B_6"], url=link, style="primary"),
                    styled_button(text=_["S_B_4"], url=config.SUPPORT_CHAT, style="primary"),
                ],
            ]
            await m.delete()
            try:
                res = await send_photo_colored(
                    chat_id=message.chat.id,
                    photo=thumbnail or random.choice(config.START_IMGS),
                    caption=searched_text,
                    reply_markup=key,
                )
                if not res:
                    await message.reply_photo(
                        photo=thumbnail or random.choice(config.START_IMGS),
                        caption=searched_text,
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=buttons_to_inline_markup(key),
                    )
            except Exception:
                await message.reply_photo(
                    photo=thumbnail or random.choice(config.START_IMGS),
                    caption=searched_text,
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=buttons_to_inline_markup(key),
                )
            if await is_on_off(2):
                username = f"@{message.from_user.username}" if message.from_user.username else "None"
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> {username}",
                )
            return

    # Normal Private Chat /start
    start_photo = random.choice(config.START_IMGS)
    out = await private_panel(_)
    
    user_name = message.from_user.first_name if message.from_user else "User"
    user_id = message.from_user.id if message.from_user else message.chat.id
    user_mention = f'<a href="tg://user?id={user_id}">{user_name}</a>'
    bot_mention = f'<a href="tg://user?id={app.id}">{app.name}</a>'
    caption = _["start_2"].format(user_mention, bot_mention)
    
    try:
        res = await send_photo_colored(
            chat_id=message.chat.id,
            photo=start_photo,
            caption=caption,
            reply_markup=out,
        )
        if not res:
            await message.reply_photo(
                photo=start_photo,
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=buttons_to_inline_markup(out),
            )
    except Exception:
        await message.reply_photo(
            photo=start_photo,
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=buttons_to_inline_markup(out),
        )

    if await is_on_off(2):
        username = f"@{message.from_user.username}" if message.from_user.username else "None"
        try:
            await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> {username}",
            )
        except Exception:
            pass


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    try:
        await message.react(random.choice(REACTIONS))
    except Exception:
        pass
    
    if isinstance(_, int):
        language = await get_lang(message.chat.id)
        _ = get_string(language)
    
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    start_photo = random.choice(config.START_IMGS)
    
    bot_mention = f'<a href="tg://user?id={app.id}">{app.name}</a>'
    caption = _["start_1"].format(bot_mention, get_readable_time(uptime))
    
    try:
        res = await send_photo_colored(
            chat_id=message.chat.id,
            photo=start_photo,
            caption=caption,
            reply_markup=out,
        )
        if not res:
            await message.reply_photo(
                photo=start_photo,
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=buttons_to_inline_markup(out),
            )
    except Exception:
        await message.reply_photo(
            photo=start_photo,
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=buttons_to_inline_markup(out),
        )
    
    return await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except Exception:
                    pass
                    
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                    
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                welcome_photo = random.choice(config.START_IMGS)
                
                try:
                    res = await send_photo_colored(
                        chat_id=message.chat.id,
                        photo=welcome_photo,
                        caption=_["start_3"].format(
                            member.first_name,
                            app.mention,
                            message.chat.title,
                            app.mention,
                        ),
                        reply_markup=out,
                    )
                    if not res:
                        await message.reply_photo(
                            photo=welcome_photo,
                            caption=_["start_3"].format(
                                member.first_name,
                                app.mention,
                                message.chat.title,
                                app.mention,
                            ),
                            parse_mode=enums.ParseMode.HTML,
                            reply_markup=buttons_to_inline_markup(out),
                        )
                except Exception:
                    await message.reply_photo(
                        photo=welcome_photo,
                        caption=_["start_3"].format(
                            member.first_name,
                            app.mention,
                            message.chat.title,
                            app.mention,
                        ),
                        parse_mode=enums.ParseMode.HTML,
                        reply_markup=buttons_to_inline_markup(out),
                    )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
                
        except Exception:
            pass
