# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import asyncio
import os
import random
from typing import Optional, Tuple

import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

from config import YOUTUBE_IMG_URL
from VishalMusic.core.dir import CACHE_DIR

# Branding font
_FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "default.ttf")
_BRAND_TEXT = "≽ vaishali 𝘅 music ≼"

# Frame color presets (12 Rich vibrant aesthetic palettes)
FRAME_PRESETS = {
    "rose_pink": {
        "name": "🌸 Sakura Rose Glow",
        "primary": (255, 105, 180),
        "secondary": (255, 182, 193),
        "accent": (255, 20, 147),
    },
    "electric_cyan": {
        "name": "⚡ Electric Cyan Blue",
        "primary": (0, 210, 255),
        "secondary": (58, 123, 213),
        "accent": (0, 242, 254),
    },
    "aurora_purple": {
        "name": "💜 Aurora Violet Magic",
        "primary": (168, 85, 247),
        "secondary": (236, 72, 153),
        "accent": (192, 132, 252),
    },
    "sunset_orange": {
        "name": "🔥 Sunset Flame Glow",
        "primary": (249, 115, 22),
        "secondary": (234, 88, 12),
        "accent": (251, 146, 60),
    },
    "royal_gold": {
        "name": "👑 Royal Gold Luxury",
        "primary": (234, 179, 8),
        "secondary": (202, 138, 4),
        "accent": (250, 204, 21),
    },
    "emerald_green": {
        "name": "🌿 Emerald Neon Mint",
        "primary": (16, 185, 129),
        "secondary": (5, 150, 105),
        "accent": (52, 211, 153),
    },
    "crimson_red": {
        "name": "🌹 Crimson Ruby Red",
        "primary": (239, 68, 68),
        "secondary": (220, 38, 38),
        "accent": (248, 113, 113),
    },
    "cyber_magenta": {
        "name": "💖 Cyberpunk Magenta",
        "primary": (217, 70, 239),
        "secondary": (192, 38, 211),
        "accent": (244, 114, 182),
    },
    "deep_violet": {
        "name": "🔮 Mystic Deep Violet",
        "primary": (139, 92, 246),
        "secondary": (109, 40, 217),
        "accent": (167, 139, 250),
    },
    "ice_blue": {
        "name": "❄️ Glacier Frost Blue",
        "primary": (56, 189, 248),
        "secondary": (2, 132, 199),
        "accent": (125, 211, 252),
    },
    "lime_spark": {
        "name": "✨ Neon Lime Spark",
        "primary": (132, 204, 22),
        "secondary": (101, 163, 13),
        "accent": (163, 230, 53),
    },
    "coral_peach": {
        "name": "🍑 Sunset Peach Coral",
        "primary": (251, 113, 133),
        "secondary": (244, 63, 94),
        "accent": (253, 164, 175),
    },
}

_last_frame_color: Optional[str] = None


def _next_frame_color() -> str:
    """Returns a different random frame color from the palette every time."""
    global _last_frame_color
    available = [k for k in FRAME_PRESETS.keys() if k != _last_frame_color]
    chosen = random.choice(available) if available else random.choice(list(FRAME_PRESETS.keys()))
    _last_frame_color = chosen
    return chosen

# Shared persistent session
_thumb_session: Optional[aiohttp.ClientSession] = None
_thumb_session_lock = asyncio.Lock()


async def _get_session() -> aiohttp.ClientSession:
    global _thumb_session
    if _thumb_session and not _thumb_session.closed:
        return _thumb_session
    async with _thumb_session_lock:
        if _thumb_session and not _thumb_session.closed:
            return _thumb_session
        connector = aiohttp.TCPConnector(limit=32, ttl_dns_cache=300)
        timeout = aiohttp.ClientTimeout(total=15, sock_connect=5, sock_read=10)
        _thumb_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return _thumb_session


def standardize_thumbnail(img: Image.Image) -> Image.Image:
    """Auto-detects and crops YouTube letterbox bars, then fits into exact 1280x720 HD 16:9 canvas."""
    w, h = img.size
    # If standard 480x360 hqdefault (which has 45px black bars top and bottom)
    if w == 480 and h == 360:
        img = img.crop((0, 45, 480, 315))
    elif w == 640 and h == 480:
        img = img.crop((0, 60, 640, 420))
    elif h > 0 and abs(w / h - 4 / 3) < 0.05:
        # Generic 4:3 letterbox crop to 16:9
        bar_h = int(h * 0.125)
        img = img.crop((0, bar_h, w, h - bar_h))

    # Fit into exact standard 1280x720 (16:9)
    fitted = ImageOps.fit(img, (1280, 720), method=Image.Resampling.LANCZOS)
    return fitted


