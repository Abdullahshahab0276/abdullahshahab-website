"""Case study (/work/<slug>/) and industry (/branding/<slug>/) pages. Called from build_blog.py."""
import json
from pathlib import Path

import yaml

PAGES_CSS = """
/* ---------- case studies + industries ---------- */
.g-grape{background:radial-gradient(55% 60% at 0% 80%,#2e1664,transparent 70%),radial-gradient(45% 45% at 30% 20%,#7846c8,transparent 70%),radial-gradient(40% 35% at 85% 10%,#e68cc8,transparent 70%),radial-gradient(50% 45% at 90% 100%,#a078f0,transparent 70%),#55349a}
.ph{padding:0 0 10px}
.ph h1{font-size:clamp(40px,3.6vw + 14px,72px);max-width:16em;margin-top:18px}
.ph .lede{margin-top:22px;max-width:40em}
.ph .ctas{margin-top:30px}
.facts{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:40px}
.fact{padding:20px 22px;border-radius:20px}
.fact small{display:block;font:400 11.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);margin-bottom:8px}
.fact b{font-weight:500;font-size:17px}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chips span{font-size:13.5px;padding:6px 11px;border-radius:999px;background:var(--fill);color:var(--ink-2)}
.hero-im{margin-top:40px;border-radius:var(--r-xl);overflow:hidden;background:#111}
.hero-im img{width:100%;height:auto}
.story{display:grid;grid-template-columns:300px 1fr;gap:56px;padding:56px 0;border-top:1px solid var(--frame)}
.story h2{font-size:clamp(28px,1.2vw + 18px,38px);letter-spacing:-.04em;position:sticky;top:100px;align-self:start}
.story p{margin:0;font-size:19px;line-height:1.65;color:#2a2a31;max-width:38em}
.gal{columns:2;column-gap:16px;margin-top:20px}
.gal img{width:100%;height:auto;border-radius:22px;margin:0 0 16px;break-inside:avoid;background:#e9e9e4}
.pts{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.pt{padding:26px 22px;border-radius:24px}
.pt .n{font:400 12px var(--mono);color:var(--ink-3)}
.pt h3{font-size:20px;margin:14px 0 8px;font-weight:500}
.pt p{margin:0;color:var(--ink-2);font-size:15.5px;line-height:1.5}
.pgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.pgrid figure{margin:0}
.pgrid img{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:20px;background:#e9e9e4}
.pgrid figcaption{display:flex;gap:10px;padding:12px 2px 0;font-size:15px}
.pgrid figcaption span{color:var(--ink-2)}
.mini-plans{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.mini{padding:26px;border-radius:24px}
.mini .amt{font:400 46px/1 var(--font);letter-spacing:-.05em;margin:14px 0 10px}
.mini p{margin:0 0 6px;color:var(--ink-2);font-size:15px}
.mini.hl{color:#fff}.mini.hl p,.mini.hl h3{color:#fff}
.faq2{max-width:880px;margin:0 auto;display:grid;gap:7px}
.faq2 details{background:#fff;border-radius:16px;box-shadow:0 0 0 1px var(--line)}
.faq2 summary{cursor:pointer;padding:20px;font-size:16.5px;list-style:none;display:flex;justify-content:space-between;gap:16px}
.faq2 summary::-webkit-details-marker{display:none}
.faq2 summary::after{content:"+";font-size:22px;line-height:1;color:var(--ink-2)}
.faq2 details[open] summary::after{content:"−"}
.faq2 p{margin:0;padding:0 20px 20px;color:var(--ink-2);line-height:1.6}
.links-row{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.links-row a{text-decoration:none;padding:10px 16px;border-radius:999px;background:#fff;box-shadow:0 0 0 1px var(--line);font-size:15px}
.links-row a:hover{box-shadow:0 0 0 1px var(--ink)}
.case-mini{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.case-mini a{text-decoration:none}
.case-mini img{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:22px;background:#111}
.case-mini h3{font-size:22px;font-weight:450;margin:14px 0 4px;letter-spacing:-.03em}
.case-mini p{margin:0;color:var(--ink-2);font-size:15px}
@media(max-width:900px){.facts,.pts,.pgrid,.mini-plans,.case-mini{grid-template-columns:1fr 1fr}.story{grid-template-columns:1fr;gap:16px}.story h2{position:static}}
@media(max-width:560px){.facts,.pts,.pgrid,.mini-plans,.case-mini{grid-template-columns:1fr}.gal{columns:1}}
"""


def esc(s):
    import html
    return html.escape(str(s), quote=True)


