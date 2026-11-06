"""Branded Pinterest pin images (1000x1500) for each blog post, used by build_blog.py."""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path(__file__).resolve().parent / "fonts"
W, H = 1000, 1500
INK = (11, 11, 15)
INK2 = (82, 82, 90)
BG = (247, 247, 245)
ACCENT = (255, 91, 46)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_title(draw, text, max_w, max_h, start=86, min_size=48, face="InterDisplay-SemiBold.otf"):
    size = start
    while size >= min_size:
        f = font(face, size)
        lines = wrap(draw, text, f, max_w)
        lh = int(size * 1.08)
        if lh * len(lines) <= max_h:
            return f, lines, lh
        size -= 4
    f = font(face, min_size)
    return f, wrap(draw, text, f, max_w), int(min_size * 1.08)


def cover_crop(img, w, h, y_bias=0.5):
    img = img.convert("RGB")
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = (img.width - w) // 2
    y = int((img.height - h) * y_bias)
    return img.crop((x, y, x + w, y + h))


def rounded(img, r):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width - 1, img.height - 1), r, fill=255)
    out = Image.new("RGBA", img.size)
    out.paste(img, (0, 0), m)
    return out


def grain(img, strength=0.07):
    """Light film grain, like the website's gradient cards."""
    noise = Image.effect_noise(img.size, 64).convert("RGB")
    return Image.blend(img, noise, strength)