def _draw_top_rounded_rect(draw: ImageDraw.ImageDraw, xy, radius: int, fill=None, outline=None, width: int = 1):
    """Draws a rectangle with rounded top corners and 90-degree sharp square bottom corners."""
    try:
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width, corners=(True, True, False, False))
    except TypeError:
        x0, y0, x1, y1 = xy
        d = radius * 2
        if fill:
            draw.rectangle([x0, y0 + radius, x1, y1], fill=fill)
            draw.rectangle([x0 + radius, y0, x1 - radius, y0 + radius], fill=fill)
            draw.pieslice([x0, y0, x0 + d, y0 + d], 180, 270, fill=fill)
            draw.pieslice([x1 - d, y0, x1, y0 + d], 270, 360, fill=fill)
        if outline and width > 0:
            draw.line([(x0 + radius, y0), (x1 - radius, y0)], fill=outline, width=width)
            draw.line([(x1, y0 + radius), (x1, y1)], fill=outline, width=width)
            draw.line([(x1, y1), (x0, y1)], fill=outline, width=width)
            draw.line([(x0, y1), (x0, y0 + radius)], fill=outline, width=width)
            draw.arc([x0, y0, x0 + d, y0 + d], 180, 270, fill=outline, width=width)
            draw.arc([x1 - d, y0, x1, y0 + d], 270, 360, fill=outline, width=width)


def _add_aesthetic_frame(image: Image.Image, frame_key: str = None) -> Image.Image:
    """Applies a sleek, thin glowing aesthetic border frame with smooth curved top corners and 90-degree square bottom corners."""
    # Ensure standard base dimensions
    image = standardize_thumbnail(image)
    if not frame_key or frame_key not in FRAME_PRESETS:
        frame_key = _next_frame_color()

    preset = FRAME_PRESETS[frame_key]
    c1 = preset["primary"]
    c2 = preset["secondary"]
    c_accent = preset["accent"]

    w, h = image.size
    # Thin frame settings: 4px border, smooth curved top corners (32px radius), sharp 90-degree bottom corners
    border_thickness = 4
    corner_radius = 32

    pad = border_thickness * 2
    canvas_w = w + pad * 2
    canvas_h = h + pad * 2
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (12, 12, 18, 255))

    # 1. Subtle Glow layer (top smoothly rounded, bottom 90 deg)
    glow = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    _draw_top_rounded_rect(
        glow_draw,
        [pad - 2, pad - 2, canvas_w - pad + 2, canvas_h - pad + 2],
        radius=corner_radius + 2,
        outline=(*c1, 140),
        width=border_thickness + 2,
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius=3))
    canvas = Image.alpha_composite(canvas, glow)

    # 2. Base rounded image mask (top smoothly rounded, bottom 90-degree square)
    mask = Image.new("L", (w, h), 0)
    mask_draw = ImageDraw.Draw(mask)
    _draw_top_rounded_rect(mask_draw, [0, 0, w, h], radius=corner_radius, fill=255)

    rounded_image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rounded_image.paste(image.convert("RGBA"), (0, 0), mask=mask)
    canvas.paste(rounded_image, (pad, pad), mask=mask)

    # 3. Outer Thin Border & Accent line (top smoothly rounded, bottom 90-degree square)
    border_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(border_layer)

    # Outer thin border
    _draw_top_rounded_rect(
        bdraw,
        [pad, pad, pad + w, pad + h],
        radius=corner_radius,
        outline=(*c1, 255),
        width=border_thickness,
    )
    # Inner thin bright accent line
    inner_pad = pad + border_thickness - 1
    _draw_top_rounded_rect(
        bdraw,
        [inner_pad, inner_pad, canvas_w - inner_pad, canvas_h - inner_pad],
        radius=max(0, corner_radius - border_thickness),
        outline=(*c_accent, 180),
        width=1,
    )
    canvas = Image.alpha_composite(canvas, border_layer)

    return canvas.convert("RGB")


async def get_thumb(videoid: str, frame_color: Optional[str] = None) -> str:
    # Pick a new distinct frame color on each play
    frame_key = frame_color if (frame_color and frame_color in FRAME_PRESETS) else _next_frame_color()
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_{frame_key}.png")
    if os.path.exists(cache_path):
        return cache_path

    thumbnail_urls = [
        f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{videoid}/hqdefault.jpg",
        f"https://img.youtube.com/vi/{videoid}/sddefault.jpg",
        f"https://img.youtube.com/vi/{videoid}/mqdefault.jpg",
    ]

    session = await _get_session()
    thumb_path = os.path.join(CACHE_DIR, f"raw_{videoid}.jpg")
    downloaded = False

    for url in thumbnail_urls:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(thumb_path, "wb") as f:
                        await f.write(await resp.read())
                    downloaded = True
                    break
        except Exception:
            continue

    if not downloaded:
        return YOUTUBE_IMG_URL

    try:
        raw_img = Image.open(thumb_path).convert("RGBA")
        framed_img = _add_aesthetic_frame(raw_img, frame_key)
        framed_img.save(cache_path, "PNG", quality=95)
    except Exception:
        return YOUTUBE_IMG_URL
    finally:
        try:
            os.remove(thumb_path)
        except OSError:
            pass

    return cache_path


async def get_thumb_url(videoid: str) -> str:
    """Returns local standardized framed thumbnail path, or fallback URL."""
    try:
        cached = await get_thumb(videoid)
        if cached and os.path.exists(cached):
            return cached
    except Exception:
        pass
    return f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg"

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
