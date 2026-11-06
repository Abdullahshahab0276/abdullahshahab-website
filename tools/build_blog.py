#!/usr/bin/env python3
"""Build the blog for abdullahshahab.com.

Write posts as Markdown files in content/posts/ (front matter at the top),
then run:   python3 tools/build_blog.py
It (re)generates:
  blog/index.html, blog/<slug>/index.html, blog/feed.xml,
  css/main.css (copied from index.html so the blog always matches the site),
  sitemap.xml, robots.txt
"""
import datetime as dt
import sys
import html
import json
import math
import re
from pathlib import Path

import markdown
import yaml

from pins import make_pins

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
SITE = "https://www.abdullahshahab.com"
AUTHOR = "Shahab"
CAL = "https://calendly.com/imabdullahshahab/30min"
POSTS_DIR = ROOT / "content" / "posts"


def esc(s):
    return html.escape(str(s), quote=True)


def load_posts():
    posts = []
    for f in sorted(POSTS_DIR.glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        if not m:
            raise SystemExit(f"{f.name}: missing front matter")
        meta = yaml.safe_load(m.group(1))
        body = m.group(2).strip()
        meta.setdefault("slug", f.stem)
        if meta.get("draft"):
            continue
        d = meta["date"]
        meta["date"] = d if isinstance(d, dt.date) else dt.date.fromisoformat(str(d))
        u = meta.get("updated", meta["date"])
        meta["updated"] = u if isinstance(u, dt.date) else dt.date.fromisoformat(str(u))
        words = len(re.findall(r"\w+", body))
        meta["read"] = max(1, math.ceil(words / 230))
        md = markdown.Markdown(extensions=["toc", "tables", "sane_lists", "smarty"])
        meta["html"] = md.convert(body)
        meta["toc"] = [t for t in md.toc_tokens if t["level"] == 2]
        posts.append(meta)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def site_parts():
    """Pull the stylesheet and icon sprite out of the homepage so the blog matches it."""
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", page, re.S).group(1)
    sprite = re.search(r'(<svg width="0" height="0".*?</svg>)\n', page, re.S).group(1)
    return css, sprite


BLOG_CSS = """
/* ---------- blog ---------- */
.crumbs{font:400 12.5px var(--mono);color:var(--ink-3);letter-spacing:.04em;margin:44px 0 26px;display:flex;gap:8px;flex-wrap:wrap}
.crumbs a{color:var(--ink-2);text-decoration:none}
.art-head{max-width:860px}
.art-head h1{font-size:clamp(38px,3.2vw + 14px,64px);max-width:none}
.art-head{max-width:980px}
.meta-row{display:flex;align-items:center;gap:14px;margin-top:28px}
.meta-row img{flex:none}
.meta-row img{width:44px;height:44px;border-radius:50%;object-fit:cover}
.meta-row b{display:block;font-weight:500;font-size:15.5px}
.meta-row small{font:400 12px var(--mono);color:var(--ink-3)}
.tagc{font:500 11.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;padding:6px 11px;border-radius:999px;background:#fff;box-shadow:0 0 0 1px var(--line);color:var(--ink-2);display:inline-block}
.cover{margin:40px 0 0;border-radius:var(--r-xl);overflow:hidden;aspect-ratio:16/8;background:#111}
.cover img{width:100%;height:100%;object-fit:cover}
.art-wrap{display:grid;grid-template-columns:minmax(0,1fr) 280px;gap:64px;align-items:start;margin-top:56px}
.toc{position:sticky;top:96px;padding:22px;border-radius:22px}
.toc h4{margin:0 0 12px;font:400 11.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3)}
.toc a{display:block;padding:6px 0;font-size:14.5px;color:var(--ink-2);text-decoration:none;line-height:1.35}
.toc a:hover{color:var(--ink)}
.toc .btn{width:100%;margin-top:16px}
.prose{font-size:18.5px;line-height:1.7;color:#24242b;letter-spacing:-.012em;max-width:720px}
.prose>*:first-child{margin-top:0}
.prose p{margin:0 0 1.15em}
.prose h2{font-size:clamp(27px,1vw + 20px,34px);font-weight:450;letter-spacing:-.035em;line-height:1.15;margin:2em 0 .6em;scroll-margin-top:96px}
.prose h3{font-size:22px;font-weight:500;margin:1.6em 0 .5em}
.prose a{color:var(--ink);text-decoration-color:rgba(75,63,227,.45);text-underline-offset:3px;text-decoration-thickness:1.5px}
.prose a:hover{text-decoration-color:#4b3fe3}
.prose strong{font-weight:600;color:var(--ink)}
.prose ul,.prose ol{padding-left:1.25em;margin:0 0 1.2em}
.prose li{margin:.45em 0;padding-left:.2em}
.prose li::marker{color:#8d4ee6}
.prose blockquote{margin:1.6em 0;padding:22px 26px;border-radius:18px;background:#fff;box-shadow:0 0 0 1px var(--line);font-size:20px;letter-spacing:-.02em}
.prose em{font-style:italic}
.prose hr{border:0;border-top:1px solid var(--frame);margin:2.4em 0}
.prose p:last-child em{color:var(--ink-2)}
.art-cta{margin:56px 0 0;border-radius:var(--r-xl);padding:36px 34px;color:#fff;display:grid;gap:14px}
.art-cta h2{color:#fff;font-size:clamp(28px,1.4vw + 18px,38px);letter-spacing:-.04em}
.art-cta p{margin:0;opacity:.9;max-width:34em}
.art-cta .row{display:flex;gap:10px;flex-wrap:wrap;margin-top:8px}
.art-cta .btn.ghostw{background:rgba(255,255,255,.14);color:#fff;box-shadow:inset 0 0 0 1px rgba(255,255,255,.35)}
.posts{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.post{display:flex;flex-direction:column;text-decoration:none;border-radius:var(--r-xl);overflow:hidden;background:#fff;box-shadow:0 0 0 1px var(--line);transition:transform .3s var(--ease),box-shadow .3s}
.post:hover{transform:translateY(-3px);box-shadow:0 0 0 1px var(--line),var(--shadow-2)}
.post .im{aspect-ratio:16/10;overflow:hidden;background:#111}
.post .im img{width:100%;height:100%;object-fit:cover}
.post .tx{padding:22px 22px 26px;display:grid;gap:10px}
.post h3{font-size:21px;font-weight:450;letter-spacing:-.03em;line-height:1.25}
.post p{margin:0;color:var(--ink-2);font-size:15px;line-height:1.5}
.post small{font:400 12px var(--mono);color:var(--ink-3)}
.post.lead{grid-column:1/-1;display:grid;grid-template-columns:1.3fr 1fr}
.post.lead .im{aspect-ratio:auto;min-height:340px}
.post.lead .tx{padding:36px;align-content:center}
.post.lead h3{font-size:clamp(26px,1.4vw + 16px,36px);letter-spacing:-.04em}
.empty-note{text-align:center;color:var(--ink-3);font:400 13px var(--mono);margin-top:26px}
@media(max-width:1000px){.art-wrap{grid-template-columns:1fr}.toc{position:static;order:-1}.posts{grid-template-columns:1fr 1fr}.post.lead{grid-template-columns:1fr}.post.lead .im{min-height:0;aspect-ratio:16/10}}
@media(max-width:640px){.posts{grid-template-columns:1fr}.prose{font-size:17.5px}.cover{aspect-ratio:4/3}.art-cta{padding:28px 22px}}
"""


def nav(root):
    return f"""<div class="notice"><div class="inner"><span class="dot"></span><span>Human-designed branding · first brand board in <b>48 hours</b></span></div></div>
<nav class="nav" id="nav"><div class="inner">
  <a class="logo" href="{root}index.html">SHAHAB<i>.</i></a>
  <div class="links">
    <a href="{root}index.html#work">Work</a><a href="{root}index.html#pricing">Packages</a><a href="{root}index.html#process">How it works</a><a href="{root}index.html#reviews">Reviews</a><a href="{root}blog/index.html">Blog</a><a href="{root}index.html#faq">FAQ</a>
  </div>
  <div class="acts">
    <a class="btn ghost sm" href="{CAL}" target="_blank" rel="noopener">Book a call</a>
    <a class="btn primary sm" href="{root}index.html#pricing">Start my brand</a>
  </div>
  <button class="burger" id="burger" aria-label="Menu"><svg width="18" height="18" viewBox="0 0 18 18"><path d="M2 5h14M2 9h14M2 13h14" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg></button>
</div></nav>
<div class="mnav" id="mnav">
  <a href="{root}index.html#work">Work</a><a href="{root}index.html#pricing">Packages</a><a href="{root}index.html#process">How it works</a><a href="{root}index.html#reviews">Reviews</a><a href="{root}blog/index.html">Blog</a><a href="{root}index.html#faq">FAQ</a><a href="{root}index.html#contact">Contact</a>
  <a class="btn primary" href="{CAL}" target="_blank" rel="noopener" style="margin-top:6px">Book a call</a>
</div>"""


def footer(root):
    y = dt.date.today().year
    return f"""<footer>
  <div class="inner">
    <div class="fcols">
      <div>
        <a class="logo" href="{root}index.html">SHAHAB<i>.</i></a>
        <p>Human-designed premium branding, logo systems, packaging and content for businesses that want to look established.</p>
        <div class="soc">
          <a href="https://www.instagram.com/imabdullahshahab" target="_blank" rel="noopener" aria-label="Instagram"><svg><use href="#i-ig"/></svg></a>
          <a href="https://wa.me/923118440498" target="_blank" rel="noopener" aria-label="WhatsApp"><svg><use href="#i-wa"/></svg></a>
          <a href="mailto:imabdullahshahab@gmail.com" aria-label="Email"><svg><use href="#i-mail"/></svg></a>
        </div>
      </div>
      <div class="fcol"><h4>Explore</h4><a href="{root}index.html#work">Featured work</a><a href="{root}index.html#process">How it works</a><a href="{root}index.html#reviews">Reviews</a><a href="{root}index.html#cases">Case studies</a><a href="{root}blog/index.html">Blog</a><a href="{root}index.html#faq">FAQ</a></div>
      <div class="fcol"><h4>Packages</h4><a href="{root}index.html#pricing">Basic plan · $250</a><a href="{root}index.html#pricing">Premium Branding · $450</a><a href="{root}index.html#pricing">Brand Ecosystem · $1,050</a><a href="{root}index.html#contact">Custom quote</a></div>
      <div class="fcol"><h4>Contact</h4><a href="mailto:imabdullahshahab@gmail.com">imabdullahshahab@gmail.com</a><a href="https://wa.me/923118440498" target="_blank" rel="noopener">WhatsApp: 03118440498</a><a href="https://www.instagram.com/imabdullahshahab" target="_blank" rel="noopener">Instagram @imabdullahshahab</a><a href="{CAL}" target="_blank" rel="noopener">Book a call</a></div>
    </div>
    <div class="fbot"><span>© {y} Shahab. All rights reserved.</span><a href="#top">Designed by a person, not a prompt. ↑</a></div>
  </div>
</footer>"""


JS = """<script>
(function(){var n=document.getElementById('nav');function s(){n.classList.toggle('scrolled',scrollY>10)}addEventListener('scroll',s,{passive:true});s();
var b=document.getElementById('burger'),m=document.getElementById('mnav');b.onclick=function(){m.classList.toggle('open')};
if('IntersectionObserver' in window){var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');o.unobserve(e.target)}})},{threshold:.1});document.querySelectorAll('.rv-up').forEach(function(el){o.observe(el)})}else document.querySelectorAll('.rv-up').forEach(function(el){el.classList.add('in')});})();
</script>"""


def head(root, title, desc, url, image, extra=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#f7f7f5">
<meta property="og:type" content="{'article' if '/blog/' in url and not url.endswith('/blog/') else 'website'}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/{image}">
<meta property="og:site_name" content="Shahab">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="Shahab blog" href="{SITE}/blog/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}css/main.css">
{extra}
</head>"""


def post_card(p, root, lead=False):
    return f"""<a class="post{' lead' if lead else ''} rv-up" href="{root}blog/{p['slug']}/index.html">
  <div class="im"><img src="{root}{p['cover']}" alt="{esc(p.get('cover_alt',''))}" loading="lazy"></div>
  <div class="tx"><span class="tagc" style="justify-self:start">{esc(p.get('category','Branding'))}</span><h3>{esc(p['title'])}</h3><p>{esc(p['description'])}</p><small>{p['date'].strftime('%b %-d, %Y')} · {p['read']} min read</small></div>
</a>"""


def build_post(p, posts, sprite):
    root = "../../"
    url = f"{SITE}/blog/{p['slug']}/"
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BlogPosting",
                "headline": p["title"],
                "description": p["description"],
                "image": f"{SITE}/{p['cover']}",
                "datePublished": p["date"].isoformat(),
                "dateModified": p["updated"].isoformat(),
                "author": {"@type": "Person", "name": AUTHOR, "url": SITE + "/", "image": f"{SITE}/img/shahab.jpg"},
                "publisher": {"@type": "Organization", "name": "Shahab", "url": SITE + "/"},
                "mainEntityOfPage": url,
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                    {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"},
                    {"@type": "ListItem", "position": 3, "name": p["title"], "item": url},
                ],
            },
        ],
    }
    extra = f'<meta property="article:published_time" content="{p["date"].isoformat()}">\n<script type="application/ld+json">{json.dumps(ld)}</script>'
    toc = "".join(f'<a href="#{t["id"]}">{esc(html.unescape(t["name"]))}</a>' for t in p["toc"])
    related = [q for q in posts if q["slug"] != p["slug"]][:3]
    rel_html = ""
    if related:
        rel_html = f"""<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Keep reading</h2></div><div class="posts">{''.join(post_card(q, root) for q in related)}</div></div></section>"""
    page = f"""{head(root, p['title'] + ' | Shahab', p['description'], url, p['cover'], extra)}
<body>
{sprite}
{nav(root)}
<div class="page" id="top"><div class="rails"></div>
<section class="hero" style="padding-bottom:0"><div class="aura"><i></i><i></i><i></i><i></i></div>
<div class="inner">
  <div class="crumbs"><a href="{root}index.html">Home</a><span>/</span><a href="{root}blog/index.html">Blog</a><span>/</span><span>{esc(p.get('category','Branding'))}</span></div>
  <div class="art-head">
    <span class="tagc">{esc(p.get('category','Branding'))}</span>
    <h1 style="margin-top:18px">{esc(p['title'])}</h1>
    <p class="lede" style="margin-top:22px">{esc(p['description'])}</p>
    <div class="meta-row"><img src="{root}img/shahab-sm.jpg" alt="Shahab"><span><b>Shahab</b><small>Brand designer · {p['date'].strftime('%B %-d, %Y')} · {p['read']} min read</small></span></div>
  </div>
  <div class="cover"><img src="{root}{p['cover']}" alt="{esc(p.get('cover_alt',''))}"></div>
</div></section>
<section style="position:relative;z-index:1;padding:0 0 96px"><div class="inner">
  <div class="art-wrap">
    <article class="prose">{p['html']}
      <div class="art-cta g g-violet">
        <h2>Want a logo you actually own?</h2>
        <p>Human-designed brand identities with full source files and copyright included. First brand board in 48 hours, from $250.</p>
        <div class="row"><a class="btn white" href="{CAL}" target="_blank" rel="noopener">Book a call <span class="ar"><svg><use href="#i-arrow"/></svg></span></a><a class="btn ghostw" href="{root}index.html#pricing">See packages</a></div>
      </div>
    </article>
    <aside class="toc card"><h4>In this article</h4>{toc}<a class="btn primary sm" href="{root}index.html#pricing">Start my brand</a></aside>
  </div>
</div></section>
{rel_html}
{footer(root)}
</div>
{JS}
</body>
</html>"""
    out = ROOT / "blog" / p["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")


def build_index(posts, sprite):
    root = "../"
    url = f"{SITE}/blog/"
    desc = "Practical guides on logos, brand identity, pricing and launching a brand that looks established, from Shahab, a human brand designer."
    cards = "".join(post_card(p, root, lead=(i == 0)) for i, p in enumerate(posts))
    note = '<p class="empty-note">New articles every week.</p>'
    ld = {"@context": "https://schema.org", "@type": "Blog", "name": "Shahab blog", "url": url, "description": desc,
          "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/blog/{p['slug']}/", "datePublished": p["date"].isoformat()} for p in posts]}
    page = f"""{head(root, 'Branding blog: logos, identity and launch guides | Shahab', desc, url, posts[0]['cover'] if posts else 'img/a018.jpg', '<script type="application/ld+json">' + json.dumps(ld) + '</script>')}
<body>
{sprite}
{nav(root)}
<div class="page" id="top"><div class="rails"></div>
<section class="hero"><div class="aura"><i></i><i></i><i></i><i></i></div>
<div class="inner">
  <div class="head" style="margin-top:56px">
    <span class="kick" style="margin:0">The Shahab blog</span>
    <h1 style="text-align:center;max-width:14em">Branding, <span class="grad">explained.</span></h1>
    <p class="lede">Straight answers on logos, brand identity, pricing and launching a brand that looks established. Written by a designer, not a prompt.</p>
  </div>
  <div class="posts" style="padding-bottom:96px">{cards}</div>
  {note}
</div></section>
<section class="band"><div class="inner"><div class="callout g g-orange" style="margin-top:0">
  <div><h2>Ready for a brand you actually own?</h2><p>Human-designed identities, source files and copyright included. First brand board in 48 hours.</p></div>
  <a class="btn white lg" href="{root}index.html#pricing">See packages <span class="ar"><svg><use href="#i-arrow"/></svg></span></a>
</div></div></section>
{footer(root)}
</div>
{JS}
</body>
</html>"""
    (ROOT / "blog").mkdir(exist_ok=True)
    (ROOT / "blog" / "index.html").write_text(page, encoding="utf-8")


def build_feed(posts):
    items = "".join(
        f"""<item><title>{esc(p['title'])}</title><link>{SITE}/blog/{p['slug']}/</link><guid>{SITE}/blog/{p['slug']}/</guid><pubDate>{dt.datetime.combine(p['date'], dt.time(9)).strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate><description>{esc(p['description'])}</description></item>"""
        for p in posts)
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Shahab blog</title><link>{SITE}/blog/</link><description>Branding, explained. Guides on logos, identity and launch.</description><language>en</language>{items}</channel></rss>
"""
    (ROOT / "blog" / "feed.xml").write_text(xml, encoding="utf-8")


def build_pin_feed(posts):
    """RSS feed for Pinterest auto-publish: two branded pins per article."""
    items = []
    for p in posts:
        for i, (img, title, desc) in enumerate(make_pins(p), 1):
            size = (ROOT / img).stat().st_size
            link = f"{SITE}/blog/{p['slug']}/?utm_source=pinterest&amp;utm_medium=pin&amp;utm_campaign={p['slug']}"
            pub = dt.datetime.combine(p["date"], dt.time(9 + i)).strftime('%a, %d %b %Y %H:%M:%S +0000')
            items.append(f"""<item><title>{esc(title)}</title><link>{link}</link><guid isPermaLink="false">{p['slug']}-pin-{i}</guid><pubDate>{pub}</pubDate><description>{esc(desc)}</description><enclosure url="{SITE}/{img}" length="{size}" type="image/jpeg"/></item>""")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Shahab: branding pins</title><link>{SITE}/blog/</link><description>Branding guides, logo tips and brand identity case studies from Shahab.</description><language>en</language>{''.join(items)}</channel></rss>
"""
    (ROOT / "pins.xml").write_text(xml, encoding="utf-8")


def build_sitemap(posts):
    today = dt.date.today().isoformat()
    urls = [(f"{SITE}/", today, "1.0"), (f"{SITE}/blog/", posts[0]["updated"].isoformat() if posts else today, "0.8")]
    urls += [(f"{SITE}/blog/{p['slug']}/", p["updated"].isoformat(), "0.7") for p in posts]
    body = "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod><priority>{pr}</priority></url>" for u, d, pr in urls)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n', encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


def main():
    css, sprite = site_parts()
    (ROOT / "css").mkdir(exist_ok=True)
    (ROOT / "css" / "main.css").write_text(css.strip() + "\n" + BLOG_CSS, encoding="utf-8")
    posts = load_posts()
    for p in posts:
        build_post(p, posts, sprite)
    build_index(posts, sprite)
    build_feed(posts)
    build_pin_feed(posts)
    build_sitemap(posts)
    print(f"Built {len(posts)} post(s): " + ", ".join(p["slug"] for p in posts))


if __name__ == "__main__":
    main()