def mesh(w, h, palette, seed=3):
    """Soft blurred colour blobs like the website's gradient cards."""
    base = Image.new("RGB", (w // 4, h // 4), palette[1])
    d = ImageDraw.Draw(base)
    rnd = random.Random(seed)
    for c in palette[2:] + [palette[0]]:
        cx, cy = rnd.randint(0, w // 4), rnd.randint(0, h // 4)
        rx, ry = rnd.randint(w // 12, w // 6), rnd.randint(h // 16, h // 9)
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=c)
    base = base.filter(ImageFilter.GaussianBlur(34)).resize((w, h), Image.BICUBIC)
    base = ImageEnhance.Color(base).enhance(1.25)
    shade = Image.linear_gradient("L").resize((w, h)).point(lambda v: int(40 + v * 0.35))
    base = Image.composite(Image.new("RGB", (w, h), (12, 10, 30)), base, shade)
    return grain(base)


def footer(draw, y, dark=True):
    col = INK if dark else (255, 255, 255)
    sub = INK2 if dark else (235, 235, 245)
    f = font("InterDisplay-SemiBold.otf", 40)
    draw.text((70, y), "SHAHAB", font=f, fill=col)
    x = 70 + draw.textlength("SHAHAB", font=f)
    draw.text((x, y), ".", font=f, fill=ACCENT if dark else (255, 255, 255))
    m = font("DejaVuSansMono.ttf", 24)
    t = "abdullahshahab.com"
    draw.text((W - 70 - draw.textlength(t, font=m), y + 12), t, font=m, fill=sub)


def pin_photo(cover_path, kicker, title, out):
    img = Image.new("RGB", (W, H), BG)
    photo = rounded(cover_crop(Image.open(cover_path), W - 100, 820), 36)
    img.paste(photo, (50, 50), photo)
    d = ImageDraw.Draw(img)
    k = font("DejaVuSansMono.ttf", 26)
    d.text((70, 920), kicker.upper(), font=k, fill=ACCENT)
    f, lines, lh = fit_title(d, title, W - 140, 400)
    y = 972
    for ln in lines:
        d.text((70, y), ln, font=f, fill=INK)
        y += lh
    d.line((70, 1380, W - 70, 1380), fill=(228, 228, 222), width=2)
    footer(d, 1406)
    img.save(out, "JPEG", quality=86, optimize=True, progressive=True)


PALETTES = [
    [(100, 102, 214), (43, 44, 148), (75, 63, 192), (213, 157, 232), (143, 202, 249)],   # violet
    [(240, 138, 30), (196, 61, 12), (232, 103, 14), (255, 178, 63), (255, 227, 176)],   # orange
    [(236, 63, 145), (156, 15, 92), (255, 42, 150), (240, 96, 58), (255, 181, 156)],    # rose
    [(79, 116, 216), (29, 51, 146), (53, 87, 207), (135, 195, 247), (233, 245, 255)],   # ocean
]


def pin_bold(cover_path, kicker, headline, out, seed=0):
    img = mesh(W, H, PALETTES[seed % len(PALETTES)], seed=seed + 5)
    d = ImageDraw.Draw(img)
    k = font("DejaVuSansMono.ttf", 26)
    kt = kicker.upper()
    kw = d.textlength(kt, font=k)
    d.rounded_rectangle((70, 90, 70 + kw + 44, 140), 25, fill=(255, 255, 255))
    d.text((92, 101), kt, font=k, fill=INK)
    f, lines, lh = fit_title(d, headline, W - 140, 560, start=96, min_size=56)
    y = 190
    for ln in lines:
        d.text((70, y), ln, font=f, fill=(255, 255, 255))
        y += lh
    card = rounded(cover_crop(Image.open(cover_path), W - 140, 560), 30)
    shadow = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((40, 50, card.width + 40, card.height + 40), 30, fill=(20, 10, 60, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    img.paste(shadow, (30, 760), shadow)
    img.paste(card, (70, 790), card)
    footer(d, 1406, dark=False)
    img.save(out, "JPEG", quality=86, optimize=True, progressive=True)


def make_pins(post):
    """Create the pin images for a post; return [(rel_path, title, description), ...]."""
    out_dir = ROOT / "img" / "pins"
    out_dir.mkdir(parents=True, exist_ok=True)
    cover = ROOT / post["cover"]
    kicker = post.get("category", "Branding")
    pins = post.get("pins") or []
    a_title = pins[0]["title"] if len(pins) > 0 else post["title"]
    a_desc = pins[0].get("description", post["description"]) if len(pins) > 0 else post["description"]
    b_title = pins[1]["title"] if len(pins) > 1 else post["title"]
    b_desc = pins[1].get("description", post["description"]) if len(pins) > 1 else post["description"]
    a = out_dir / f"{post['slug']}-1.jpg"
    b = out_dir / f"{post['slug']}-2.jpg"
    if not a.exists() or post.get("rebuild_pins"):
        pin_photo(cover, kicker, a_title, a)
    if not b.exists() or post.get("rebuild_pins"):
        pin_bold(cover, kicker, b_title, b, seed=sum(map(ord, post["slug"])))
    return [(f"img/pins/{a.name}", a_title, a_desc), (f"img/pins/{b.name}", b_title, b_desc)]


def pin_portfolio(board_path, name, category, out, variant=1):
    """Portfolio pin: full brand board + zoomed detail + project name."""
    board = Image.open(board_path).convert("RGB")
    if variant == 1:
        img = Image.new("RGB", (W, H), BG)
        top = rounded(cover_crop(board, W - 100, 640), 30)
        img.paste(top, (50, 50), top)
        z = board.crop((int(board.width * .05), int(board.height * .05), int(board.width * .55), int(board.height * .55)))
        det = rounded(cover_crop(z, W - 100, 420), 30)
        img.paste(det, (50, 710), det)
        dark = False
    else:
        img = mesh(W, H, PALETTES[sum(map(ord, name)) % len(PALETTES)], seed=sum(map(ord, name)))
        card = rounded(cover_crop(board, W - 100, 760), 30)
        img.paste(card, (50, 300), card)
        dark = True
    d = ImageDraw.Draw(img)
    k = font("DejaVuSansMono.ttf", 26)
    if variant == 1:
        d.text((70, 1170), ("BRAND IDENTITY · " + category).upper()[:58], font=k, fill=ACCENT)
        f, lines, lh = fit_title(d, name, W - 140, 150, start=110, min_size=60)
        y = 1210
        for ln in lines[:1]:
            d.text((70, y), ln, font=f, fill=INK)
        d.line((70, 1380, W - 70, 1380), fill=(228, 228, 222), width=2)
        footer(d, 1406)
    else:
        kt = "BRAND IDENTITY"
        kw = d.textlength(kt, font=k)
        d.rounded_rectangle((70, 80, 70 + kw + 44, 130), 25, fill=(255, 255, 255))
        d.text((92, 91), kt, font=k, fill=INK)
        f, lines, lh = fit_title(d, name, W - 140, 130, start=104, min_size=60)
        d.text((70, 150), lines[0], font=f, fill=(255, 255, 255))
        s = font("Inter-Medium.otf", 32)
        d.text((70, 1110), category, font=s, fill=(255, 255, 255))
        d.text((70, 1160), "Human-designed · first brand board in 48 hours", font=font("Inter-Regular.otf", 28), fill=(235, 235, 245))
        footer(d, 1406, dark=False)
    img.save(out, "JPEG", quality=85, optimize=True, progressive=True)
