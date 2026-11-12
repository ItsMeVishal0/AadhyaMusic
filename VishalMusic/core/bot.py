# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import os
import sys
from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import BotCommand, MenuButtonCommands

import config
from ..logging import LOGGER


# Dynamically scale workers for optimal low-RAM / low-CPU performance
WORKER_COUNT = min(16, max(4, (os.cpu_count() or 1) * 4))


import asyncio

class VISHAL(Client):
    def __init__(self):
        super().__init__(
            name="VishalMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=False,
            workers=WORKER_COUNT,
            max_concurrent_transmissions=4,
            sleep_threshold=120,
        )

        LOGGER(__name__).info(f"ʙᴏᴛ ᴄʟɪᴇɴᴛ ɪɴɪᴛɪᴀʟɪᴢᴇᴅ ᴡɪᴛʜ {WORKER_COUNT} ᴡᴏʀᴋᴇʀs.")

    async def start(self):
        try:
            await super().start()
        except errors.FloodWait as e:
            LOGGER(__name__).warning(f"Telegram FloodWait encountered ({e.value}s). Waiting automatically...")
            await asyncio.sleep(e.value)
            await super().start()
        me = await self.get_me()
        self.username, self.id = me.username, me.id
        self.name = f"{me.first_name} {me.last_name or ''}".strip()
        self.mention = me.mention

        try:
            await self.send_message(
                config.LOGGER_ID,
                (
                    f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\n"
                    f"ɪᴅ : <code>{self.id}</code>\n"
                    f"ɴᴀᴍᴇ : {self.name}\n"
                    f"ᴜsᴇʀɴᴀᴍᴇ : @{self.username}"
                ),
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).warning("⚠️ Bot cannot access the log group/channel – continuing without it.")
            return
        except Exception as exc:
            LOGGER(__name__).warning(f"⚠️ Bot failed to access the log group: {type(exc).__name__} – continuing.")
            return


        try:
            member = await self.get_chat_member(config.LOGGER_ID, self.id)
            if member.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).warning("⚠️ Bot is not admin in the log group/channel – continuing without it.")
                return
        except Exception as e:
            LOGGER(__name__).warning(f"⚠️ Could not check log group admin status: {e} – continuing.")
            return

        try:
            await self.set_bot_commands(
                [
                    BotCommand("start", "⚡ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ"),
                    BotCommand("help", "📖 ɢᴇᴛ ʜᴇʟᴘ ᴍᴇɴᴜ"),
                    BotCommand("play", "🎵 ᴘʟᴀʏ ᴀ sᴏɴɢ ɪɴ ᴠᴄ"),
                    BotCommand("vplay", "🎬 ᴘʟᴀʏ ᴠɪᴅᴇᴏ ɪɴ ᴠᴄ"),
                    BotCommand("stop", "⏹️ sᴛᴏᴘ sᴛʀᴇᴀᴍɪɴɢ"),
                    BotCommand("pause", "⏸️ ᴘᴀᴜsᴇ ᴛʜᴇ sᴛʀᴇᴀᴍ"),
                    BotCommand("resume", "▶️ ʀᴇsᴜᴍᴇ ᴛʜᴇ sᴛʀᴇᴀᴍ"),
                    BotCommand("skip", "⏭️ sᴋɪᴘ ᴛᴏ ɴᴇxᴛ sᴏɴɢ"),
                    BotCommand("queue", "📜 sʜᴏᴡ ǫᴜᴇᴜᴇ ʟɪsᴛ"),
                    BotCommand("loop", "🔁 ʟᴏᴏᴘ ᴄᴜʀʀᴇɴᴛ sᴏɴɢ"),
                    BotCommand("shuffle", "🔀 sʜᴜғғʟᴇ ᴛʜᴇ ǫᴜᴇᴜᴇ"),
                    BotCommand("seek", "⏩ sᴇᴇᴋ ɪɴ ᴄᴜʀʀᴇɴᴛ sᴏɴɢ"),
                    BotCommand("speed", "🎚️ ᴄʜᴀɴɢᴇ ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ"),
                    BotCommand("song", "📥 ᴅᴏᴡɴʟᴏᴀᴅ sᴏɴɢ"),
                    BotCommand("settings", "⚙️ ʙᴏᴛ sᴇᴛᴛɪɴɢs"),
                    BotCommand("ping", "🏓 ᴄʜᴇᴄᴋ ʙᴏᴛ ᴘɪɴɢ"),
                    BotCommand("reload", "🔄 ʀᴇʟᴏᴀᴅ ᴀᴅᴍɪɴ ᴄᴀᴄʜᴇ"),
                ]
            )
            try:
                await self.set_chat_menu_button(menu_button=MenuButtonCommands())
            except Exception:
                pass
            LOGGER(__name__).info("✅ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅꜱ ᴍᴇɴᴜ ꜱᴇᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ.")
        except Exception as e:
            LOGGER(__name__).warning(f"⚠️ Failed to set bot commands: {e}")

        LOGGER(__name__).info(f"✅ ᴍᴜsɪᴄ ʙᴏᴛ sᴛᴀʀᴛᴇᴅ ᴀs {self.name} (@{self.username})")

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
