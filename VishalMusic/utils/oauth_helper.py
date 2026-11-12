# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import os
import json
import time
import uuid
import threading
import urllib.request
import urllib.error
from pathlib import Path

from VishalMusic import LOGGER

LOGGER_OAUTH = LOGGER("VishalMusic.utils.oauth")

CLIENT_ID = "861556708454-d6dlm3lh05idd8npek18k6be8ba3oc68.apps.googleusercontent.com"
CLIENT_SECRET = "SboVhoG9s0rNafixCSGGKXAT"
SCOPES = "https://gdata.youtube.com https://www.googleapis.com/auth/youtube"

TOKEN_FILE = Path("VishalMusic/assets/youtube_oauth.json")


def is_token_valid() -> bool:
    """Check if a valid cached OAuth2 token exists."""
    if not TOKEN_FILE.exists():
        return False
    try:
        data = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
        return bool(data.get("refresh_token") and data.get("access_token"))
    except Exception:
        return False


def save_token(token_data: dict) -> None:
    """Save token data to local file and yt-dlp cache."""
    try:
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(json.dumps(token_data, indent=2), encoding="utf-8")
        
        # Also store into yt-dlp cache so yt-dlp can find it
        try:
            from yt_dlp.cache import Cache
            cache = Cache(None)
            cache.store("youtube-oauth2", "token_data", token_data)
        except Exception:
            pass
    except Exception as e:
        LOGGER_OAUTH.warning(f"Failed to save oauth token: {e}")


def _poll_device_token(device_code: str, interval: int, expires_in: int) -> None:
    """Background polling loop for user authorization."""
    end_time = time.time() + expires_in
    while time.time() < end_time:
        time.sleep(interval)
        try:
            req = urllib.request.Request(
                "https://www.youtube.com/o/oauth2/token",
                data=json.dumps({
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                }).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req) as resp:
                token_res = json.loads(resp.read().decode())
                if token_res.get("access_token") and token_res.get("refresh_token"):
                    token_data = {
                        "access_token": token_res["access_token"],
                        "expires": time.time() + token_res.get("expires_in", 3600),
                        "refresh_token": token_res["refresh_token"],
                        "token_type": token_res.get("token_type", "Bearer"),
                    }
                    save_token(token_data)
                    print("\n" + "=" * 60)
                    print("✅ 𝗬𝗢𝗨𝗧𝗨𝗕𝗘 𝗢𝗔𝗨𝗧𝗛𝟮: 𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗮𝘁𝗶𝗼𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹! 𝗧𝗼𝗸𝗲𝗻 𝗦𝗮𝘃𝗲𝗱.")
                    print("=" * 60 + "\n")
                    LOGGER_OAUTH.info("✅ ʏᴏᴜᴛᴜʙᴇ ᴏᴀᴜᴛʜ2: ᴀᴜᴛʜᴏʀɪᴢᴀᴛɪᴏɴ sᴜᴄᴄᴇssғᴜʟ!")
                    return
        except urllib.error.HTTPError as e:
            try:
                err_body = json.loads(e.read().decode())
                err = err_body.get("error")
                if err == "authorization_pending":
                    continue
                elif err in ("expired_token", "access_denied"):
                    return
            except Exception:
                pass
        except Exception:
            pass


def init_youtube_oauth_nonblocking() -> None:
    """Non-blocking YouTube OAuth2 helper on startup."""
    try:
        if is_token_valid():
            LOGGER_OAUTH.info("✅ ʏᴏᴜᴛᴜʙᴇ ᴏᴀᴜᴛʜ2: ᴀʟʀᴇᴀᴅʏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ.")
            return

        req = urllib.request.Request(
            "https://www.youtube.com/o/oauth2/device/code",
            data=json.dumps({
                "client_id": CLIENT_ID,
                "scope": SCOPES,
                "device_id": uuid.uuid4().hex,
                "device_model": "ytlr::",
            }).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())

        user_code = data.get("user_code")
        verification_url = data.get("verification_url", "https://www.google.com/device")
        device_code = data.get("device_code")
        interval = data.get("interval", 5)
        expires_in = data.get("expires_in", 1800)

        if user_code and device_code:
            LOGGER_OAUTH.info(f"🔑 ʏᴏᴜᴛᴜʙᴇ ᴏᴀᴜᴛʜ2: ɢᴏ ᴛᴏ {verification_url} ᴀɴᴅ ᴇɴᴛᴇʀ ᴄᴏᴅᴇ: {user_code}")
            print("\n" + "╔" + "═" * 62 + "╗", flush=True)
            print("║  🔑 𝗬𝗢𝗨𝗧𝗨𝗕𝗘 𝗗𝗘𝗩𝗜𝗖𝗘 𝗟𝗢𝗚𝗜𝗡 (Optional yt-dlp Fallback)         ║", flush=True)
            print(f"║  1. Link : {verification_url:<49} ║", flush=True)
            print(f"║  2. Code : {user_code:<49} ║", flush=True)
            print("╚" + "═" * 62 + "╝\n", flush=True)

            thread = threading.Thread(
                target=_poll_device_token,
                args=(device_code, interval, expires_in),
                daemon=True,
            )
            thread.start()

    except Exception as e:
        LOGGER_OAUTH.debug(f"OAuth init skipped (fallback only): {e}")
