# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import asyncio
import contextlib
import json
import os
import re
import time
import aiofiles
import aiohttp
import shutil
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

import config
import yt_dlp

from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch

from VishalMusic.utils.cookie_handler import COOKIE_PATH
from VishalMusic.utils.database import is_on_off
from VishalMusic.utils.downloader import download_audio_concurrent, yt_dlp_download
from VishalMusic.utils.errors import capture_internal_err
from VishalMusic.utils.formatters import time_to_seconds
from VishalMusic.utils.tuning import (
    YTDLP_TIMEOUT,
    YOUTUBE_META_MAX,
    YOUTUBE_META_TTL,
)

from VishalMusic import LOGGER

_module_logger = LOGGER(__name__)

_cache: Dict[str, Tuple[float, List[Dict]]] = {}
_cache_lock = asyncio.Lock()
_formats_cache: Dict[str, Tuple[float, List[Dict], str]] = {}
_formats_lock = asyncio.Lock()

# ============ YOUTUBE DUAL API CONFIGURATION ============
YOUTUBE_API_1 = (getattr(config, "YOUTUBE_API_1", None) or getattr(config, "API_URL", None) or "").rstrip("/").removesuffix("/download")
YOUTUBE_API_KEY_1 = getattr(config, "YOUTUBE_API_KEY_1", None) or getattr(config, "API_KEY", None) or ""

YOUTUBE_API_2 = (getattr(config, "YOUTUBE_API_2", None) or getattr(config, "API_URL_2", None) or getattr(config, "DEEP_API", None) or "").rstrip("/").removesuffix("/download")
YOUTUBE_API_KEY_2 = getattr(config, "YOUTUBE_API_KEY_2", None) or getattr(config, "API_KEY_2", None) or ""

# Legacy aliases
PRIMARY_API_URL = YOUTUBE_API_1
VISHAL_API_KEY = YOUTUBE_API_KEY_1
FALLBACK_API_URL = YOUTUBE_API_2
FALLBACK_API_KEY = YOUTUBE_API_KEY_2

PRIMARY_API_LOADED = False
FALLBACK_API_LOADED = False



# ============ RATE LIMITING (async â€” does NOT block the event loop) ============
_request_timestamps = []
_RATE_LIMIT_WINDOW = 60
_MAX_REQUESTS_PER_WINDOW = 10
_rate_limit_lock = asyncio.Lock()

