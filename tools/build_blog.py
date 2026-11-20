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
from pages import PAGES_CSS, build_pages
import seo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
SITE = "https://www.abdullahshahab.com"
AUTHOR = "Abdullah Shahab"
PERSON_ID = SITE + "/#shahab"
ORG_ID = SITE + "/#business"
# Every real profile of Abdullah Shahab / Shahab. Add LinkedIn, Behance, Dribbble, Pinterest,
# Clutch etc. here as soon as they exist: they feed the Person + business schema (knowledge panel).
SAME_AS = ["https://www.instagram.com/imabdullahshahab"]
SERVICES = [("Logo design", "/logo-design/"), ("Brand identity design", "/brand-identity-design/"),
            ("Startup branding", "/startup-branding/"), ("Brand guidelines", "/brand-guidelines/"),
            ("Rebranding", "/rebranding/"), ("Packages & pricing", "/pricing/")]
PAGES = []   # (url, html) of every page written, for the sitemap
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
.toc h4,.toc .th{margin:0 0 12px;font:400 11.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3)}
.toc a{display:block;padding:6px 0;font-size:14.5px;color:var(--ink-2);text-decoration:none;line-height:1.35}
.toc a:hover{color:var(--ink)}
.toc .btn{width:100%;margin-top:16px}
.prose{font-size:18.5px;line-height:1.7;color:#24242b;letter-spacing:-.012em;max-width:720px}
.prose{min-width:0}.prose table{display:block;max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
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
.post h2,.post h3{font-size:21px;font-weight:450;letter-spacing:-.03em;line-height:1.25}
.post p{margin:0;color:var(--ink-2);font-size:15px;line-height:1.5}
.post small{font:400 12px var(--mono);color:var(--ink-3)}
.post.lead{grid-column:1/-1;display:grid;grid-template-columns:1.3fr 1fr}
.post.lead .im{aspect-ratio:auto;min-height:340px}
.post.lead .tx{padding:36px;align-content:center}
.post.lead h2,.post.lead h3{font-size:clamp(26px,1.4vw + 16px,36px);letter-spacing:-.04em}
.empty-note{text-align:center;color:var(--ink-3);font:400 13px var(--mono);margin-top:26px}
.author-box{display:flex;gap:18px;align-items:flex-start;padding:24px;border-radius:22px;margin:48px 0 0}
.author-box img{width:64px;height:64px;border-radius:50%;object-fit:cover;flex:none}
.author-box small{font:400 11.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3)}
.author-box b{display:block;font-size:18px;font-weight:500;margin:4px 0 6px}
.author-box b a{text-decoration:none}
.author-box p{margin:0;font-size:15.5px;line-height:1.55;color:var(--ink-2)}
@media(max-width:1000px){.art-wrap{grid-template-columns:1fr}.toc{position:static;order:-1}.posts{grid-template-columns:1fr 1fr}.post.lead{grid-template-columns:1fr}.post.lead .im{min-height:0;aspect-ratio:16/10}}
@media(max-width:640px){.posts{grid-template-columns:1fr}.prose{font-size:17.5px}.cover{aspect-ratio:4/3}.art-cta{padding:28px 22px}}
"""


def nav(root):
    return f"""<div class="notice"><div class="inner"><span class="dot"></span><span>Human-designed branding · first brand board in <b>48 hours</b></span></div></div>
<nav class="nav" id="nav"><div class="inner">
  <a class="logo" href="/" aria-label="Shahab home">SHAHAB<i>.</i></a>
  <div class="links">
    <a href="/#work">Work</a><a href="/#services">Services</a><a href="/pricing/">Pricing</a><a href="/#process">How it works</a><a href="/#reviews">Reviews</a><a href="/blog/">Blog</a><a href="/about/">About</a>
  </div>
  <div class="acts">
    <a class="btn ghost sm" href="{CAL}" target="_blank" rel="noopener">Book a call</a>
    <a class="btn primary sm" href="/pricing/">Start my brand</a>
  </div>
  <button class="burger" id="burger" aria-label="Menu"><svg width="18" height="18" viewBox="0 0 18 18"><path d="M2 5h14M2 9h14M2 13h14" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg></button>
</div></nav>
<div class="mnav" id="mnav">
  <a href="/#work">Work</a><a href="/#services">Services</a><a href="/pricing/">Pricing</a><a href="/#process">How it works</a><a href="/#reviews">Reviews</a><a href="/blog/">Blog</a><a href="/about/">About</a><a href="/#contact">Contact</a>
  <a class="btn primary" href="{CAL}" target="_blank" rel="noopener" style="margin-top:6px">Book a call</a>
</div>"""


def footer(root):
    y = dt.date.today().year
    svc = "".join(f'<a href="{u}">{esc(n)}</a>' for n, u in SERVICES)
    return f"""<footer>
  <div class="inner">
    <div class="fcols">
      <div>
        <a class="logo" href="/" aria-label="Shahab home">SHAHAB<i>.</i></a>
        <p>Human-designed logo and brand identity design by Abdullah Shahab, for founders in the USA, UK and worldwide.</p>
        <div class="soc">
          <a href="https://www.instagram.com/imabdullahshahab" target="_blank" rel="noopener" aria-label="Instagram"><svg><use href="#i-ig"/></svg></a>
          <a href="https://wa.me/923118440498" target="_blank" rel="noopener" aria-label="WhatsApp"><svg><use href="#i-wa"/></svg></a>
          <a href="mailto:imabdullahshahab@gmail.com" aria-label="Email"><svg><use href="#i-mail"/></svg></a>
        </div>
      </div>
      <div class="fcol"><h3>Services</h4>{svc}</div>
      <div class="fcol"><h3>Industries</h3><a href="/branding/beauty-wellness/">Beauty &amp; wellness</a><a href="/branding/food-drink/">Food &amp; drink</a><a href="/branding/tech-fintech/">Tech &amp; fintech</a><a href="/branding/fashion-luxury/">Fashion &amp; luxury</a><a href="/branding/sports/">Sports</a></div>
      <div class="fcol"><h3>Explore</h3><a href="/#work">Featured work</a><a href="/work/voitex/">Case studies</a><a href="/#reviews">Reviews</a><a href="/blog/">Blog</a><a href="/about/">About Abdullah Shahab</a><a href="/#faq">FAQ</a></div>
      <div class="fcol"><h3>Contact</h3><a href="mailto:imabdullahshahab@gmail.com">imabdullahshahab@gmail.com</a><a href="https://wa.me/923118440498" target="_blank" rel="noopener">WhatsApp: +92 311 8440498</a><a href="https://www.instagram.com/imabdullahshahab" target="_blank" rel="noopener">Instagram @imabdullahshahab</a><a href="{CAL}" target="_blank" rel="noopener">Book a call</a></div>
    </div>
    <div class="fbot"><span>© {y} Shahab · Abdullah Shahab. All rights reserved.</span><a href="#top">Designed by a person, not a prompt. ↑</a></div>
  </div>
</footer>"""


JS = """<script>
(function(){var n=document.getElementById('nav');function s(){n.classList.toggle('scrolled',scrollY>10)}addEventListener('scroll',s,{passive:true});s();
var b=document.getElementById('burger'),m=document.getElementById('mnav');b.onclick=function(){m.classList.toggle('open')};
if('IntersectionObserver' in window){var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');o.unobserve(e.target)}})},{threshold:.1});document.querySelectorAll('.rv-up').forEach(function(el){o.observe(el)})}else document.querySelectorAll('.rv-up').forEach(function(el){el.classList.add('in')});})();
</script>"""


def head(root, title, desc, url, image, extra="", og_type=None):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#f7f7f5">
<meta name="p:domain_verify" content="3a7c80742d16baeafd3771a237406652"/>
<meta property="og:type" content="{og_type or ('article' if '/blog/' in url and not url.endswith('/blog/') else 'website')}">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/{image}">
<meta property="og:site_name" content="Shahab">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{SITE}/{image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="Shahab blog" href="{SITE}/blog/feed.xml">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=Geist+Mono:wght@400;500&display=swap" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=Geist+Mono:wght@400;500&display=swap"></noscript>
<link rel="stylesheet" href="/css/main.css">
{extra}
</head>"""


def post_card(p, root, lead=False, tag="h3"):
    return f"""<a class="post{' lead' if lead else ''} rv-up" href="/blog/{p['slug']}/">
  <div class="im"><img src="/{p['cover']}" alt="{esc(p.get('cover_alt',''))}" loading="lazy"></div>
  <div class="tx"><span class="tagc" style="justify-self:start">{esc(p.get('category','Branding'))}</span><{tag}>{esc(p['title'])}</{tag}><p>{esc(p['description'])}</p><small>{p['date'].strftime('%b %-d, %Y')} · {p['read']} min read</small></div>
</a>"""


def write_page(rel, html_text, url, index=True):
    """Run the technical-SEO pass, write the file, and remember it for the sitemap."""
    page_path = "/" + rel.replace("index.html", "") if rel.endswith("index.html") else "/" + rel
    html_text = seo.finalize(html_text, page_path)
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_text, encoding="utf-8")
    if index:
        PAGES.append((url, html_text))


PERSON = {"@type": "Person", "@id": PERSON_ID, "name": AUTHOR, "url": SITE + "/about/"}
PUBLISHER = {"@type": "ProfessionalService", "@id": ORG_ID, "name": "Shahab — Branding & Design", "url": SITE + "/",
             "logo": SITE + "/favicon-512.png"}

POST_SERVICE = {  # which money page each post category supports (topic cluster hub)
    "Pricing": ("/pricing/", "Compare branding packages"),
    "Brand Identity": ("/brand-identity-design/", "Brand identity design"),
    "Branding & IP": ("/logo-design/", "Human-designed logo design"),
    "Industry Guides": ("/brand-identity-design/", "Brand identity design"),
}


def author_box():
    return f"""<div class="author-box card"><img src="/img/shahab-sm.jpg" alt="Abdullah Shahab, brand identity designer" width="64" height="64" loading="lazy">
  <div><small>Written by</small><b><a href="/about/">Abdullah Shahab</a></b><p>Brand identity designer with 7 years of experience and 46+ brand identities for founders in tech, beauty, fashion, sports and food. Every logo designed by hand. <a href="/about/">More about me</a>.</p></div></div>"""


def build_post(p, posts, sprite):
    root = "/"
    url = f"{SITE}/blog/{p['slug']}/"
    title_tag = p.get("seo_title") or (p["title"] + " | Shahab")
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
                "author": {**PERSON, "image": f"{SITE}/img/shahab.jpg", "jobTitle": "Brand Identity Designer", "sameAs": SAME_AS},
                "publisher": PUBLISHER,
                "mainEntityOfPage": url,
                "articleSection": p.get("category", "Branding"),
                "wordCount": len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", p["html"]))),
                "inLanguage": "en",
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
    extra = (f'<meta property="article:published_time" content="{p["date"].isoformat()}">\n'
             f'<meta property="article:modified_time" content="{p["updated"].isoformat()}">\n'
             f'<meta property="article:author" content="{AUTHOR}">\n'
             f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')
    toc = "".join(f'<a href="#{t["id"]}">{esc(html.unescape(t["name"]))}</a>' for t in p["toc"])
    same = [q for q in posts if q["slug"] != p["slug"] and q.get("category") == p.get("category")]
    rest = [q for q in posts if q["slug"] != p["slug"] and q not in same]
    related = (same + rest)[:3]
    rel_html = ""
    if related:
        rel_html = f"""<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Keep reading</h2></div><div class="posts">{''.join(post_card(q, root) for q in related)}</div></div></section>"""
    svc_url, svc_name = POST_SERVICE.get(p.get("category"), ("/brand-identity-design/", "Brand identity design"))
    updated = f' · Updated {p["updated"].strftime("%B %-d, %Y")}' if p["updated"] != p["date"] else ""
    page = f"""{head(root, title_tag, p['description'], url, p['cover'], extra)}
<body>
{sprite}
{nav(root)}
<div class="page" id="top"><div class="rails"></div>
<main>
<section class="hero" style="padding-bottom:0"><div class="aura"><i></i><i></i><i></i><i></i></div>
<div class="inner">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="/blog/">Blog</a><span>/</span><span>{esc(p.get('category','Branding'))}</span></nav>
  <div class="art-head">
    <span class="tagc">{esc(p.get('category','Branding'))}</span>
    <h1 style="margin-top:18px">{esc(p['title'])}</h1>
    <p class="lede" style="margin-top:22px">{esc(p['description'])}</p>
    <div class="meta-row"><img src="/img/shahab-sm.jpg" alt="Abdullah Shahab" width="44" height="44"><span><b><a href="/about/" style="color:inherit;text-decoration:none">Abdullah Shahab</a></b><small>Brand designer · <time datetime="{p['date'].isoformat()}">{p['date'].strftime('%B %-d, %Y')}</time>{updated} · {p['read']} min read</small></span></div>
  </div>
  <div class="cover"><img src="/{p['cover']}" alt="{esc(p.get('cover_alt',''))}" fetchpriority="high"></div>
</div></section>
<section style="position:relative;z-index:1;padding:0 0 96px"><div class="inner">
  <div class="art-wrap">
    <article class="prose">{p['html']}
      {author_box()}
      <div class="art-cta g g-violet">
        <h2>Want a logo you actually own?</h2>
        <p>Human-designed brand identities with full source files and copyright included. First brand board in 48 hours, from $250.</p>
        <div class="row"><a class="btn white" href="{CAL}" target="_blank" rel="noopener">Book a call <span class="ar"><svg><use href="#i-arrow"/></svg></span></a><a class="btn ghostw" href="/pricing/">See packages &amp; pricing</a></div>
      </div>
    </article>
    <aside class="toc card"><p class="th">In this article</p>{toc}<p class="th" style="margin-top:20px">Related service</p><a href="{svc_url}">{esc(svc_name)} →</a><a class="btn primary sm" href="/pricing/">Start my brand</a></aside>
  </div>
</div></section>
{rel_html}
</main>
{footer(root)}
</div>
{JS}
</body>
</html>"""
    write_page(f"blog/{p['slug']}/index.html", page, url)


def build_index(posts, sprite):
    root = "/"
    url = f"{SITE}/blog/"
    desc = "Practical guides on logo design, brand identity, branding costs and launching a brand that looks established, from brand designer Abdullah Shahab."
    cards = "".join(post_card(p, root, lead=(i == 0), tag="h2") for i, p in enumerate(posts))
    note = '<p class="empty-note">New articles every week.</p>'
    ld = {"@context": "https://schema.org", "@type": "Blog", "name": "Shahab blog", "url": url, "description": desc,
          "author": PERSON, "publisher": PUBLISHER,
          "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/blog/{p['slug']}/", "datePublished": p["date"].isoformat()} for p in posts]}
    svc_links = "".join(f'<a href="{u}">{esc(n)}</a>' for n, u in SERVICES)
    page = f"""{head(root, 'Branding & Logo Design Blog: Guides for Founders | Shahab', desc, url, posts[0]['cover'] if posts else 'img/a018.jpg', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>')}
<body>
{sprite}
{nav(root)}
<div class="page" id="top"><div class="rails"></div>
<main>
<section class="hero"><div class="aura"><i></i><i></i><i></i><i></i></div>
<div class="inner">
  <div class="head" style="margin-top:56px">
    <span class="kick" style="margin:0">The Shahab blog</span>
    <h1 style="text-align:center;max-width:14em">Branding &amp; logo design, <span class="grad">explained.</span></h1>
    <p class="lede">Straight answers on logos, brand identity, pricing and launching a brand that looks established. Written by a designer, not a prompt.</p>
  </div>
  <div class="posts" style="padding-bottom:96px">{cards}</div>
  {note}
</div></section>
<section class="band" style="padding:40px 0"><div class="inner"><p class="cta-note" style="text-align:center;margin-bottom:16px">Branding services</p><div class="links-row">{svc_links}</div></div></section>
<section class="band"><div class="inner"><div class="callout g g-orange" style="margin-top:0">
  <div><h2>Ready for a brand you actually own?</h2><p>Human-designed identities, source files and copyright included. First brand board in 48 hours.</p></div>
  <a class="btn white lg" href="/pricing/">See packages <span class="ar"><svg><use href="#i-arrow"/></svg></span></a>
</div></div></section>
</main>
{footer(root)}
</div>
{JS}
</body>
</html>"""
    write_page("blog/index.html", page, url)


def build_feed(posts):
    items = "".join(
        f"""<item><title>{esc(p['title'])}</title><link>{SITE}/blog/{p['slug']}/</link><guid>{SITE}/blog/{p['slug']}/</guid><pubDate>{dt.datetime.combine(p['date'], dt.time(9)).strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate><description>{esc(p['description'])}</description></item>"""
        for p in posts)
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Shahab blog</title><link>{SITE}/blog/</link><description>Branding, explained. Guides on logos, identity and launch.</description><language>en</language>{items}</channel></rss>
"""
    (ROOT / "blog" / "feed.xml").write_text(xml, encoding="utf-8")


def build_pin_feed(posts):
    """Pinterest schedule. Writes pins-data.json; functions/pins.xml.js serves only the pins whose
    date has arrived, so Pinterest picks up a fresh pin every day (portfolio pins + article pins)."""
    from pins import pin_portfolio
    items = []
    for p in posts:
        for i, (img, title, desc) in enumerate(make_pins(p), 1):
            items.append({"id": f"{p['slug']}-pin-{i}", "date": (p["date"] + dt.timedelta(days=i - 1)).isoformat(),
                          "title": title, "description": desc, "image": img,
                          "link": f"{SITE}/blog/{p['slug']}/?utm_source=pinterest&utm_medium=pin&utm_campaign={p['slug']}"})
    port = json.loads((ROOT / "content" / "portfolio.json").read_text(encoding="utf-8"))
    port.sort(key=lambda x: not x.get("featured"))
    start = dt.date(2026, 11, 7)
    out_dir = ROOT / "img" / "pins"
    out_dir.mkdir(parents=True, exist_ok=True)
    day = 0
    for variant in (1, 2):
        for pr in port:
            slug = re.sub(r"[^a-z0-9]+", "-", pr["name"].lower()).strip("-")
            img = out_dir / f"work-{slug}-{variant}.jpg"
            if not img.exists():
                pin_portfolio(ROOT / pr["image"], pr["name"], pr["category"], img, variant)
            cat = pr["category"].split(" · ")
            title = f"{pr['name']} brand identity: {cat[0]} logo & branding" if variant == 1 else f"{pr['name']}: {pr['category']} brand identity"
            desc = pr["alt"].replace(" — ", ": ") + ". Designed by Shahab, human-designed branding with the first brand board in 48 hours."
            items.append({"id": f"work-{slug}-{variant}", "date": (start + dt.timedelta(days=day)).isoformat(),
                          "title": title[:100], "description": desc[:480], "image": f"img/pins/{img.name}",
                          "link": f"{SITE}/?utm_source=pinterest&utm_medium=pin&utm_campaign=work-{slug}#work"})
            day += 1
    tips = json.loads((ROOT / "content" / "tips.json").read_text(encoding="utf-8"))
    groups = {"beauty": ["beauty", "skincare", "cosmetic", "spa", "wellness"], "food": ["food", "café", "cafe", "coffee", "brew", "dessert", "beverage"],
              "tech": ["tech", "fintech", "payments", "ai", "logistics"], "fashion": ["fashion", "luxury", "jewellery", "perfume", "streetwear"],
              "sports": ["sports", "tennis", "padel", "badminton"]}

    def pick_image(tp, n):
        text = (tp["kicker"] + " " + tp["headline"]).lower()
        key = next((g for g in ("beauty", "food", "tech", "fashion", "sports") if any(w in text for w in groups[g][:1] + groups[g][1:] if len(w) > 3 or g == w)), None)
        pool = [x for x in port if key and any(w in x["category"].lower() for w in groups[key])] or [x for x in port if x.get("featured")]
        return pool[n % len(pool)]["image"]
    from pins import pin_tip, pin_tip_text
    # 4 styles per tip, rotated so neighbouring days look different:
    # 1 cream + work photo, 2 work photo background, 3 plain cream text, 4 plain text on a website gradient
    day = 0
    for rnd in range(4):
        for n, tp in enumerate(tips):
            variant = (n + rnd) % 4 + 1
            slug = re.sub(r"[^a-z0-9]+", "-", tp["headline"].lower()).strip("-")[:50]
            img = out_dir / f"tip-{slug}-{variant}.jpg"
            if not img.exists():
                if variant in (1, 2):
                    pin_tip(tp, img, variant, seed=n, image=ROOT / pick_image(tp, n + variant * 7))
                else:
                    pin_tip_text(tp, img, gradient=(variant == 4), seed=n * 3 + rnd)
            link = tp["link"]
            url = f"{SITE}/{link}" if not link.startswith("#") else f"{SITE}/"
            sep = "&" if "?" in url else "?"
            url += f"{sep}utm_source=pinterest&utm_medium=pin&utm_campaign=tip-{slug}" + (link if link.startswith("#") else "")
            desc = tp["headline"] + ": " + "; ".join(tp["points"]) + ". " + tp["cta"] + ", from Shahab, a human brand designer."
            items.append({"id": f"tip-{slug}-{variant}", "date": (start + dt.timedelta(days=day)).isoformat(),
                          "title": tp["headline"][:100], "description": desc[:480], "image": f"img/pins/{img.name}", "link": url})
            day += 1
    items.sort(key=lambda x: (x["date"], x["id"]))
    (ROOT / "pins-data.json").write_text(json.dumps({"site": SITE, "items": items}, ensure_ascii=False), encoding="utf-8")
    old = ROOT / "pins.xml"
    if old.exists():
        old.unlink()
    return items


def build_sitemap():
    pri = lambda u: "1.0" if u == SITE + "/" else "0.9" if u.count("/") == 4 and "/blog/" not in u and "/work/" not in u and "/branding/" not in u else "0.8"
    rows = []
    for u, h in sorted(PAGES, key=lambda x: (x[0] != SITE + "/", x[0])):
        rows.append(f"<url><loc>{u}</loc><lastmod>{seo.lastmod(u, h)}</lastmod><priority>{pri(u)}</priority></url>")
    seo.save_lastmod()
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(rows) + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


def finalize_static():
    """index.html and 404.html are hand-written; give them the same technical pass."""
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    write_page("index.html", home, SITE + "/")
    nf = (ROOT / "404.html").read_text(encoding="utf-8")
    write_page("404.html", nf, SITE + "/404", index=False)


def main():
    n = seo.make_webp()
    css, sprite = site_parts()
    (ROOT / "css").mkdir(exist_ok=True)
    (ROOT / "css" / "main.css").write_text(css.strip() + "\n" + BLOG_CSS + PAGES_CSS, encoding="utf-8")
    posts = load_posts()
    for p in posts:
        build_post(p, posts, sprite)
    build_index(posts, sprite)
    build_pages(ROOT, SITE, CAL, head, nav, footer, sprite, JS, write_page, posts, PERSON, PUBLISHER, SAME_AS, SERVICES)
    finalize_static()
    build_feed(posts)
    build_pin_feed(posts)
    build_sitemap()
    print(f"Built {len(posts)} post(s), {len(PAGES)} indexable pages, {n} new WebP images")


if __name__ == "__main__":
    main()
