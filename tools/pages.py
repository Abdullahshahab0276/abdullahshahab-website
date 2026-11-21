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
.svc-im img{aspect-ratio:16/7;object-fit:cover}
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
.pgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.pgrid figure{margin:0}.pgrid img{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:22px;background:#e9e9e4}.pgrid figcaption{font-size:14px;color:var(--ink-3);margin-top:8px}@media(max-width:760px){.pgrid{grid-template-columns:1fr 1fr}}.ziplist{columns:6;column-gap:18px;font-size:15px;line-height:1.9}@media(max-width:760px){.ziplist{columns:3}}.case-mini{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.case-mini a{text-decoration:none}
.case-mini img{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:22px;background:#111}
.case-mini h3{font-size:22px;font-weight:450;margin:14px 0 4px;letter-spacing:-.03em}
.case-mini p{margin:0;color:var(--ink-2);font-size:15px}
.svc{max-width:860px;margin:0 auto}
.svc h2{font-size:clamp(28px,1.2vw + 18px,38px);letter-spacing:-.04em;line-height:1.15;margin:56px 0 16px;font-weight:450}
.svc p{font-size:18px;line-height:1.7;color:#2a2a31;margin:0 0 14px}
.svc ul{margin:0 0 16px;padding-left:1.2em;font-size:17.5px;line-height:1.65;color:#2a2a31}
.svc li{margin:.4em 0}
.svc a{color:var(--ink);text-decoration-color:rgba(75,63,227,.45);text-underline-offset:3px}
.ptable{width:100%;border-collapse:separate;border-spacing:0;background:#fff;border-radius:22px;box-shadow:0 0 0 1px var(--line);overflow:hidden;font-size:15.5px}
.ptable th,.ptable td{padding:14px 16px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
.ptable thead th{background:var(--fill);font-weight:500}
.ptable tr:last-child td{border-bottom:0}
.twrap{overflow-x:auto;-webkit-overflow-scrolling:touch;margin-top:10px}
.who{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:8px}
.who span{padding:10px 16px;border-radius:999px;background:#fff;box-shadow:0 0 0 1px var(--line);font-size:15px}
.about-grid{display:grid;grid-template-columns:360px 1fr;gap:56px;align-items:start}
.about-grid img{width:100%;height:auto;border-radius:var(--r-xl)}
.factlist{display:grid;gap:8px;margin-top:20px}
.factlist div{display:flex;justify-content:space-between;gap:16px;padding:12px 16px;border-radius:14px;background:#fff;box-shadow:0 0 0 1px var(--line);font-size:15px}
.factlist span{color:var(--ink-3)}
@media(max-width:900px){.about-grid{grid-template-columns:1fr}}
@media(max-width:900px){.facts,.pts,.pgrid,.mini-plans,.case-mini{grid-template-columns:1fr 1fr}.story{grid-template-columns:1fr;gap:16px}.story h2{position:static}}
@media(max-width:560px){.facts,.pts,.pgrid,.mini-plans,.case-mini{grid-template-columns:1fr}.gal{columns:1}}
"""


def esc(s):
    import html
    return html.escape(str(s), quote=True)


PLANS = [  # single source for package facts used on generated pages
    ("Basic plan", "250", "1 logo concept, colour palette, typography, 3D mockup, stationery and brand guidelines.", "2-day delivery · 2 revisions"),
    ("Premium Branding", "450", "3 logo concepts, complete brand guidelines, competitive analysis and social media kit.", "2-day delivery · 3 revisions"),
    ("The Brand Ecosystem", "1050", "Everything in Premium plus strategy, brand voice, ad creatives, packaging and UI assets.", "5 business days · unlimited revisions on the chosen concept"),
]
COMPARE = [  # rows of the pricing comparison table
    ("Price (one-time)", "$250", "$450", "$1,050"),
    ("Logo concepts", "1", "3", "3"),
    ("Revisions", "2", "3", "Unlimited on the chosen concept"),
    ("Delivery", "2 days", "2 days", "5 business days"),
    ("First brand board", "48 hours", "48 hours", "48 hours"),
    ("Vector source files + copyright", "Yes", "Yes", "Yes"),
    ("Colour palette + typography", "Yes", "Yes", "Yes"),
    ("3D mockups + stationery", "Yes", "Yes (incl. business card)", "Yes"),
    ("Brand guidelines", "Yes", "Complete", "Complete"),
    ("Competitive analysis", "—", "Yes", "Yes"),
    ("Imagery + graphic styles", "—", "Yes", "Yes"),
    ("Social media kit", "—", "Yes", "Yes"),
    ("Brand voice + marketing angles", "—", "—", "Yes"),
    ("10 social creatives, 5 Google ad banners, 5 static ads", "—", "—", "Yes"),
    ("LinkedIn profile + email marketing design", "—", "—", "Yes"),
    ("Packaging, merchandise, pattern, icons + UI assets", "—", "—", "Yes"),
]


def build_pages(ROOT, SITE, CAL, head, nav, footer, sprite, JS, write_page, posts, PERSON, PUBLISHER, SAME_AS, SERVICES):
    works = yaml.safe_load((ROOT / "content" / "work.yaml").read_text(encoding="utf-8"))
    inds = yaml.safe_load((ROOT / "content" / "industries.yaml").read_text(encoding="utf-8"))
    extra = yaml.safe_load((ROOT / "content" / "industries_extra.yaml").read_text(encoding="utf-8"))
    svcs = yaml.safe_load((ROOT / "content" / "services.yaml").read_text(encoding="utf-8"))
    about = yaml.safe_load((ROOT / "content" / "about.yaml").read_text(encoding="utf-8"))
    port = json.loads((ROOT / "content" / "portfolio.json").read_text(encoding="utf-8"))
    post_by = {p["slug"]: p for p in posts}
    work_by = {w["slug"]: w for w in works}
    svc_by = {x["slug"]: x for x in svcs}
    arrow = '<span class="ar"><svg><use href="#i-arrow"/></svg></span>'
    offers = [{"@type": "Offer", "name": n, "price": pr, "priceCurrency": "USD", "description": d, "url": SITE + "/pricing/"} for n, pr, d, _ in PLANS]
    provider = {"@type": "ProfessionalService", "@id": PUBLISHER["@id"], "name": PUBLISHER["name"], "url": SITE + "/"}

    def crumbs(*parts):
        out = '<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a>'
        for label, href in parts:
            out += '<span>/</span>' + (f'<a href="{href}">{esc(label)}</a>' if href else f'<span>{esc(label)}</span>')
        return out + "</nav>"

    def bc_ld(*parts):
        items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}]
        for i, (n, u) in enumerate(parts, 2):
            items.append({"@type": "ListItem", "position": i, "name": n, "item": u})
        return {"@type": "BreadcrumbList", "itemListElement": items}

    def faq_ld(faqs):
        return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

    def cta_block(title, text):
        return f"""<section class="band"><div class="inner"><div class="callout g g-violet" style="margin-top:0">
  <div><h2>{esc(title)}</h2><p>{esc(text)}</p></div>
  <div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn white lg" href="{CAL}" target="_blank" rel="noopener">Book a call {arrow}</a><a class="btn white lg" style="padding-right:28px;background:rgba(255,255,255,.16);color:#fff" href="/pricing/">See packages</a></div>
</div></div></section>"""

    def page(title, desc, url, image, ld, body):
        x = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>"
        return f"""{head("/", title, desc, url, image, x)}
<body>
{sprite}
{nav("/")}
<div class="page" id="top"><div class="rails"></div>
<main>
{body}
</main>
{footer("/")}
</div>
{JS}
</body>
</html>"""

    def cards(items):
        return '<div class="case-mini">' + "".join(
            f'<a class="rv-up" href="/work/{w["slug"]}/"><img src="/{w["cover"]}" alt="{esc(w["name"])} brand identity case study" loading="lazy"><h3>{esc(w["name"])}</h3><p>{esc(w["industry"])} · {esc(w["tagline"])}</p></a>'
            for w in items) + "</div>"

    def post_links(slugs):
        ps = [post_by[x] for x in slugs if x in post_by]
        if not ps:
            return ""
        return '<section class="band" style="padding:48px 0"><div class="inner"><div class="head rv-up"><h2 class="md">Guides from the blog</h2></div><div class="links-row">' + "".join(
            f'<a href="/blog/{q["slug"]}/">{esc(q["title"])}</a>' for q in ps) + "</div></div></section>"

    def plans_html():
        out = '<div class="mini-plans">'
        for i, (n, pr, d, t) in enumerate(PLANS):
            cls = "mini hl g g-violet" if i == 1 else "mini card"
            out += f'<div class="{cls}"><h3>{n}</h3><div class="amt">${int(pr):,}</div><p>{d}</p><p>{t}</p></div>'
        return out + '</div><div class="cta-wrap"><a class="btn primary cta" href="/pricing/">Compare all packages ' + arrow + "</a></div>"

    def faq_html(faqs):
        return '<div class="faq2">' + "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faqs) + "</div>"

    def svc_links_row(exclude=None):
        return "".join(f'<a href="{u}">{esc(n)}</a>' for n, u in SERVICES if u != exclude)

    # ---------- case studies ----------
    for w in works:
        url = f"{SITE}/work/{w['slug']}/"
        ind = next((i for i in inds if i["slug"] == w.get("industry_page")), None)
        sections = ""
        gal = w["gallery"]
        per = max(1, len(gal) // (len(w["sections"]) + 1))
        gi = 1
        for s_ in w["sections"]:
            imgs = gal[gi:gi + per]
            gi += per
            g = '<div class="gal">' + "".join(f'<img src="/{x}" alt="{esc(w["name"])}: {esc(s_["heading"].lower())}" loading="lazy">' for x in imgs) + "</div>" if imgs else ""
            sections += f'<div class="story rv-up"><h2>{esc(s_["heading"])}</h2><div><p>{esc(s_["body"])}</p>{g}</div></div>'
        rest = gal[gi:]
        if rest:
            sections += '<div class="story rv-up"><h2>More from the identity</h2><div><div class="gal">' + "".join(f'<img src="/{x}" alt="{esc(w["name"])} brand identity mockup" loading="lazy">' for x in rest) + "</div></div></div>"
        others = [o for o in works if o["slug"] != w["slug"]]
        body = f"""<section class="hero ph"><div class="aura"><i></i><i></i><i></i><i></i></div><div class="inner">
  {crumbs(("Work", "/#work"), (w["name"], None))}
  <span class="tagc">Case study · {esc(w["industry"])}</span>
  <h1>{esc(w["title"])}</h1>
  <p class="lede">{esc(w["intro"])}</p>
  <div class="ctas"><a class="btn primary lg" href="{CAL}" target="_blank" rel="noopener">Start a project like this {arrow}</a><a class="btn ghost lg" style="padding-right:28px" href="/{w["pdf"]}" target="_blank" rel="noopener">View the full PDF</a></div>
  <div class="facts">
    <div class="fact card"><small>Brand</small><b>{esc(w["name"])}</b></div>
    <div class="fact card"><small>Industry</small><b>{esc(w["industry"])}</b></div>
    <div class="fact card"><small>Brand line</small><b>“{esc(w["tagline"])}”</b></div>
  </div>
  <div class="fact card" style="margin-top:12px"><small>What was delivered</small><div class="chips">{"".join(f"<span>{esc(d)}</span>" for d in w["deliverables"])}</div></div>
  <div class="hero-im"><img src="/{gal[0]}" alt="{esc(w["name"])} brand identity" fetchpriority="high"></div>
</div></section>
<section style="position:relative;z-index:1;padding:20px 0 40px"><div class="inner">{sections}</div></section>
{cta_block("Want a brand like " + w["name"] + "?", "Human-designed identities with source files and copyright included. First brand board in 48 hours, from $250.")}
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">More brand identity case studies</h2></div>{cards(others)}
<p class="small-note" style="margin-top:30px">{f'<a href="/branding/{ind["slug"]}/">More {esc(ind["name"].lower())} branding</a> · ' if ind else ""}<a href="/brand-identity-design/">Brand identity design services</a> · <a href="/pricing/">Packages &amp; pricing</a></p></div></section>"""
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "CreativeWork", "name": w["title"], "description": w["description"], "url": url, "image": f"{SITE}/{gal[0]}",
             "creator": PERSON, "publisher": provider, "about": w["industry"], "keywords": ", ".join(w["deliverables"]), "inLanguage": "en"},
            bc_ld(("Work", SITE + "/#work"), (w["name"], url))]}
        title = w["title"] if len(w["title"]) <= 52 else w["name"] + " Brand Identity Case Study"
        write_page(f"work/{w['slug']}/index.html", page(title + " | Shahab", w["description"], url, gal[0], ld, body), url)

    # ---------- industries ----------
    for ind in inds:
        url = f"{SITE}/branding/{ind['slug']}/"
        ex = extra.get(ind["slug"], {})
        kws = [k.lower() for k in ind["keywords"]]
        items = [p for p in port if any(k in p["category"].lower() for k in kws)]
        rel_works = [w for w in works if w.get("industry_page") == ind["slug"]]
        pts = "".join(f'<div class="pt card rv-up"><span class="n">0{i}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for i, (t, d) in enumerate(ind["points"], 1))
        grid = "".join(f'<figure class="rv-up"><img src="/{p["image"]}" alt="{esc(p["alt"])}" loading="lazy"><figcaption><b style="font-weight:500">{esc(p["name"])}</b><span>{esc(p["category"])}</span></figcaption></figure>' for p in items[:9])
        faqs = ind["faqs"] + ex.get("faqs", [])
        others = "".join(f'<a href="/branding/{o["slug"]}/">{esc(o["name"])}</a>' for o in inds if o["slug"] != ind["slug"])
        low = ind["name"].lower()
        who = "".join(f"<span>{esc(x)}</span>" for x in ex.get("who", []))
        svc_l = "".join(f'<a href="/{x}/">{esc(svc_by[x]["name"])}</a>' for x in ex.get("services", []) if x in svc_by)
        body = f"""<section class="hero ph"><div class="aura"><i></i><i></i><i></i><i></i></div><div class="inner">
  {crumbs(("Branding", "/brand-identity-design/"), (ind["name"], None))}
  <span class="tagc">{esc(ind["name"])} branding</span>
  <h1>{esc(ind["h1"])}</h1>
  <p class="lede">{esc(ind["intro"])}</p>
  <div class="ctas"><a class="btn primary lg" href="{CAL}" target="_blank" rel="noopener">Book a free brief call {arrow}</a><a class="btn ghost lg" style="padding-right:28px" href="/pricing/">See packages</a></div>
  <div class="trust" style="margin:26px 0 70px"><span><svg><use href="#i-check"/></svg>First brand board in 48 hours</span><span><svg><use href="#i-check"/></svg>Source files &amp; copyright included</span><span><svg><use href="#i-check"/></svg>Human-designed, never a prompt</span></div>
</div></section>
{f'<section class="band" style="padding-top:0"><div class="inner"><div class="head rv-up"><h2 class="md">Who this {esc(low)} branding is for</h2></div><div class="who">{who}</div></div></section>' if who else ""}
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">What great {esc(low)} branding gets right</h2></div><div class="pts">{pts}</div></div></section>
{f'<section class="band"><div class="inner"><div class="svc"><h2>What your {esc(low)} brand identity includes</h2><p>{esc(ex["deliver"])}</p><p>Every package includes vector source files and the copyright, because every concept is designed by me rather than generated by AI. Your first full brand board arrives within 48 hours of the brief; Basic and Premium are completed in 2 days, The Brand Ecosystem in 5 business days.</p><h2>How the process works</h2><ul><li><b>Brief:</b> a short call about your business, customers and the look you want.</li><li><b>Research and concepts:</b> I study your market and competitors, then design logo concepts, colours, type and mockups.</li><li><b>Refine and launch:</b> we revise until it feels right, then you receive every file and the guidelines.</li></ul></div></div></section>' if ex.get("deliver") else ""}
{f'<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">{esc(ind["name"])} brands I have designed</h2><p class="lede">Complete brand boards: logo, colour, typography, packaging and real-world mockups.</p></div><div class="pgrid">{grid}</div></div></section>' if items else ""}
{f'<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">{esc(ind["name"])} branding case study</h2></div>{cards(rel_works)}</div></section>' if rel_works else ""}
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">{esc(ind["name"])} branding packages and prices</h2><p class="lede">Fixed, one-time pricing. Pick the package that fits your stage, or ask for a custom quote.</p></div>
{plans_html()}</div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Questions about {esc(low)} branding</h2></div>{faq_html(faqs)}</div></section>
{post_links(ex.get("posts", []))}
{cta_block("Ready to brand your " + low.replace(" & ", " or ") + " business?", "Book a short call and tell me about your business. Your first full brand board arrives within 48 hours.")}
<section class="band" style="padding:56px 0"><div class="inner"><p class="cta-note" style="text-align:center;margin-bottom:16px">Related services</p><div class="links-row">{svc_l}</div><p class="cta-note" style="text-align:center;margin:28px 0 16px">Branding for other industries</p><div class="links-row">{others}</div></div></section>"""
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "Service", "name": ind["h1"], "serviceType": "Brand identity design", "description": ex.get("meta", ind["description"]), "url": url,
             "provider": provider, "areaServed": ["United States", "United Kingdom", "Canada", "Australia", "United Arab Emirates"],
             "audience": {"@type": "BusinessAudience", "name": ", ".join(ex.get("who", [])) or ind["name"]},
             "offers": offers},
            faq_ld(faqs),
            bc_ld((ind["name"] + " branding", url))]}
        img = items[0]["image"] if items else "img/a018.jpg"
        write_page(f"branding/{ind['slug']}/index.html", page(ind["title"], ex.get("meta", ind["description"]), url, img, ld, body), url)

    # ---------- service (commercial) pages ----------
    for sv in svcs:
        url = f"{SITE}/{sv['slug']}/"
        secs = ""
        for sec in sv["sections"]:
            secs += f'<h2>{esc(sec["h2"])}</h2>'
            for para in sec.get("p", [])[:1] if sec.get("ul") else sec.get("p", []):
                secs += f"<p>{para}</p>"
            if sec.get("ul"):
                secs += "<ul>" + "".join(f"<li>{li}</li>" for li in sec["ul"]) + "</ul>"
                for para in sec.get("p", [])[1:]:
                    secs += f"<p>{para}</p>"
            if sec.get("p2"):
                secs += f'<p>{sec["p2"]}</p>'
        table = ""
        if sv.get("table"):
            head_row = "<tr><th>Included</th>" + "".join(f"<th>{n}</th>" for n, *_ in PLANS) + "</tr>"
            rows = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in COMPARE)
            table = f'<section class="band" style="padding-top:0"><div class="inner"><div class="svc" style="max-width:1100px"><h2>Branding packages compared</h2><div class="twrap"><table class="ptable"><thead>{head_row}</thead><tbody>{rows}</tbody></table></div><p class="small-note" style="margin-top:14px">Prices in US dollars, paid once. No subscription. <a href="{CAL}" target="_blank" rel="noopener">Book a call</a> or <a href="/#contact">ask for a custom quote</a>.</p></div></div></section>'
        rel_cases = [work_by[x] for x in sv.get("related_cases", []) if x in work_by]
        body = f"""<section class="hero ph"><div class="aura"><i></i><i></i><i></i><i></i></div><div class="inner">
  {crumbs((sv["name"], None))}
  <span class="tagc">{esc(sv["kicker"])}</span>
  <h1>{esc(sv["h1"])}</h1>
  <p class="lede">{esc(sv["intro"])}</p>
  <div class="ctas"><a class="btn primary lg" href="{CAL}" target="_blank" rel="noopener">Book a free brief call {arrow}</a><a class="btn ghost lg" style="padding-right:28px" href="{'/#contact' if sv['slug'] == 'pricing' else '/pricing/'}">{'Get a custom quote' if sv['slug'] == 'pricing' else 'See packages &amp; pricing'}</a></div>
  <div class="trust" style="margin:26px 0 40px"><span><svg><use href="#i-check"/></svg>First brand board in 48 hours</span><span><svg><use href="#i-check"/></svg>Source files &amp; copyright included</span><span><svg><use href="#i-check"/></svg>From $250, paid once</span></div>
  <div class="hero-im svc-im"><img src="/{sv["image"]}" alt="{esc(sv["image_alt"])}" fetchpriority="high"></div>
</div></section>
{table}
<section class="band"><div class="inner"><div class="svc">{secs}</div></div></section>
{"" if sv.get("table") else '<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">' + esc(sv["name"]) + ' packages and prices</h2><p class="lede">Fixed, one-time pricing designed by one designer, start to finish.</p></div>' + plans_html() + '</div></section>'}
{f'<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Case studies</h2></div>{cards(rel_cases)}</div></section>' if rel_cases else ""}
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">{esc(sv["name"])} FAQs</h2></div>{faq_html(sv["faqs"])}</div></section>
{post_links(sv.get("related_posts", []))}
{cta_block("Ready to start your " + sv["name"].lower().replace("packages & pricing", "brand") + "?", "Book a short call and tell me about your business. Your first full brand board arrives within 48 hours.")}
<section class="band" style="padding:56px 0"><div class="inner"><p class="cta-note" style="text-align:center;margin-bottom:16px">More services</p><div class="links-row">{svc_links_row("/" + sv["slug"] + "/")}</div><p class="cta-note" style="text-align:center;margin:28px 0 16px">Branding by industry</p><div class="links-row">{"".join(f'<a href="/branding/{o["slug"]}/">{esc(o["name"])}</a>' for o in inds)}</div></div></section>"""
        graph = [faq_ld(sv["faqs"]), bc_ld((sv["name"], url))]
        if sv["slug"] == "pricing":
            graph.insert(0, {"@type": "OfferCatalog", "name": "Shahab branding packages", "url": url, "itemListElement": [{**o, "seller": provider} for o in offers]})
        else:
            graph.insert(0, {"@type": "Service", "name": sv["h1"], "serviceType": sv["keyword"].title(), "description": sv["description"], "url": url,
                             "provider": provider, "areaServed": ["United States", "United Kingdom", "Canada", "Australia", "United Arab Emirates"],
                             "offers": offers})
        ld = {"@context": "https://schema.org", "@graph": graph}
        write_page(f"{sv['slug']}/index.html", page(sv["title"], sv["description"], url, sv["image"], ld, body), url)

    # ---------- service areas (/usa/, /usa/<city>/, /uk/, /uk/<city>/) ----------
    locs = yaml.safe_load((ROOT / "content" / "locations.yaml").read_text(encoding="utf-8"))
    ind_by = {i["slug"]: i for i in inds}
    hubs = {l["slug"]: l for l in locs if l.get("hub")}
    us_custom = {l["name"]: l for l in locs if l.get("parent") == "usa"}
    us_cities = json.loads((ROOT / "content" / "us_cities.json").read_text(encoding="utf-8"))
    us_states = {}
    for c in us_cities:
        us_states.setdefault(c["state_slug"], {"name": c["state_name"], "code": c["state"], "cities": []})["cities"].append(c)
    for loc in locs:
        if loc.get("parent") == "usa":
            continue
        hub = loc if loc.get("hub") else hubs[loc["parent"]]
        path = f"{loc['slug']}/" if loc.get("hub") else f"{hub['slug']}/{loc['slug']}/"
        url = f"{SITE}/{path}"
        children = [c for c in locs if c.get("parent") == hub["slug"] and hub["slug"] != "usa"]
        secs = ""
        for sec in loc.get("sections", []):
            secs += f'<h2>{esc(sec["h2"])}</h2>' + "".join(f"<p>{x}</p>" for x in sec.get("p", []))
            if sec.get("table"):
                hr, *rows = sec["table"]
                secs += '<div class="twrap"><table class="ptable"><thead><tr>' + "".join(f"<th>{esc(h)}</th>" for h in hr) + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>"
            if sec.get("ul"):
                secs += "<ul>" + "".join(f"<li>{li}</li>" for li in sec["ul"]) + "</ul>"
        if not loc.get("hub"):
            secs += f'<h2>What {esc(loc["name"])} businesses ask me for</h2><ul>' + "".join(f"<li>{esc(n)}</li>" for n in loc["needs"]) + "</ul>"
            secs += f'<h2>Working with a remote designer from {esc(loc["name"])}</h2><p>{esc(loc["timezone"])} Calls are booked on Calendly in your own time zone, and everything else happens by email, WhatsApp and shared files. Your first full brand board arrives within 48 hours of the brief.</p>'
            secs += "<h2>Industries I design for in " + esc(loc["name"]) + "</h2><p>" + ", ".join(f'<a href="/branding/{x}/">{esc(ind_by[x]["name"].lower())} branding</a>' for x in loc["industries"] if x in ind_by) + ". Every identity is designed by me, with source files and copyright included.</p>"
        sib = "".join(f'<a href="/{hub["slug"]}/{c["slug"]}/">{esc(c["name"])}</a>' for c in children if c["slug"] != loc["slug"])
        if hub["slug"] == "usa":
            sib = "".join(f'<a href="/{k}/">{esc(v["name"])}</a>' for k, v in sorted(us_states.items(), key=lambda kv: kv[1]["name"]))
        area_links = (f'<a href="/{hub["slug"]}/">All of the {esc(hub["name"])}</a>' if not loc.get("hub") else "") + sib
        other_hub = "".join(f'<a href="/{h}/">Branding in the {esc(hubs[h]["name"])}</a>' for h in hubs if h != hub["slug"])
        crumb_parts = [(hub["name"], None)] if loc.get("hub") else [(hub["name"], f"/{hub['slug']}/"), (loc["name"], None)]
        body = f"""<section class="hero ph"><div class="aura"><i></i><i></i><i></i><i></i></div><div class="inner">
  {crumbs(*crumb_parts)}
  <span class="tagc">{esc(loc["name"])} · remote brand designer</span>
  <h1>{esc(loc["h1"])}</h1>
  <p class="lede">{esc(loc["intro"])}</p>
  <div class="ctas"><a class="btn primary lg" href="{CAL}" target="_blank" rel="noopener">Book a call in your time zone {arrow}</a><a class="btn ghost lg" style="padding-right:28px" href="/pricing/">See packages &amp; pricing</a></div>
  <div class="trust" style="margin:26px 0 40px"><span><svg><use href="#i-check"/></svg>First brand board in 48 hours</span><span><svg><use href="#i-check"/></svg>Fixed prices in USD</span><span><svg><use href="#i-check"/></svg>Source files &amp; copyright included</span></div>
</div></section>
<section class="band" style="padding-top:0"><div class="inner"><div class="svc">{secs}</div></div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Packages and prices for {esc(loc["name"])} clients</h2><p class="lede">Fixed, one-time pricing in US dollars. One designer, start to finish.</p></div>{plans_html()}</div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Recent brand identities</h2></div>{cards(works[:3])}</div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">{esc(loc["name"])} branding FAQs</h2></div>{faq_html(loc["faqs"])}</div></section>
{cta_block("Let's design your " + loc["name"] + " brand", "Book a short call at a time that suits you. Your first full brand board arrives within 48 hours.")}
<section class="band" style="padding:56px 0"><div class="inner"><p class="cta-note" style="text-align:center;margin-bottom:16px">{('States' if hub['slug'] == 'usa' else 'Cities') if loc.get('hub') else 'More service areas'}</p><div class="links-row">{area_links}{other_hub}</div><p class="cta-note" style="text-align:center;margin:28px 0 16px">Services</p><div class="links-row">{svc_links_row()}</div></div></section>"""
        if loc.get("hub"):
            area = {"@type": "Country", "name": hub["country"]}
        else:
            area = {"@type": "City", "name": loc["name"], "containedInPlace": {"@type": "State" if hub["slug"] == "usa" else "AdministrativeArea", "name": loc["state"]}}
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "Service", "name": loc["h1"], "serviceType": "Brand identity design", "description": loc["description"], "url": url,
             "provider": provider, "areaServed": area, "availableChannel": {"@type": "ServiceChannel", "serviceUrl": url, "name": "Remote (video call, email, WhatsApp)"}, "offers": offers},
            faq_ld(loc["faqs"]),
            bc_ld(*([(hub["name"], url)] if loc.get("hub") else [(hub["name"], f"{SITE}/{hub['slug']}/"), (loc["name"], url)]))]}
        write_page(f"{path}index.html", page(loc["title"], loc["description"], url, "img/a018.jpg", ld, body), url)

    # ---------- US state hubs (/<state>/) and city pages (/<state>/<city>/) ----------
    # Data: content/us_cities.json (tools/gen_us.py): every US city with 100k+ people, its county,
    # time zone, nearby cities and (for big cities) neighborhoods. Remote service only: no addresses.
    page_of = {(c["state"], c["name"]): f'/{c["state_slug"]}/{c["slug"]}/' for c in us_cities}
    IND_LINKS = [("beauty-wellness", "skincare, beauty and wellness brands"), ("food-drink", "restaurants, cafés and food brands"),
                 ("tech-fintech", "tech, SaaS and fintech startups"), ("fashion-luxury", "fashion and luxury labels"), ("sports", "gyms, sports clubs and fitness brands")]
    intro_variants = [
        "Customers in {city} judge a business in seconds, from a storefront, a website or an Instagram profile. I design logos and complete brand identities for {city} founders and small businesses who need to look established, without agency prices or agency timelines.",
        "{city} is home to about {pop} people and a lot of competition for their attention. I'm a brand identity designer who works remotely with {city} businesses: a short call, a first brand board in 48 hours, and a finished identity you own.",
        "Whether you're launching in {city} or rebranding a business that has outgrown its look, a professional identity is what makes people trust you before they talk to you. I design human-made logos and brand systems for {city} businesses, remotely, at fixed prices.",
        "I design logos and brand identities for businesses across {city} and {county_txt}. Everything is designed by me, by hand, and delivered online, so {city} founders get studio-quality branding with a first brand board in 48 hours.",
    ]

    def fmt_pop(n):
        return f"{round(n / 1_000_000, 1)} million" if n >= 1_000_000 else f"{round(n / 1000):,}" + ",000"

    def city_faqs(c, custom):
        name, st, sn = c["name"], c["state"], c["state_name"]
        f = [
            [f"How much does a logo cost for a {name} business?", f"My packages are fixed for every client, wherever you are in {sn}: $250 for a logo with colours, type, mockups and guidelines; $450 for three concepts, complete guidelines and a social kit; $1,050 for the full Brand Ecosystem."],
            [f"Do you work with {name} businesses remotely?", f"Yes. All work is online: a call booked in your own time zone, concepts as a brand board, feedback by email or WhatsApp, and final files by download. You never need to travel or meet in person."],
            [f"How fast can I get a logo in {name}?", "Your first full brand board arrives within 48 hours of the brief. Basic and Premium packages are completed in 2 days; The Brand Ecosystem takes 5 business days."],
            [f"Can my logo be trademarked in {sn}?", "I don't file trademarks, but every logo is original and human-designed, and you receive clean source files. A trademark attorney can advise on a federal USPTO registration, which covers every state."],
        ]
        return (custom.get("faqs", []) if custom else []) + f

    from florida import county_slug, zip_index, portfolio_html
    PORT = json.loads((ROOT / "content" / "portfolio.json").read_text(encoding="utf-8"))
    ZIPS = json.loads((ROOT / "content" / "fl_zips.json").read_text(encoding="utf-8"))
    fl_svcs = yaml.safe_load((ROOT / "content" / "florida.yaml").read_text(encoding="utf-8"))["services"]
    fl_intro = [
        "I design logos and brand identities for {city} businesses and the rest of {county_txt}. Human-made, delivered online, at fixed prices from $250, with a first brand board within 48 hours.",
        "Florida is crowded with new businesses, and {city} is no exception. A clear, professional identity is how a {city} business looks established from its first sign, post or Google listing. I design them remotely, start to finish.",
        "From a new LLC registered on Sunbiz to a {city} business that has outgrown a DIY logo, I design brand identities that work on storefronts, vehicles, Instagram and Google Maps. Remote, fixed prices, first board in 48 hours.",
        "{city} founders get the same senior designer and the same fixed prices as my clients in Miami or New York: a short call, a first brand board in 48 hours, and an identity you own outright.",
    ]
    for c in us_cities:
        name, st, sn = c["name"], c["state"], c["state_name"]
        custom = us_custom.get(name) if st in ("NY", "CA", "FL", "TX", "IL") else None
        if custom and custom.get("state") and custom["state"] != sn and not (custom["name"] == "New York" and name == "New York City"):
            custom = None
        if name == "New York City":
            custom = us_custom.get("New York")
        path = f'{c["state_slug"]}/{c["slug"]}/'
        url = f"{SITE}/{path}"
        county_txt = c["county"] if c["county"].startswith("the ") else (f'{c["county"]} County' if c["county"] else sn)
        h = sum(map(ord, name + st))
        v = (intro_variants + fl_intro)[h % 8] if st == "FL" else intro_variants[h % len(intro_variants)]
        intro = custom["intro"] if custom else v.format(city=name, pop=fmt_pop(c["pop"]), county_txt=county_txt)
        secs = ""
        if custom:
            secs += f"<h2>What {esc(name)} businesses ask me for</h2><ul>" + "".join(f"<li>{esc(n)}</li>" for n in custom["needs"]) + "</ul>"
        secs += f"<h2>Who I design for in {esc(name)}</h2><p>Brand identities for " + ", ".join(f'<a href="/branding/{s_}/">{esc(t)}</a>' for s_, t in IND_LINKS) + f". Plus service businesses, real estate, home services and professional firms across {esc(county_txt)}. Need only a mark? See <a href=\"/logo-design/\">logo design</a>; launching something new? See <a href=\"/startup-branding/\">startup branding</a>.</p>"
        nb = c.get("nb") or []
        near_links = [f'<a href="{page_of[(st, n)]}">{esc(n)}</a>' if (st, n) in page_of else esc(n) for n in c["near"]]
        if nb or near_links:
            secs += f"<h2>Areas I serve in and around {esc(name)}</h2>"
            if nb:
                secs += f"<p>Businesses in every part of {esc(name)}, including " + ", ".join(esc(x) for x in nb[:-1]) + (" and " if len(nb) > 1 else "") + esc(nb[-1]) + ".</p>"
            if near_links:
                secs += f"<p>Nearby cities I also work with: " + ", ".join(near_links) + ".</p>"
        tzline = (f'{esc(name)} is on {c["tz"]} Time, and Pakistan (where I work) is {c["off_lo"]} hours ahead' if c["off_lo"] == c["off_hi"]
                  else f'{esc(name)} is on {c["tz"]} Time, and Pakistan (where I work) is {c["off_lo"]}–{c["off_hi"]} hours ahead, depending on daylight saving')
        secs += f"<h2>Working with a remote designer from {esc(name)}</h2><p>{tzline}. Calls are booked on Calendly, which shows open times in your own time zone, and a brief sent at the end of your day is worked on while you sleep. Everything else happens by email, WhatsApp and shared files.</p>"
        if st == "FL":
            cs_ = county_slug(c["county"])
            fl_line = f'{esc(name)} is in <a href="/florida/{cs_}/">{esc(c["county"])} County</a>'
            if c.get("seat"):
                fl_line += ", where it's the county seat"
            if c.get("metro"):
                fl_line += f', part of the {esc(c["metro"])} metro area'
            pick = [fl_svcs[(h + i) % len(fl_svcs)] for i in range(3)]
            zs = zip_index(ZIPS, c)
            zip_p = (f"<p>ZIP codes I serve in and around {esc(name)}: " + ", ".join(zs) + f'. See <a href="/florida/zip-codes/">every Florida ZIP code</a>.</p>') if zs else ""
            secs += f"<h2>Branding for {esc(name)} and {esc(c['county'])} County</h2>{zip_p}<p>{fl_line}. I work with businesses in every town and community in the county, and across <a href=\"/florida/\">all of Florida</a>. Popular with Florida clients: " + ", ".join(f'<a href="/florida/{x["slug"]}/">{esc(x["kw"])}</a>' for x in pick) + ".</p>"
        faqs = city_faqs(c, custom)
        if st == "FL":
            others = sorted([o for o in us_states[c["state_slug"]]["cities"] if o["slug"] != c["slug"]],
                            key=lambda o: (o["county"] != c["county"], (o["lat"] - c["lat"]) ** 2 + (o["lon"] - c["lon"]) ** 2))[:12]
        else:
            others = [o for o in us_states[c["state_slug"]]["cities"] if o["slug"] != c["slug"]][:12]
        other_links = "".join(f'<a href="/{o["state_slug"]}/{o["slug"]}/">{esc(o["name"])}</a>' for o in others)
        title = f"Logo Designer for {name}, {st} Businesses | Shahab"
        if len(title) > 60:
            title = f"Logo Designer for {name}, {st} | Shahab"
        desc = f"Human-designed logos and brand identities for {name}, {st} businesses. Remote, fixed prices from $250, first brand board in 48 hours."
        body = f"""<section class="hero ph"><div class="aura"><i></i><i></i><i></i><i></i></div><div class="inner">
  {crumbs(("USA", "/usa/"), (sn, f"/{c['state_slug']}/"), (name, None))}
  <span class="tagc">{esc(name)}, {st} · remote brand designer</span>
  <h1>Logo and brand identity design for {esc(name)} businesses</h1>
  <p class="lede">{esc(intro)}</p>
  <div class="ctas"><a class="btn primary lg" href="{CAL}" target="_blank" rel="noopener">Book a call in your time zone {arrow}</a><a class="btn ghost lg" style="padding-right:28px" href="/pricing/">See packages &amp; pricing</a></div>
  <div class="trust" style="margin:26px 0 40px"><span><svg><use href="#i-check"/></svg>First brand board in 48 hours</span><span><svg><use href="#i-check"/></svg>Fixed prices in USD</span><span><svg><use href="#i-check"/></svg>Source files &amp; copyright included</span></div>
</div></section>
<section class="band" style="padding-top:0"><div class="inner"><div class="svc">{secs}</div></div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Branding packages for {esc(name)} businesses</h2><p class="lede">Fixed, one-time pricing in US dollars. One designer, start to finish.</p></div>{plans_html()}</div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Recent brand identities</h2></div>{cards([works[(h + i) % len(works)] for i in range(3)])}</div></section>
{portfolio_html(PORT, h, esc, "More brand identities I've designed") if st == "FL" else ""}
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">{esc(name)} logo and branding FAQs</h2></div>{faq_html(faqs[h % len(faqs):] + faqs[:h % len(faqs)])}</div></section>
{cta_block("Let's design your " + name + " brand", "Book a short call at a time that suits you. Your first full brand board arrives within 48 hours.")}
<section class="band" style="padding:56px 0"><div class="inner"><p class="cta-note" style="text-align:center;margin-bottom:16px">More cities in {esc(sn)}</p><div class="links-row"><a href="/{c['state_slug']}/">All of {esc(sn)}</a>{other_links}</div><p class="cta-note" style="text-align:center;margin:28px 0 16px">Services</p><div class="links-row">{svc_links_row()}</div></div></section>"""
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "Service", "name": f"Logo and brand identity design for {name}, {st} businesses", "serviceType": "Brand identity design",
             "description": desc, "url": url, "provider": provider,
             "areaServed": {"@type": "City", "name": name, "containedInPlace": {"@type": "State", "name": sn}},
             "availableChannel": {"@type": "ServiceChannel", "serviceUrl": url, "name": "Remote (video call, email, WhatsApp)"}, "offers": offers},
            faq_ld(faqs),
            bc_ld(("USA", f"{SITE}/usa/"), (sn, f"{SITE}/{c['state_slug']}/"), (name, url))]}
        write_page(f"{path}index.html", page(title, desc, url, "img/a018.jpg", ld, body), url)

    from florida import build_florida
    build_florida(dict(ROOT=ROOT, SITE=SITE, CAL=CAL, esc=esc, page=page, crumbs=crumbs, bc_ld=bc_ld, faq_ld=faq_ld, faq_html=faq_html,
                       cta_block=cta_block, plans_html=plans_html, cards=cards, works=works, svc_links_row=svc_links_row, provider=provider,
                       offers=offers, arrow=arrow, write_page=write_page, us_cities=us_cities))
    for ss, stt in sorted(us_states.items()):
        if ss == "florida":
            continue
        url = f"{SITE}/{ss}/"
        sn = stt["name"]
        cs = sorted(stt["cities"], key=lambda x: -x["pop"])
        tzs = sorted({(x["tz"], x["off_lo"], x["off_hi"]) for x in cs})
        tz_txt = "; ".join(f'{t} Time: Pakistan is {lo} hours ahead' if lo == hi else f'{t} Time: Pakistan is {lo}–{hi} hours ahead' for t, lo, hi in tzs)
        links = "".join(f'<a href="/{ss}/{x["slug"]}/">{esc(x["name"])}</a>' for x in cs)
        top = ", ".join(x["name"] for x in cs[:4])
        faqs = [[f"Do you work with businesses across {sn}?", f"Yes. All work is remote, so it doesn't matter whether you're in {top} or a small town anywhere in {sn}."],
                [f"How much does branding cost for a {sn} business?", "Fixed packages: $250, $450 or $1,050, paid once in US dollars, with source files and copyright included."],
                ["How fast is the first draft?", "Your first full brand board arrives within 48 hours of the brief."]]
        title = f"Logo & Brand Identity Designer for {sn} Businesses | Shahab"
        if len(title) > 60:
            title = f"Logo Designer for {sn} Businesses | Shahab"
        desc = f"Human-designed logos and brand identities for businesses across {sn}, including {top}. Remote, from $250, first brand board in 48 hours."
        if len(desc) > 160:
            desc = f"Human-designed logos and brand identities for businesses across {sn}. Remote, fixed prices from $250, first brand board in 48 hours."
        body = f"""<section class="hero ph"><div class="aura"><i></i><i></i><i></i><i></i></div><div class="inner">
  {crumbs(("USA", "/usa/"), (sn, None))}
  <span class="tagc">{esc(sn)} · remote brand designer</span>
  <h1>Logo and brand identity design for {esc(sn)} businesses</h1>
  <p class="lede">I design logos and complete brand identities for founders and small businesses across {esc(sn)}, from {esc(top)} to smaller towns. Remote, fixed prices from $250, and a first brand board in 48 hours.</p>
  <div class="ctas"><a class="btn primary lg" href="{CAL}" target="_blank" rel="noopener">Book a call in your time zone {arrow}</a><a class="btn ghost lg" style="padding-right:28px" href="/pricing/">See packages &amp; pricing</a></div>
</div></section>
<section class="band" style="padding-top:0"><div class="inner"><div class="head rv-up"><h2 class="md">Cities I serve in {esc(sn)}</h2></div><div class="links-row">{links}</div>
<div class="svc" style="margin-top:40px"><h2>Time zones</h2><p>{esc(tz_txt)}. Calls are booked on Calendly in your own time zone.</p></div></div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Branding packages for {esc(sn)} businesses</h2></div>{plans_html()}</div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">{esc(sn)} branding FAQs</h2></div>{faq_html(faqs)}</div></section>
{cta_block("Let's design your brand", "Book a short call at a time that suits you. Your first full brand board arrives within 48 hours.")}
<section class="band" style="padding:56px 0"><div class="inner"><p class="cta-note" style="text-align:center;margin-bottom:16px">Services</p><div class="links-row">{svc_links_row()}</div><p class="cta-note" style="text-align:center;margin:28px 0 16px"><a href="/usa/">All US states</a></p></div></section>"""
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "Service", "name": f"Logo and brand identity design for {sn} businesses", "serviceType": "Brand identity design", "description": desc, "url": url,
             "provider": provider, "areaServed": {"@type": "State", "name": sn}, "offers": offers},
            faq_ld(faqs), bc_ld(("USA", f"{SITE}/usa/"), (sn, url))]}
        write_page(f"{ss}/index.html", page(title, desc, url, "img/a018.jpg", ld, body), url)

    # ---------- about ----------
    url = f"{SITE}/about/"
    secs = ""
    for sec in about["sections"]:
        secs += f'<h2>{esc(sec["h2"])}</h2>' + "".join(f"<p>{x}</p>" for x in sec.get("p", []))
        if sec.get("ul"):
            secs += "<ul>" + "".join(f"<li>{li}</li>" for li in sec["ul"]) + "</ul>"
    facts = "".join(f"<div><span>{esc(k)}</span><b style='font-weight:500'>{esc(v)}</b></div>" for k, v in about["facts"])
    body = f"""<section class="hero ph"><div class="aura"><i></i><i></i><i></i><i></i></div><div class="inner">
  {crumbs(("About", None))}
  <span class="tagc">About</span>
  <h1>{esc(about["h1"])}</h1>
  <p class="lede">{esc(about["intro"])}</p>
  <div class="ctas"><a class="btn primary lg" href="{CAL}" target="_blank" rel="noopener">Book a call {arrow}</a><a class="btn ghost lg" style="padding-right:28px" href="/#work">See the work</a></div>
</div></section>
<section class="band"><div class="inner"><div class="about-grid">
  <div><img src="/img/shahab.jpg" alt="Abdullah Shahab, brand identity designer" fetchpriority="high"><div class="factlist">{facts}</div></div>
  <div class="svc" style="margin:0">{secs}<h2>Contact</h2><p>Email <a href="mailto:imabdullahshahab@gmail.com">imabdullahshahab@gmail.com</a>, message me on <a href="https://wa.me/923118440498" target="_blank" rel="noopener">WhatsApp (+92 311 8440498)</a>, follow <a href="https://www.instagram.com/imabdullahshahab" target="_blank" rel="noopener">@imabdullahshahab</a> on Instagram, or <a href="{CAL}" target="_blank" rel="noopener">book a 30-minute call</a>.</p></div>
</div></div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Selected case studies</h2></div>{cards(works[:3])}</div></section>
{cta_block("Let's design your brand", "Tell me about your business on a short call. Your first full brand board arrives within 48 hours.")}"""
    person = {**PERSON, "alternateName": "Shahab", "jobTitle": "Brand Identity Designer", "image": SITE + "/img/shahab.jpg",
              "description": about["description"], "worksFor": provider, "sameAs": SAME_AS,
              "hasCredential": {"@type": "EducationalOccupationalCredential", "credentialCategory": "degree", "name": "BS in Graphic Design (Fine Arts)"},
              "knowsAbout": ["Logo design", "Brand identity design", "Brand guidelines", "Packaging design", "Rebranding"],
              "homeLocation": {"@type": "Country", "name": "Pakistan"}}
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "ProfilePage", "url": url, "name": about["title"], "mainEntity": {"@id": PERSON["@id"]}},
        person, bc_ld(("About", url))]}
    write_page("about/index.html", page(about["title"], about["description"], url, "img/shahab.jpg", ld, body), url)
    return works, inds
