# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import os
import gc
import sys
import time
import asyncio
import importlib
from threading import Thread

# Python 3.12 high-efficiency asyncio runtime

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from VishalMusic import LOGGER, app, userbot
from VishalMusic.core.call import VISHAL
from VishalMusic.misc import _boot_, sudo
from VishalMusic.plugins import ALL_MODULES
from VishalMusic.utils.database import get_banned_users, get_gbanned
from VishalMusic.utils.cookie_handler import fetch_and_store_cookies
from config import BANNED_USERS



async def _start_render_web_server():
    """Ultra-lightweight async web server for Render / Koyeb / Heroku healthchecks"""
    try:
        from aiohttp import web
        
        async def handle_home(request):
            uptime = int(time.time() - _boot_)
            hours, rem = divmod(uptime, 3600)
            mins, secs = divmod(rem, 60)
            bot_uname = getattr(app, "username", "") or config.BOT_USERNAME or "online"
            bot_display = getattr(app, "name", "") or config.BOT_NAME
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{bot_display} - Status</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ background: #0f172a; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
        .card {{ background: #1e293b; border-radius: 16px; padding: 2rem; max-width: 480px; width: 90%; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; border: 1px solid #334155; }}
        .status {{ display: inline-flex; align-items: center; gap: 8px; background: rgba(34,197,94,0.1); color: #22c55e; padding: 6px 14px; border-radius: 9999px; font-weight: 600; font-size: 0.9rem; margin-bottom: 1rem; }}
        .dot {{ width: 8px; height: 8px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 10px #22c55e; }}
        h1 {{ margin: 0 0 0.5rem 0; font-size: 1.5rem; }}
        p {{ color: #94a3b8; font-size: 0.95rem; margin: 0.5rem 0 1.5rem; }}
        .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 1rem; text-align: left; }}
        .stat-box {{ background: #0f172a; padding: 12px; border-radius: 10px; border: 1px solid #334155; }}
        .stat-label {{ color: #64748b; font-size: 0.75rem; text-transform: uppercase; font-weight: bold; }}
        .stat-value {{ font-size: 1rem; font-weight: 600; color: #e2e8f0; margin-top: 4px; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="status"><div class="dot"></div> Render Keep-Alive Active</div>
        <h1>🎵 {bot_display}</h1>
        <p>Ultra-optimized Telegram Music Bot is running smoothly 24/7 on Render.</p>
        <div class="stats">
            <div class="stat-box"><div class="stat-label">Status</div><div class="stat-value" style="color:#22c55e;">Online 🟢</div></div>
            <div class="stat-box"><div class="stat-label">Uptime</div><div class="stat-value">{hours}h {mins}m {secs}s</div></div>
            <div class="stat-box"><div class="stat-label">Bot Username</div><div class="stat-value">@{bot_uname}</div></div>
            <div class="stat-box"><div class="stat-label">Ping Status</div><div class="stat-value" style="color:#38bdf8;">200 OK</div></div>
        </div>
    </div>
</body>
</html>"""
            return web.Response(text=html, content_type="text/html", status=200)

        async def handle_health(request):
            return web.json_response({
                "status": "alive",
                "service": "VishalMusic",
                "uptime_seconds": int(time.time() - _boot_),
                "timestamp": int(time.time())
            }, status=200)

        server = web.Application()
        server.router.add_get("/", handle_home)
        server.router.add_get("/health", handle_health)
        server.router.add_get("/ping", handle_health)
        
        runner = web.AppRunner(server)
        await runner.setup()
        port = int(os.environ.get("PORT", getattr(config, "PORT", 2000) or 8080))
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        LOGGER("VishalMusic").info(f"🌐 ʀᴇɴᴅᴇʀ ᴡᴇʙ ꜱᴇʀᴠᴇʀ ʀᴜɴɴɪɴɢ ᴏɴ ᴘᴏʀᴛ {port}")
    except Exception as e:
        LOGGER("VishalMusic").warning(f"⚠️ ᴡᴇʙ ꜱᴇʀᴠᴇʀ ꜱᴛᴀʀᴛ ꜰᴀɪʟᴇᴅ: {e}")


async def _render_keep_alive_loop() -> None:
    """Self-pinger keep-alive task to prevent Render free instance from sleeping."""
    await asyncio.sleep(45)  # Wait 45s after startup
    url = getattr(config, "PING_URL", None) or os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("PING_URL") or os.environ.get("RENDER_URL") or os.environ.get("APP_URL")
    
    port = int(os.environ.get("PORT", getattr(config, "PORT", 2000) or 8080))
    ping_target = url.rstrip("/") if url else f"http://127.0.0.1:{port}"
    if not ping_target.endswith("/health"):
        ping_endpoint = f"{ping_target}/health"
    else:
        ping_endpoint = ping_target

    LOGGER("VishalMusic").info(f"💓 ʀᴇɴᴅᴇʀ ᴋᴇᴇᴘ-ᴀʟɪᴠᴇ ᴀᴄᴛɪᴠᴇ: ᴘɪɴɢɪɴɢ {ping_endpoint} ᴇᴠᴇʀʏ 8 ᴍɪɴᴜᴛᴇꜱ.")

    import aiohttp
    while True:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.get(ping_endpoint) as resp:
                    if resp.status == 200:
                        LOGGER("VishalMusic").info(f"💓 ᴋᴇᴇᴘ-ᴀʟɪᴠᴇ ᴘɪɴɢ ꜱᴜᴄᴄᴇꜱꜱ [200 OK]")
                    else:
                        LOGGER("VishalMusic").warning(f"⚠️ ᴋᴇᴇᴘ-ᴀʟɪᴠᴇ ᴘɪɴɢ ʀᴇᴛᴜʀɴᴇᴅ ꜱᴛᴀᴛᴜꜱ: {resp.status}")
        except Exception as e:
            LOGGER("VishalMusic").warning(f"⚠️ ᴋᴇᴇᴘ-ᴀʟɪᴠᴇ ᴘɪɴɢ ᴇʀʀᴏʀ: {e}")
        
        # Ping every 8 minutes (480s) before Render 15min idle limit
        await asyncio.sleep(480)


async def _cookie_refresh_loop() -> None:
    hours = float(os.environ.get("COOKIE_REFRESH_HOURS", "12"))
    while True:
        await asyncio.sleep(hours * 3600)
        try:
            await fetch_and_store_cookies()
            LOGGER("VishalMusic").info("ʏᴏᴜᴛᴜʙᴇ ᴄᴏᴏᴋɪᴇs ʀᴇꜰʀᴇꜱʜᴇᴅ ✔")
        except Exception as e:
            LOGGER("VishalMusic").warning(f"⚠️ ᴄᴏᴏᴋɪᴇ ʀᴇꜰʀᴇꜱʜ ꜰᴀɪʟᴇᴅ: {e}")


async def _memory_cleanup_loop() -> None:
    """Low-RAM optimizer: run periodic garbage collection and clear temporary downloads & caches."""
    while True:
        await asyncio.sleep(120)  # Every 2 mins for Render low-RAM tier
        try:
            gc.collect(2)
            # Clean leftover files in downloads and cache directories
            for folder in ("downloads", "cache"):
                if os.path.exists(folder):
                    now = time.time()
                    for f in os.listdir(folder):
                        fp = os.path.join(folder, f)
                        # Remove stale files older than 30 mins
                        if os.path.isfile(fp) and (now - os.path.getmtime(fp) > 1800):
                            try:
                                os.remove(fp)
                            except Exception:
                                pass
        except Exception:
            pass


async def _auto_restart_loop(hours: float) -> None:
    while True:
        await asyncio.sleep(hours * 3600)
        LOGGER("VishalMusic").info(f"🔄 ᴀᴜᴛᴏ-ʀᴇꜱᴛᴀʀᴛ ᴀꜰᴛᴇʀ {hours}h ᴏꜰ ᴜᴘᴛɪᴍᴇ...")
        try:
            os.execv(sys.executable, [sys.executable, "-m", "VishalMusic"])
        except Exception as e:
            LOGGER("VishalMusic").error(f"❌ ᴀᴜᴛᴏ-ʀᴇꜱᴛᴀʀᴛ ꜰᴀɪʟᴇᴅ: {e}")
            return



async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("ᴀssɪsᴛᴀɴᴛ sᴇssɪᴏɴ ɴᴏᴛ ғɪʟʟᴇᴅ, ᴘʟᴇᴀsᴇ ғɪʟʟ ᴀ ᴘʏʀᴏɢʀᴀᴍ sᴇssɪᴏɴ...")
        exit()

    try:
        await fetch_and_store_cookies()
    except Exception as e:
        LOGGER("VishalMusic").warning(f"⚠️ ᴄᴏᴏᴋɪᴇ ᴇʀʀᴏʀ: {e}")

    try:
        from VishalMusic.utils.oauth_helper import init_youtube_oauth_nonblocking
        init_youtube_oauth_nonblocking()
    except Exception:
        pass

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception:
        pass

    await sudo()
    await app.start()

    for all_module in ALL_MODULES:
        try:
            importlib.import_module("VishalMusic.plugins." + all_module)
        except Exception as e:
            LOGGER("VishalMusic.plugins").error(
                f"❌ Failed to load module {all_module}: {e}\nBot continues without it."
            )

    LOGGER("VishalMusic.plugins").info("✅ ᴀʟʟ ᴍᴏᴅᴜʟᴇꜱ ʟᴏᴀᴅᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ.")
    await userbot.start()
    await VISHAL.start()
    await _start_render_web_server()

    try:
        test_file = "VishalMusic/assets/test.mp4" if os.path.exists("VishalMusic/assets/test.mp4") else "assets/test.mp4"
        await VISHAL.stream_call(test_file)
    except NoActiveGroupCall:
        LOGGER("VishalMusic").error(
            "ᴘʟᴇᴀsᴇ ᴛᴜʀɴ ᴏɴ ᴛʜᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ ᴏғ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ\ᴄʜᴀɴɴᴇʟ.\n\nsᴛᴏᴘᴘɪɴɢ ʙᴏᴛ..."
        )
        exit()
    except Exception:
        pass

    await VISHAL.decorators()
    LOGGER("VishalMusic").info(
        "\x41\x6e\x61\x6e\x79\x61\x20\x4d\x75\x73\x69\x63\x20\x42\x6f\x74\x20\x53\x74\x61\x72\x74\x65\x64\x20\x53\x75\x63\x63\x65\x73\x73\x66\x75\x6c\x6c\x79\x2e\n\n\x44\x6f\x6e\x27\x74\x20\x66\x6f\x72\x67\x65\x74\x20\x74\x6f\x20\x76\x69\x73\x69\x74\x20\x40\x46\x65\x65\x6c\x69\x6e\x67\x73\x5f\x73\x61\x79\x73"
    )

    # Background tasks
    asyncio.create_task(_render_keep_alive_loop())
    asyncio.create_task(_cookie_refresh_loop())
    asyncio.create_task(_memory_cleanup_loop())

    try:
        from VishalMusic.plugins.admins.callback import _now_playing_timer
        asyncio.create_task(_now_playing_timer())
        LOGGER("VishalMusic").info("⏱️ ʟɪᴠᴇ ɴᴏᴡ-ᴘʟᴀʏɪɴɢ ᴛɪᴍᴇʀ & ᴩʀᴏɢʀᴇss ʙᴀʀ sᴛᴀʀᴛᴇᴅ.")
    except Exception as e:
        LOGGER("VishalMusic").warning(f"⚠️ Timer task start failed: {e}")

    auto_restart_hours = float(os.environ.get("AUTO_RESTART_HOURS", "0"))
    if auto_restart_hours > 0:
        LOGGER("VishalMusic").info(f"🔄 ᴀᴜᴛᴏ-ʀᴇꜱᴛᴀʀᴛ ᴇɴᴀʙʟᴇᴅ: ᴇᴠᴇʀʏ {auto_restart_hours} ʜᴏᴜʀꜱ.")
        asyncio.create_task(_auto_restart_loop(auto_restart_hours))

    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("VishalMusic").info("sᴛᴏᴘᴘɪɴɢ ᴠɪsʜᴀʟ ᴍᴜsɪᴄ ʙᴏᴛ...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
