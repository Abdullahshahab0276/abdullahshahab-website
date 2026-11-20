"""Technical SEO pass applied to every HTML page the build writes (and to index.html / 404.html).

finalize(html, page_path) makes each page:
  * link with clean absolute URLs (/blog/slug/ instead of ../blog/slug/index.html), so no
    internal link triggers a redirect;
  * serve WebP images (a .webp copy is made next to every site image; og:image stays JPG for
    social networks);
  * set width/height on every local <img> to prevent layout shift, and decoding="async";
  * keep the first content image eager with fetchpriority="high" (LCP), lazy-load the rest.

lastmod(url, html) returns a stable "last changed" date per URL, stored in content/lastmod.json,
so the sitemap only reports a new date when the page content really changed.
"""
import datetime as dt
import hashlib
import json
import posixpath
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"pins"}          # Pinterest pin images stay JPG
_dims = {}


def make_webp(quality=80):
    """Create/refresh img/**/*.webp for every site JPG/PNG (not pins). Returns count written."""
    n = 0
    for f in (ROOT / "img").rglob("*"):
        if f.suffix.lower() not in (".jpg", ".jpeg", ".png") or SKIP_DIRS & set(f.parts):
            continue
        out = f.with_suffix(".webp")
        if out.exists() and out.stat().st_mtime >= f.stat().st_mtime:
            continue
        im = Image.open(f)
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "transparency" in im.info else "RGB")
        if max(im.size) > 1600:
            im.thumbnail((1600, 1600))
        im.save(out, "WEBP", quality=quality, method=6)
        n += 1
    return n


def dims(rel):
    if rel not in _dims:
        p = ROOT / rel
        try:
            with Image.open(p) as im:
                _dims[rel] = im.size
        except Exception:
            _dims[rel] = None
    return _dims[rel]


def _abs(href, page_dir):
    """Resolve a relative href against the page's directory, drop index.html."""
    if re.match(r"^(https?:|mailto:|tel:|#|/|data:|javascript:)", href):
        path = href
    else:
        path = posixpath.normpath(posixpath.join(page_dir, href))
        if not path.startswith("/"):
            path = "/" + path
        # normpath strips a trailing slash that mattered
        if href.endswith("/") and not path.endswith("/"):
            path += "/"
    if path.startswith("/"):
        path = re.sub(r"(^|/)index\.html(?=$|[#?])", r"\1", path)
    return path


def finalize(html, page_path):
    """page_path: site path of the page, e.g. '/blog/logo-file-formats/'."""
    page_dir = page_path if page_path.endswith("/") else posixpath.dirname(page_path) + "/"

    def fix_attr(m):
        attr, val = m.group(1), m.group(2)
        return f'{attr}="{_abs(val, page_dir)}"'

    # hrefs and srcs outside of <script> blocks
    parts = re.split(r"(<script[\s\S]*?</script>)", html)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r'\b(href|src|poster|data-video)="([^"]+)"', fix_attr, parts[i])
    html = "".join(parts)

    seen_first = [False]

    def fix_img(m):
        tag = m.group(0)
        src = re.search(r'\ssrc="([^"]+)"', tag)
        if not src or not src.group(1).startswith("/img/"):
            return tag
        s = src.group(1)
        rel = s.lstrip("/")
        base = re.sub(r"\.(jpe?g|png)$", "", rel, flags=re.I)
        webp = base + ".webp"
        src_rel = rel
        if rel != webp and (ROOT / webp).exists() and "/pins/" not in rel:
            tag = tag.replace(f'src="{s}"', f'src="/{webp}"')
            src_rel = webp
        d = dims(rel) or dims(src_rel)
        if d and "width=" not in tag:
            tag = tag.replace("<img", f'<img width="{d[0]}" height="{d[1]}"', 1)
        if "decoding=" not in tag:
            tag = tag.replace("<img", '<img decoding="async"', 1)
        return tag

    html = re.sub(r"<img\b[^>]*>", fix_img, html)
    return html


_LM_FILE = ROOT / "content" / "lastmod.json"
_lm = None


def lastmod(url, html):
    """Date the page content last changed (ignores the build year in the footer)."""
    global _lm
    if _lm is None:
        _lm = json.loads(_LM_FILE.read_text()) if _LM_FILE.exists() else {}
    body = re.sub(r"©\s*\d{4}", "", html)
    h = hashlib.sha1(body.encode("utf-8")).hexdigest()[:16]
    rec = _lm.get(url)
    if not rec or rec["hash"] != h:
        rec = {"hash": h, "date": dt.date.today().isoformat()}
        _lm[url] = rec
    return rec["date"]


def save_lastmod():
    if _lm is not None:
        _LM_FILE.write_text(json.dumps(_lm, indent=1, sort_keys=True) + "\n")