def build_pages(ROOT, SITE, CAL, head, nav, footer, sprite, JS):
    works = yaml.safe_load((ROOT / "content" / "work.yaml").read_text(encoding="utf-8"))
    inds = yaml.safe_load((ROOT / "content" / "industries.yaml").read_text(encoding="utf-8"))
    port = json.loads((ROOT / "content" / "portfolio.json").read_text(encoding="utf-8"))
    urls = []
    arrow = '<span class="ar"><svg><use href="#i-arrow"/></svg></span>'

    def crumbs(root, *parts):
        out = f'<div class="crumbs"><a href="{root}index.html">Home</a>'
        for label, href in parts:
            out += f'<span>/</span>' + (f'<a href="{href}">{esc(label)}</a>' if href else f'<span>{esc(label)}</span>')
        return out + "</div>"

    def cta_block(root, title, text):
        return f"""<section class="band"><div class="inner"><div class="callout g g-violet" style="margin-top:0">
  <div><h2>{esc(title)}</h2><p>{esc(text)}</p></div>
  <div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn white lg" href="{CAL}" target="_blank" rel="noopener">Book a call {arrow}</a><a class="btn white lg" style="padding-right:28px;background:rgba(255,255,255,.16);color:#fff" href="{root}index.html#pricing">See packages</a></div>
</div></div></section>"""

    def page(root, title, desc, url, image, ld, body):
        extra = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>"
        return f"""{head(root, title, desc, url, image, extra)}
<body>
{sprite}
{nav(root)}
<div class="page" id="top"><div class="rails"></div>
{body}
{footer(root)}
</div>
{JS}
</body>
</html>"""

    def cards(root, items):
        return '<div class="case-mini">' + "".join(
            f'<a class="rv-up" href="{root}work/{w["slug"]}/index.html"><img src="{root}{w["cover"]}" alt="{esc(w["name"])} brand identity" loading="lazy"><h3>{esc(w["name"])}</h3><p>{esc(w["industry"])} · {esc(w["tagline"])}</p></a>'
            for w in items) + "</div>"

    ind_by = {i["slug"]: i for i in inds}

    # ---------- case studies ----------
    for w in works:
        root = "../../"
        url = f"{SITE}/work/{w['slug']}/"
        ind = ind_by.get(w.get("industry_page"))
        sections = ""
        gal = w["gallery"]
        per = max(1, len(gal) // (len(w["sections"]) + 1))
        gi = 1
        for s in w["sections"]:
            imgs = gal[gi:gi + per]
            gi += per
            g = '<div class="gal">' + "".join(f'<img src="{root}{x}" alt="{esc(w["name"])}: {esc(s["heading"].lower())}" loading="lazy">' for x in imgs) + "</div>" if imgs else ""
            sections += f'<div class="story rv-up"><h2>{esc(s["heading"])}</h2><div><p>{esc(s["body"])}</p>{g}</div></div>'
        rest = gal[gi:]
        if rest:
            sections += '<div class="story rv-up"><h2>More from the identity</h2><div><div class="gal">' + "".join(f'<img src="{root}{x}" alt="{esc(w["name"])} brand identity mockup" loading="lazy">' for x in rest) + "</div></div></div>"
        others = [o for o in works if o["slug"] != w["slug"]]
        body = f"""<section class="hero ph"><div class="aura"><i></i><i></i><i></i><i></i></div><div class="inner">
  {crumbs(root, ("Work", root + "index.html#work"), (w["name"], None))}
  <span class="tagc">Case study · {esc(w["industry"])}</span>
  <h1>{esc(w["title"])}</h1>
  <p class="lede">{esc(w["intro"])}</p>
  <div class="ctas"><a class="btn primary lg" href="{CAL}" target="_blank" rel="noopener">Start a project like this {arrow}</a><a class="btn ghost lg" style="padding-right:28px" href="{root}{w["pdf"]}" target="_blank" rel="noopener">View the full PDF</a></div>
  <div class="facts">
    <div class="fact card"><small>Brand</small><b>{esc(w["name"])}</b></div>
    <div class="fact card"><small>Industry</small><b>{esc(w["industry"])}</b></div>
    <div class="fact card"><small>Brand line</small><b>“{esc(w["tagline"])}”</b></div>
  </div>
  <div class="fact card" style="margin-top:12px"><small>What was delivered</small><div class="chips">{"".join(f"<span>{esc(d)}</span>" for d in w["deliverables"])}</div></div>
  <div class="hero-im"><img src="{root}{gal[0]}" alt="{esc(w["name"])} brand identity"></div>
</div></section>
<section style="position:relative;z-index:1;padding:20px 0 40px"><div class="inner">{sections}</div></section>
{cta_block(root, "Want a brand like " + w["name"] + "?", "Human-designed identities with source files and copyright included. First brand board in 48 hours, from $250.")}
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">More case studies</h2></div>{cards(root, others)}
{f'<p class="small-note" style="margin-top:30px"><a href="{root}branding/{ind["slug"]}/index.html">See more {esc(ind["name"].lower())} branding →</a></p>' if ind else ""}</div></section>"""
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "CreativeWork", "name": w["title"], "description": w["description"], "url": url, "image": f"{SITE}/{gal[0]}",
             "creator": {"@type": "Person", "name": "Shahab", "url": SITE + "/"}, "about": w["industry"], "keywords": ", ".join(w["deliverables"])},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Work", "item": SITE + "/#work"},
                {"@type": "ListItem", "position": 3, "name": w["name"], "item": url}]}]}
        out = ROOT / "work" / w["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(root, w["title"] + " | Shahab", w["description"], url, gal[0], ld, body), encoding="utf-8")
        urls.append(url)

    # ---------- industries ----------
    for ind in inds:
        root = "../../"
        url = f"{SITE}/branding/{ind['slug']}/"
        kws = [k.lower() for k in ind["keywords"]]
        items = [p for p in port if any(k in p["category"].lower() for k in kws)]
        rel_works = [w for w in works if w.get("industry_page") == ind["slug"]]
        pts = "".join(f'<div class="pt card rv-up"><span class="n">0{i}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for i, (t, d) in enumerate(ind["points"], 1))
        grid = "".join(f'<figure class="rv-up"><img src="{root}{p["image"]}" alt="{esc(p["alt"])}" loading="lazy"><figcaption><b style="font-weight:500">{esc(p["name"])}</b><span>{esc(p["category"])}</span></figcaption></figure>' for p in items[:9])
        faqs = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in ind["faqs"])
        others = "".join(f'<a href="{root}branding/{o["slug"]}/index.html">{esc(o["name"])}</a>' for o in inds if o["slug"] != ind["slug"])
        body = f"""<section class="hero ph"><div class="aura"><i></i><i></i><i></i><i></i></div><div class="inner">
  {crumbs(root, ("Branding", None), (ind["name"], None))}
  <span class="tagc">{esc(ind["name"])} branding</span>
  <h1>{esc(ind["h1"])}</h1>
  <p class="lede">{esc(ind["intro"])}</p>
  <div class="ctas"><a class="btn primary lg" href="{CAL}" target="_blank" rel="noopener">Book a free brief call {arrow}</a><a class="btn ghost lg" style="padding-right:28px" href="{root}index.html#pricing">See packages</a></div>
  <div class="trust" style="margin:26px 0 70px"><span><svg><use href="#i-check"/></svg>First brand board in 48 hours</span><span><svg><use href="#i-check"/></svg>Source files &amp; copyright included</span><span><svg><use href="#i-check"/></svg>Human-designed, never a prompt</span></div>
</div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">What great {esc(ind["name"].lower())} branding gets right</h2></div><div class="pts">{pts}</div></div></section>
{f'<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">{esc(ind["name"])} brands I have designed</h2><p class="lede">Complete brand boards: logo, colour, typography, packaging and real-world mockups.</p></div><div class="pgrid">{grid}</div></div></section>' if items else ""}
{f'<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Case study</h2></div>{cards(root, rel_works)}</div></section>' if rel_works else ""}
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Packages</h2><p class="lede">Fixed, one-time pricing. Pick the package that fits your stage, or ask for a custom quote.</p></div>
<div class="mini-plans">
  <div class="mini card"><h3>Basic plan</h3><div class="amt">$250</div><p>1 logo concept, colour palette, typography, 3D mockup, stationery and guidelines.</p><p>2-day delivery · 2 revisions</p></div>
  <div class="mini hl g g-violet"><h3>Premium Branding</h3><div class="amt">$450</div><p>3 logo concepts, complete brand guidelines, competitive analysis and social media kit.</p><p>2-day delivery · 3 revisions</p></div>
  <div class="mini card"><h3>The Brand Ecosystem</h3><div class="amt">$1,050</div><p>Everything in Premium plus strategy, ad creatives, packaging and merchandise.</p><p>5 business days · unlimited revisions</p></div>
</div>
<div class="cta-wrap"><a class="btn primary cta" href="{root}index.html#pricing">Compare all packages {arrow}</a></div></div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Questions about {esc(ind["name"].lower())} branding</h2></div><div class="faq2">{faqs}</div></div></section>
{cta_block(root, "Ready to brand your " + ind["name"].lower().replace(" & ", " or ") + " business?", "Book a short call and tell me about your business. Your first full brand board arrives within 48 hours.")}
<section class="band" style="padding:56px 0"><div class="inner"><p class="cta-note" style="text-align:center;margin-bottom:16px">Branding for other industries</p><div class="links-row">{others}</div></div></section>"""
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "Service", "name": ind["h1"], "serviceType": "Brand identity design", "description": ind["description"], "url": url,
             "provider": {"@type": "ProfessionalService", "name": "Shahab — Branding & Design", "url": SITE + "/"},
             "areaServed": ["United States", "United Kingdom", "Canada", "Australia"],
             "offers": [{"@type": "Offer", "name": n, "price": p, "priceCurrency": "USD"} for n, p in (("Basic plan", "250"), ("Premium Branding", "450"), ("The Brand Ecosystem", "1050"))]},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in ind["faqs"]]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": ind["name"] + " branding", "item": url}]}]}
        img = items[0]["image"] if items else "img/a018.jpg"
        out = ROOT / "branding" / ind["slug"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(root, ind["title"], ind["description"], url, img, ld, body), encoding="utf-8")
        urls.append(url)
    return urls, works, inds