async def _check_rate_limit_async():
    """Non-blocking async rate-limit guard (replaces the old blocking time.sleep)."""
    global _request_timestamps

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════

    async with _rate_limit_lock:
        now = time.time()




        _request_timestamps = [ts for ts in _request_timestamps if now - ts < _RATE_LIMIT_WINDOW]
        if len(_request_timestamps) >= _MAX_REQUESTS_PER_WINDOW:


            sleep_time = _RATE_LIMIT_WINDOW - (now - _request_timestamps[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            _request_timestamps = []
        _request_timestamps.append(time.time())


# â”€â”€ Shared persistent HTTP session for all API calls â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_yt_session: aiohttp.ClientSession = None
_yt_session_lock = asyncio.Lock()

async def _get_yt_session() -> aiohttp.ClientSession:
    global _yt_session
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if _yt_session and not _yt_session.closed:
        if getattr(_yt_session, "_loop", None) is None or _yt_session._loop == current_loop:
            return _yt_session
        else:
            try:
                await _yt_session.close()
            except Exception:
                pass
            _yt_session = None

    async with _yt_session_lock:
        if _yt_session and not _yt_session.closed:
            return _yt_session
        connector = aiohttp.TCPConnector(limit=32, ttl_dns_cache=300, enable_cleanup_closed=True)
        timeout = aiohttp.ClientTimeout(total=300, sock_connect=10, sock_read=60)
        _yt_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return _yt_session


async def load_apis():
    """Load and verify YouTube API 1 and YouTube API 2."""
    global PRIMARY_API_LOADED, FALLBACK_API_LOADED
    logger = LOGGER("VishalMusic.platforms.Youtube")

    if YOUTUBE_API_1:
        try:
            session = await _get_yt_session()
            async with session.get(f"{YOUTUBE_API_1}/", timeout=aiohttp.ClientTimeout(total=8)) as response:
                if response.status in (200, 404, 403, 401):
                    PRIMARY_API_LOADED = True
                    logger.info(f"✅ YouTube API 1 connected: {YOUTUBE_API_1}")
                else:
                    logger.warning(f"⚠️ YouTube API 1 status {response.status}")
        except Exception as e:
            logger.warning(f"⚠️ YouTube API 1 unreachable: {e}")

    if YOUTUBE_API_2:
        try:
            session = await _get_yt_session()
            async with session.get(f"{YOUTUBE_API_2}/", timeout=aiohttp.ClientTimeout(total=8)) as response:
                if response.status in (200, 404, 403, 401):
                    FALLBACK_API_LOADED = True
                    logger.info(f"✅ YouTube API 2 connected: {YOUTUBE_API_2}")
                else:
                    logger.warning(f"⚠️ YouTube API 2 status {response.status}")
        except Exception as e:
            logger.warning(f"⚠️ YouTube API 2 unreachable: {e}")

    return PRIMARY_API_LOADED, FALLBACK_API_LOADED

# Initialize APIs on startup
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(load_apis())
    else:
        loop.run_until_complete(load_apis())
except RuntimeError:
    pass

def _cookiefile_path() -> Optional[str]:
    path = str(COOKIE_PATH)
    try:
        if path and os.path.exists(path) and os.path.getsize(path) > 0:
            return path
    except Exception:
        pass
    return None

def _cookies_args() -> List[str]:
    args = [
        "--no-warnings",
        "--geo-bypass",
        "--force-ipv4",
        "--no-check-certificate",
        "--extractor-args", "youtube:player_client=android,ios,mweb,web_creator;player_skip=webpage,configs",
        "--user-agent", "com.google.android.youtube/19.29.35 (Linux; U; Android 14; en_US; Pixel 8 Pro)",
    ]
    p = _cookiefile_path()
    if p:
        args.extend(["--cookies", p])
    return args

async def _exec_proc(*args: str) -> Tuple[bytes, bytes]:
    proc = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        return await asyncio.wait_for(proc.communicate(), timeout=YTDLP_TIMEOUT)
    except asyncio.TimeoutError:
        with contextlib.suppress(Exception):
            proc.kill()
        return b"", b"timeout"

# Legacy sync alias removed â€” use _check_rate_limit_async() everywhere

# ============ UNIVERSAL API DOWNLOAD HELPER (Supports API 1 & API 2) ============
# ============ INSTANT ZERO-BANDWIDTH DIRECT API STREAMING ============
async def get_direct_stream_url(
    api_url: str,
    api_key: str,
    link: str,
    media_type: str = "audio",
    timeout_sec: int = 15,
) -> Optional[str]:
    """Acquire direct real-time stream URL from API without downloading locally."""
    if not api_url:
        return None
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None

    try:
        params = {"url": video_id, "type": media_type}
        if api_key:
            params["api_key"] = api_key

        headers = {}
        if api_key:
            headers["X-API-KEY"] = api_key

        timeout_obj = aiohttp.ClientTimeout(total=timeout_sec, sock_connect=8, sock_read=timeout_sec)
        session = await _get_yt_session()
        async with session.get(
            f"{api_url}/download",
            params=params,
            headers=headers,
            timeout=timeout_obj,
            allow_redirects=False,
        ) as response:
            if response.status in (301, 302, 303, 307, 308):
                location = response.headers.get("Location")
                if location and location.startswith("http"):
                    return location

            if response.status == 200:
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    data = await response.json()
                    stream_url = data.get("download_url") or data.get("url") or data.get("link") or data.get("stream_url")
                    if stream_url and isinstance(stream_url, str) and stream_url.startswith("http"):
                        return stream_url
                    
                    download_token = data.get("download_token") or data.get("token")
                    if download_token:
                        return f"{api_url}/stream/{video_id}?type={media_type}&token={download_token}"
                elif any(media in content_type for media in ("audio/", "video/", "application/octet-stream")):
                    key_param = f"&api_key={api_key}" if api_key else ""
                    return f"{api_url}/download?url={video_id}&type={media_type}{key_param}"
        return None
    except Exception as e:
        _module_logger.debug(f"Direct stream URL fetch error ({api_url}): {e}")
        return None


async def get_stream_url(link: str, media_type: str = "audio") -> Optional[str]:
    """Get direct stream URL via API 1 or API 2 (Zero Local Download)"""
    if YOUTUBE_API_1:
        url = await get_direct_stream_url(YOUTUBE_API_1, YOUTUBE_API_KEY_1, link, media_type)
        if url:
            _module_logger.info("⚡ Direct API 1 Stream URL Acquired")
            return url
    if YOUTUBE_API_2:
        url = await get_direct_stream_url(YOUTUBE_API_2, YOUTUBE_API_KEY_2, link, media_type)
        if url:
            _module_logger.info("⚡ Direct API 2 Stream URL Acquired")
            return url
    return None

async def _download_from_api(
    api_url: str,
    api_key: str,
    link: str,
    media_type: str = "audio",
    timeout_sec: int = 180,
) -> Optional[str]:
    """Universal downloader for YouTube API 1 and API 2.
    Supports: Direct binary download, JSON url/download_url, and token streaming.
    """
    if not api_url:
        return None
    video_id = link.split("v=")[-1].split("&")[0] if "v=" in link else link
    if not video_id or len(video_id) < 3:
        return None

    ext = "mp3" if media_type == "audio" else "mp4"
    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    try:
        params = {"url": video_id, "type": media_type}
        if api_key:
            params["api_key"] = api_key

        headers = {}
        if api_key:
            headers["X-API-KEY"] = api_key

        timeout_obj = aiohttp.ClientTimeout(total=timeout_sec, sock_connect=30, sock_read=timeout_sec)
        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.get(
                f"{api_url}/download",
                params=params,
                headers=headers,
            ) as response:
                if response.status != 200:
                    return None

                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    data = await response.json()
                    # 1. Direct stream URL in JSON
                    stream_url = data.get("download_url") or data.get("url") or data.get("link")
                    if stream_url:
                        async with session.get(stream_url) as s_resp:
                            if s_resp.status == 200:
                                async with aiofiles.open(file_path, "wb") as f:
                                    async for chunk in s_resp.content.iter_chunked(1 << 20):
                                        await f.write(chunk)
                                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                                    return file_path
                    # 2. Token-based streaming
                    download_token = data.get("download_token") or data.get("token")
                    if download_token:
                        async with session.get(
                            f"{api_url}/stream/{video_id}?type={media_type}",
                            headers={"X-Download-Token": download_token},
                        ) as s_resp:
                            if s_resp.status == 200:
                                async with aiofiles.open(file_path, "wb") as f:
                                    async for chunk in s_resp.content.iter_chunked(1 << 20):
                                        await f.write(chunk)
                                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                                    return file_path
                    return None
                else:
                    # Direct binary stream
                    async with aiofiles.open(file_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(1 << 20):  # 1 MB
                            await f.write(chunk)

                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        return file_path
        return None
    except Exception as e:
        _module_logger.debug(f"API download error ({api_url}): {e}")
        return None


# ============ API 1: YOUTUBE API 1 ============
async def download_song_primary_api(link: str) -> Optional[str]:
    """Download audio via YouTube API 1."""
    return await _download_from_api(
        YOUTUBE_API_1, YOUTUBE_API_KEY_1, link, media_type="audio", timeout_sec=120
    )


async def download_video_primary_api(link: str) -> Optional[str]:
    """Download video via YouTube API 1."""
    return await _download_from_api(
        YOUTUBE_API_1, YOUTUBE_API_KEY_1, link, media_type="video", timeout_sec=180
    )


# ============ API 2: YOUTUBE API 2 (FALLBACK) ============
async def download_song_fallback_api(link: str) -> Optional[str]:
    """Download audio via YouTube API 2."""
    return await _download_from_api(
        YOUTUBE_API_2, YOUTUBE_API_KEY_2, link, media_type="audio", timeout_sec=120
    )


async def download_video_fallback_api(link: str) -> Optional[str]:
    """Download video via YouTube API 2."""
    return await _download_from_api(
        YOUTUBE_API_2, YOUTUBE_API_KEY_2, link, media_type="video", timeout_sec=180
    )


# ============ YT-DLP FALLBACK ============
async def download_video_ytdlp(link: str) -> str:
    """Download video using yt-dlp directly"""
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link

    if not video_id or len(video_id) < 3:
        return None

    yt_link = f"https://www.youtube.com/watch?v={video_id}" if not link.startswith("http") else link
    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")

    if os.path.exists(file_path) and os.path.getsize(file_path) > 10240:
        return file_path

    await _check_rate_limit_async()

    try:
        ytdlp_opts = [
            "yt-dlp",
            *(_cookies_args()),
            "--no-warnings",
            "--geo-bypass",
            "--force-ipv4",
            "-f",
            "best[height<=?720][width<=?1280]/best",
            "-o",
            file_path,
            yt_link
        ]
        
        stdout, stderr = await _exec_proc(*ytdlp_opts)
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 10240:
            return file_path
        else:
            alternative_formats = ["best[ext=mp4]", "best", "worst[ext=mp4]", "worst"]
            
            for fmt in alternative_formats:
                try:
                    ytdlp_opts = [
                        "yt-dlp",
                        *(_cookies_args()),
                        "--no-warnings",
                        "--geo-bypass",
                        "--force-ipv4",
                        "-f",
                        fmt,
                        "-o",
                        file_path,
                        yt_link
                    ]
                    
                    stdout, stderr = await _exec_proc(*ytdlp_opts)
                    
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 10240:
                        return file_path
                    
                    await asyncio.sleep(1)
                except Exception:
                    continue
            
            return None

    except Exception as e:
        return None


async def download_audio_ytdlp(link: str) -> str:
    """Download audio using yt-dlp directly"""
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link

    if not video_id or len(video_id) < 3:
        return None

    yt_link = f"https://www.youtube.com/watch?v={video_id}" if not link.startswith("http") else link
    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.webm")

    if os.path.exists(file_path):
        return file_path

    await _check_rate_limit_async()
    
    try:
        ytdlp_opts = [
            "yt-dlp",
            *(_cookies_args()),
            "--no-warnings",
            "--geo-bypass",
            "--force-ipv4",
            "-f",
            "bestaudio[ext=webm]/bestaudio",
            "--extract-audio",
            "--audio-format", "webm",
            "-o",
            file_path,
            yt_link
        ]
        
        stdout, stderr = await _exec_proc(*ytdlp_opts)
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 10240:
            return file_path
        else:
            alternative_formats = ["bestaudio[ext=m4a]/bestaudio", "bestaudio/best", "worstaudio"]
            
            for fmt in alternative_formats:
                try:
                    alt_file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.webm")
                    ytdlp_opts = [
                        "yt-dlp",
                        *(_cookies_args()),
                        "--no-warnings",
                        "--geo-bypass",
                        "--force-ipv4",
                        "-f",
                        fmt,
                        "--extract-audio",
                        "--audio-format", "webm",
                        "-o",
                        alt_file_path,
                        yt_link
                    ]
                    
                    stdout, stderr = await _exec_proc(*ytdlp_opts)
                    
                    if os.path.exists(alt_file_path) and os.path.getsize(alt_file_path) > 10240:
                        return alt_file_path
                    
                    await asyncio.sleep(1)
                except Exception:
                    continue
            
            return None

    except Exception as e:
        return None


# ============ MAIN DOWNLOAD FUNCTIONS (API 1 -> API 2 -> YTDLP) ============
async def download_audio(link: str) -> Optional[str]:
    """Main audio download: YouTube API 1 -> YouTube API 2 -> yt-dlp fallback."""
    # 1. TRY YOUTUBE API 1
    if YOUTUBE_API_1:
        _module_logger.info("🎵 Audio Download - Trying YouTube API 1...")
        result = await download_song_primary_api(link)
        if result:
            _module_logger.info("✅ Audio: YouTube API 1 Success")
            return result

    # 2. TRY YOUTUBE API 2 (FALLBACK)
    if YOUTUBE_API_2:
        _module_logger.info("🔄 Audio - Trying YouTube API 2 (Fallback)...")
        result = await download_song_fallback_api(link)
        if result:
            _module_logger.info("✅ Audio: YouTube API 2 Success")
            return result

    # 3. TRY YT-DLP FALLBACK
    _module_logger.info("🔄 Audio - APIs unavailable or failed, trying yt-dlp fallback...")
    result = await download_audio_ytdlp(link)
    if result:
        _module_logger.info("✅ Audio: yt-dlp Success")
        if result.endswith(".webm"):
            mp3_path = result.replace(".webm", ".mp3")
            try:
                shutil.move(result, mp3_path)
                return mp3_path
            except Exception:
                return result
        return result

    _module_logger.info("❌ All audio download methods failed")
    return None


async def download_video(link: str) -> Optional[str]:
    """Main video download: YouTube API 1 -> YouTube API 2 -> yt-dlp fallback."""
    # 1. TRY YOUTUBE API 1
    if YOUTUBE_API_1:
        _module_logger.info("🎬 Video Download - Trying YouTube API 1...")
        result = await download_video_primary_api(link)
        if result:
            _module_logger.info("✅ Video: YouTube API 1 Success")
            return result

    # 2. TRY YOUTUBE API 2 (FALLBACK)
    if YOUTUBE_API_2:
        _module_logger.info("🔄 Video - Trying YouTube API 2 (Fallback)...")
        result = await download_video_fallback_api(link)
        if result:
            _module_logger.info("✅ Video: YouTube API 2 Success")
            return result

    # 3. TRY YT-DLP FALLBACK
    _module_logger.info("🔄 Video - APIs unavailable or failed, trying yt-dlp fallback...")
    result = await download_video_ytdlp(link)
    if result:
        _module_logger.info("✅ Video: yt-dlp Success")
        return result

    _module_logger.info("❌ All video download methods failed")
    return None


# ============ YOUTUBE API CLASS ============
@capture_internal_err
async def cached_youtube_search(query: str) -> List[Dict]:
    key = f"q:{query}"
    now = time.time()
    async with _cache_lock:
        if key in _cache:
            ts, val = _cache[key]
            if now - ts < YOUTUBE_META_TTL:
                return val
            _cache.pop(key, None)
        if len(_cache) > YOUTUBE_META_MAX:
            _cache.clear()
    try:
        data = await VideosSearch(query, limit=1).next()
        result = data.get("result", [])
    except Exception:
        result = []
    if result:
        async with _cache_lock:
            _cache[key] = (now, result)
    return result


@capture_internal_err
async def youtube_search_multi(query: str, limit: int = 8) -> List[Dict]:
    """
    Fetch multiple YouTube results for a query â€” used by autoplay so it can
    score and pick from a pool of candidates rather than always getting the
    same #1 result. Results are NOT cached (we want variety across calls).
    """
    try:
        data = await VideosSearch(query, limit=limit).next()
        return data.get("result", [])
    except Exception:
        return []

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")

class YouTubeAPI:
    def __init__(self) -> None:
        self.base_url = "https://www.youtube.com/watch?v="
        self.playlist_url = "https://youtube.com/playlist?list="
        self.status = "https://www.youtube.com/oembed?url="
        self._url_pattern = re.compile(r"(?:youtube\.com|youtu\.be)")
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def _prepare_link(self, link: str, videoid: Union[str, bool, None] = None) -> str:
        if isinstance(videoid, str) and videoid.strip():
            link = self.base_url + videoid.strip()
        if "youtu.be" in link:
            link = self.base_url + link.split("/")[-1].split("?")[0]
        elif "youtube.com/shorts/" in link or "youtube.com/live/" in link:
            link = self.base_url + link.split("/")[-1].split("?")[0]
        return link.split("&")[0]

    @capture_internal_err
    async def url(self, message: Message) -> Optional[str]:
        msgs = [message] + ([message.reply_to_message] if message.reply_to_message else [])
        for msg in msgs:
            text = msg.text or msg.caption or ""
            entities = msg.entities or msg.caption_entities or []
            for ent in entities:
                if ent.type == MessageEntityType.URL:
                    url = text[ent.offset : ent.offset + ent.length]
                    if self._url_pattern.search(url):
                        return url
                if ent.type == MessageEntityType.TEXT_LINK:
                    url = ent.url
                    if self._url_pattern.search(url):
                        return url
        return None

    @capture_internal_err
    async def exists(self, link: str, videoid: Union[str, bool, None] = None) -> bool:
        return bool(self._url_pattern.search(self._prepare_link(link, videoid)))

    @capture_internal_err
    async def _fetch_video_info(self, query: str, *, use_cache: bool = True) -> Optional[Dict]:
        q = self._prepare_link(query)
        if use_cache and not q.startswith("http"):
            res = await cached_youtube_search(q)
            return res[0] if res else None
        data = await VideosSearch(q, limit=1).next()
        result = data.get("result", [])
        return result[0] if result else None

    @capture_internal_err
    async def is_live(self, link: str) -> bool:
        await _check_rate_limit_async()
        prepared = self._prepare_link(link)
        stdout, _ = await _exec_proc("yt-dlp", *(_cookies_args()), "--dump-json", prepared)
        if not stdout:
            return False
        try:
            info = json.loads(stdout.decode())
            return bool(info.get("is_live"))
        except json.JSONDecodeError:
            return False

    @capture_internal_err
    async def details(self, link: str, videoid: Union[str, bool, None] = None) -> Tuple[str, Optional[str], int, str, str]:
        info = await self._fetch_video_info(self._prepare_link(link, videoid))
        if not info:
            raise ValueError("Video not found")
        dt = info.get("duration")
        ds = int(time_to_seconds(dt)) if dt else 0
        thumb = (info.get("thumbnail") or info.get("thumbnails", [{}])[0].get("url", "")).split("?")[0]
        return info.get("title", ""), dt, ds, thumb, info.get("id", "")

    @capture_internal_err
    async def title(self, link: str, videoid: Union[str, bool, None] = None) -> str:
        info = await self._fetch_video_info(self._prepare_link(link, videoid))
        return info.get("title", "") if info else ""

    @capture_internal_err
    async def duration(self, link: str, videoid: Union[str, bool, None] = None) -> Optional[str]:
        info = await self._fetch_video_info(self._prepare_link(link, videoid))
        return info.get("duration") if info else None

    @capture_internal_err
    async def thumbnail(self, link: str, videoid: Union[str, bool, None] = None) -> str:
        info = await self._fetch_video_info(self._prepare_link(link, videoid))
        if info:
            thumb = info.get("thumbnail") or info.get("thumbnails", [{}])[0].get("url", "")
            return thumb.split("?")[0] if thumb else ""
        return ""

    @capture_internal_err
    async def video(self, link: str, videoid: Union[str, bool, None] = None) -> Tuple[int, str]:
        link = self._prepare_link(link, videoid)
        
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return (1, downloaded_file)
        except Exception:
            pass
        
        await _check_rate_limit_async()
        
        ytdlp_args = [
            "yt-dlp", *(_cookies_args()), "--no-warnings", "--geo-bypass", "--force-ipv4",
            "-g", "-f", "best[height<=?720][width<=?1280]/best", link
        ]
        
        stdout, stderr = await _exec_proc(*ytdlp_args)
        
        if stdout:
            stream_url = stdout.decode().split("\n")[0]
            if stream_url and stream_url.startswith('http'):
                return (1, stream_url)
            else:
                return (0, "Invalid stream URL")
        else:
            error_msg = stderr.decode() if stderr else "Unknown error"
            if "429" in error_msg or "Too Many Requests" in error_msg:
                await asyncio.sleep(30)
                return (0, "Rate limited")
            elif "403" in error_msg:
                return await self._try_alternative_format(link)
            else:
                return (0, error_msg)

    async def _try_alternative_format(self, link: str) -> Tuple[int, str]:
        format_options = ["best[height<=480]", "best[ext=mp4]", "best", "worst"]
        for fmt in format_options:
            stdout, stderr = await _exec_proc("yt-dlp", *(_cookies_args()), "--no-warnings", "-g", "-f", fmt, link)
            if stdout:
                stream_url = stdout.decode().split("\n")[0]
                if stream_url and stream_url.startswith('http'):
                    return (1, stream_url)
            await asyncio.sleep(1)
        return (0, "All format attempts failed")

    @capture_internal_err
    async def playlist(self, link: str, limit: int, user_id, videoid: Union[str, bool, None] = None) -> List[str]:
        if videoid:
            link = self.playlist_url + str(videoid)
        link = link.split("&")[0]
        await _check_rate_limit_async()
        playlist = await shell_cmd(f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}")
        try:
            items = [key for key in playlist.split("\n") if key]
        except:
            items = []
        return items

    @capture_internal_err
    async def track(self, link: str, videoid: Union[str, bool, None] = None) -> Tuple[Dict, str]:
        try:
            info = await self._fetch_video_info(self._prepare_link(link, videoid))
            if not info:
                raise ValueError("Track not found via API")
        except Exception:
            await _check_rate_limit_async()
            prepared = self._prepare_link(link, videoid)
            stdout, _ = await _exec_proc("yt-dlp", *(_cookies_args()), "--dump-json", prepared)
            if not stdout:
                raise ValueError("Track not found (yt-dlp fallback)")
            info = json.loads(stdout.decode())
        thumb = (info.get("thumbnail") or info.get("thumbnails", [{}])[0].get("url", "")).split("?")[0]
        _dur = info.get("duration")
        if isinstance(_dur, str) and _dur:
            duration_min = _dur
        elif isinstance(_dur, (int, float)) and _dur > 0:
            _secs = int(_dur)
            duration_min = f"{_secs // 60}:{_secs % 60:02d}"
        else:
            duration_min = None
        details = {
            "title": info.get("title", ""),
            "link": info.get("webpage_url", self._prepare_link(link, videoid)),
            "vidid": info.get("id", ""),
            "duration_min": duration_min,
            "thumb": thumb,
        }
        return details, info.get("id", "")

    @capture_internal_err
    async def formats(self, link: str, videoid: Union[str, bool, None] = None) -> Tuple[List[Dict], str]:
        link = self._prepare_link(link, videoid)
        key = f"f:{link}"
        now = time.time()
        async with _formats_lock:
            cached = _formats_cache.get(key)
            if cached and now - cached[0] < YOUTUBE_META_TTL:
                return cached[1], cached[2]

        await _check_rate_limit_async()
        
        opts = {
            "quiet": True,
            "no_warnings": True,
            "geo_bypass": True,
            "force_ipv4": True,
            "nocheckcertificate": True,
            "source_address": "0.0.0.0",
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "ios", "mweb", "web_creator"],
                    "player_skip": ["webpage", "configs"],
                }
            },
            "http_headers": {
                "User-Agent": "com.google.android.youtube/19.29.35 (Linux; U; Android 14; en_US; Pixel 8 Pro)",
                "Accept-Language": "en-US,en;q=0.9",
            },
        }
        cf = _cookiefile_path()
        if cf:
            opts["cookiefile"] = cf
        out: List[Dict] = []
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                for fmt in info.get("formats", []):
                    if "dash" in str(fmt.get("format", "")).lower():
                        continue
                    if not any(k in fmt for k in ("filesize", "filesize_approx")):
                        continue
                    if not all(k in fmt for k in ("format", "format_id", "ext", "format_note")):
                        continue
                    size = fmt.get("filesize") or fmt.get("filesize_approx")
                    if not size:
                        continue
                    out.append({
                        "format": fmt["format"],
                        "filesize": size,
                        "format_id": fmt["format_id"],
                        "ext": fmt["ext"],
                        "format_note": fmt["format_note"],
                        "yturl": link,
                    })
        except Exception:
            pass

        async with _formats_lock:
            if len(_formats_cache) > YOUTUBE_META_MAX:
                _formats_cache.clear()
            _formats_cache[key] = (now, out, link)

        return out, link

    @capture_internal_err
    async def slider(self, link: str, query_type: int, videoid: Union[str, bool, None] = None) -> Tuple[str, Optional[str], str, str]:
        data = await VideosSearch(self._prepare_link(link, videoid), limit=10).next()
        results = data.get("result", [])
        if not results or query_type >= len(results):
            raise IndexError(f"Query type index {query_type} out of range (found {len(results)} results)")
        r = results[query_type]
        return (
            r.get("title", ""),
            r.get("duration"),
            r.get("thumbnails", [{}])[0].get("url", "").split("?")[0],
            r.get("id", ""),
        )

    @capture_internal_err
    async def download(
        self,
        link: str,
        mystic,
        *,
        video: Union[bool, str, None] = None,
        videoid: Union[str, bool, None] = None,
        songaudio: Union[bool, str, None] = None,
        songvideo: Union[bool, str, None] = None,
        format_id: Union[bool, str, None] = None,
        title: Union[bool, str, None] = None,
    ) -> Union[Tuple[str, Optional[bool]], Tuple[None, None]]:
        link = self._prepare_link(link, videoid)
        video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
        
        extension = ".webm" if not video else ".mp4"
        common_file_path = os.path.join("downloads", f"{video_id}{extension}")

        if os.path.exists(common_file_path) and os.path.getsize(common_file_path) > 10240:
            _module_logger.info("✅ Local cache")
            return common_file_path, True

        if songvideo or video:
            try:
                downloaded_file = await download_video(link)
                if downloaded_file and os.path.exists(downloaded_file):
                    _module_logger.info("✅ Video downloaded successfully")
                    if downloaded_file != common_file_path and downloaded_file.endswith('.mp4'):
                        try:
                            shutil.move(downloaded_file, common_file_path)
                            return common_file_path, True
                        except Exception:
                            return downloaded_file, True
                    return downloaded_file, True
            except Exception as e:
                _module_logger.info(f"❌ Video download error: {str(e)}")
            
            status, stream_url = await self.video(link)
            if status == 1:
                _module_logger.info("✅ Video stream fallback")
                return stream_url, None
            else:
                return None, None

        else:
            # ── 1. Lightweight Fast Async API Download (Primary + Secondary) ──
            try:
                downloaded = await download_audio(link)
                if downloaded and os.path.exists(downloaded) and os.path.getsize(downloaded) > 10240:
                    _module_logger.info("✅ Audio acquired via API")
                    if downloaded != common_file_path:
                        try:
                            shutil.move(downloaded, common_file_path)
                            return common_file_path, True
                        except Exception:
                            return downloaded, True
                    return downloaded, True
            except Exception as e:
                _module_logger.debug(f"API audio download failed: {e}")

            # ── 2. Sequential Fallback: Single Low-Memory yt-dlp ──
            try:
                downloaded = await yt_dlp_download(link, type="audio")
                if downloaded and os.path.exists(downloaded) and os.path.getsize(downloaded) > 10240:
                    _module_logger.info("✅ Audio downloaded via yt-dlp fallback")
                    if downloaded != common_file_path:
                        try:
                            shutil.move(downloaded, common_file_path)
                            return common_file_path, True
                        except Exception:
                            return downloaded, True
                    return downloaded, True
            except Exception as e:
                _module_logger.debug(f"yt-dlp fallback failed: {e}")

            _module_logger.info("❌ All audio download methods failed")
            return None, None

YouTube = YouTubeAPI()

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
