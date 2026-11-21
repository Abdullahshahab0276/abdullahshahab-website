"""Florida statewide build: /florida/ hub, 67 county pages, Florida service pages.
City pages (/florida/<city>/) are built by pages.py from content/us_cities.json.
Data: content/florida.yaml (copy + sourced facts), content/fl_places_all.json (every populated
place in Florida from GeoNames, tools/gen_fl.py)."""
import json, math, re
import yaml


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("st.", "saint").replace(".", "")).strip("-")


def county_slug(county):
    return slug(county) + "-county"


def _d(a, b):
    return math.hypot((a["lat"] - b["lat"]) * 111, (a["lon"] - b["lon"]) * 111 * 0.88)


def zip_index(zips, c):
    """ZIP codes for a city page: USPS place name matches, or ZIP centroid within 6 km, same county."""
    return sorted({z["zip"] for z in zips if z["county"] == c["county"] and (z["place"] == c["name"] or _d(z, c) < 6)})


def portfolio_html(port, h, esc, title, cats=None):
    """Six portfolio brand boards, rotated per page; optionally filtered by category keywords."""
    pool = [p for p in port if not cats or any(k in p["category"] for k in cats)]
    pool += [p for p in port if p not in pool]
    pick = [pool[(h + i * 7) % len(pool)] for i in range(6)] if not cats else pool[:6]
    seen, out = set(), []
    for p in pick + port:
        if p["image"] not in seen and len(out) < 6:
            seen.add(p["image"]); out.append(p)
    figs = "".join(f'<figure><img src="/{p["image"]}" alt="{esc(p["alt"])}" loading="lazy"><figcaption>{esc(p["name"])} · {esc(p["category"])}</figcaption></figure>' for p in out)
    return f'<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">{esc(title)}</h2></div><div class="pgrid">{figs}</div><div class="cta-wrap"><a class="btn primary cta" href="/#work">See the full portfolio <span class="ar"><svg><use href="#i-arrow"/></svg></span></a></div></div></section>'


def build_florida(x):
    ROOT, SITE, CAL, esc = x["ROOT"], x["SITE"], x["CAL"], x["esc"]
    page, crumbs, bc_ld, faq_ld, faq_html, cta_block = x["page"], x["crumbs"], x["bc_ld"], x["faq_ld"], x["faq_html"], x["cta_block"]
    plans_html, cards, works, svc_links_row, provider, offers, arrow, write_page = (
        x["plans_html"], x["cards"], x["works"], x["svc_links_row"], x["provider"], x["offers"], x["arrow"], x["write_page"])
    fl = yaml.safe_load((ROOT / "content" / "florida.yaml").read_text(encoding="utf-8"))
    places = json.loads((ROOT / "content" / "fl_places_all.json").read_text(encoding="utf-8"))
    cities = [c for c in x["us_cities"] if c["state"] == "FL"]
    city_by_slug = {c["slug"]: c for c in cities}
    metro_of = {}
    for c in cities:
        if c["metro"]:
            metro_of.setdefault(c["county"], c["metro"])
    counties = {}
    for p in places:
        counties.setdefault(p["county"], []).append(p)
    svcs = fl["services"]
    port = json.loads((ROOT / "content" / "portfolio.json").read_text(encoding="utf-8"))
    zips = json.loads((ROOT / "content" / "fl_zips.json").read_text(encoding="utf-8"))
    city_by_name = {(c["name"], c["county"]): c for c in cities}
    cats = {"restaurant-branding": ["Food", "Café", "Coffee", "Beverage", "Dessert"], "med-spa-branding": ["Beauty", "Spa", "Skincare", "Wellness"],
            "real-estate-branding": ["Real Estate", "Luxury"], "bilingual-branding": ["Food", "Beauty", "Fashion"]}

    def fl_svc_row(exclude=None):
        return "".join(f'<a href="/florida/{s["slug"]}/">{esc(s["kw"])}</a>' for s in svcs if s["slug"] != exclude)

    hero = lambda parts, tag, h1, intro: f"""<section class="hero ph"><div class="aura"><i></i><i></i><i></i><i></i></div><div class="inner">
  {crumbs(*parts)}
  <span class="tagc">{esc(tag)}</span>
  <h1>{esc(h1)}</h1>
  <p class="lede">{esc(intro)}</p>
  <div class="ctas"><a class="btn primary lg" href="{CAL}" target="_blank" rel="noopener">Book a call in your time zone {arrow}</a><a class="btn ghost lg" style="padding-right:28px" href="/pricing/">See packages &amp; pricing</a></div>
  <div class="trust" style="margin:26px 0 40px"><span><svg><use href="#i-check"/></svg>First brand board in 48 hours</span><span><svg><use href="#i-check"/></svg>Fixed prices in USD</span><span><svg><use href="#i-check"/></svg>Source files &amp; copyright included</span></div>
</div></section>"""
    area_fl = {"@type": "State", "name": "Florida"}
    pages = []

    # ---------- Florida service / keyword pages: /florida/<service>/ ----------
    for i, s in enumerate(svcs):
        url = f"{SITE}/florida/{s['slug']}/"
        secs = ""
        for sec in s["sections"]:
            secs += f"<h2>{esc(sec['h2'])}</h2>" + "".join(f"<p>{p}</p>" for p in sec.get("p", []))
            if sec.get("ul"):
                secs += "<ul>" + "".join(f"<li>{li}</li>" for li in sec["ul"]) + "</ul>"
            if sec.get("table"):
                hr, *rows = sec["table"]
                secs += '<div class="twrap"><table class="ptable"><thead><tr>' + "".join(f"<th>{esc(h)}</th>" for h in hr) + "</tr></thead><tbody>" + "".join(
                    "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>"
        top = sorted(cities, key=lambda c: -c["pop"])
        pick = top[i * 3 % 20: i * 3 % 20 + 8]
        secs += "<h2>Where in Florida</h2><p>I work with businesses in all 67 Florida counties, including " + ", ".join(
            f'<a href="/florida/{c["slug"]}/">{esc(c["name"])}</a>' for c in pick) + ". Browse every city and county on the <a href=\"/florida/\">Florida page</a>.</p>"
        related = "".join(f'<a href="{u}">{esc(u.strip("/").split("/")[-1].replace("-", " ").capitalize())}</a>' for u in s.get("links", []))
        faqs = s["faqs"] + fl["hub"]["faqs"][1:3]
        body = hero((("USA", "/usa/"), ("Florida", "/florida/"), (s["kw"], None)), "Florida · remote brand designer", s["h1"], s["intro"]) + f"""
<section class="band" style="padding-top:0"><div class="inner"><div class="svc">{secs}<h2>Related</h2><p class="links-row" style="justify-content:flex-start">{related}</p></div></div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Packages for Florida businesses</h2><p class="lede">Fixed, one-time pricing in US dollars. One designer, start to finish.</p></div>{plans_html()}</div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Recent brand identities</h2></div>{cards([works[(i + k) % len(works)] for k in range(3)])}</div></section>
{portfolio_html(port, i * 5, esc, "Brand identities I've designed", cats.get(s["slug"]))}
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">FAQs</h2></div>{faq_html(faqs)}</div></section>
{cta_block("Let's design your Florida brand", "Book a short call at a time that suits you. Your first full brand board arrives within 48 hours.")}
<section class="band" style="padding:56px 0"><div class="inner"><p class="cta-note" style="text-align:center;margin-bottom:16px">More Florida services</p><div class="links-row"><a href="/florida/">All of Florida</a>{fl_svc_row(s['slug'])}</div></div></section>"""
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "Service", "name": s["h1"], "serviceType": s["kw"], "description": s["description"], "url": url, "provider": provider,
             "areaServed": area_fl, "availableChannel": {"@type": "ServiceChannel", "serviceUrl": url, "name": "Remote (video call, email, WhatsApp)"}, "offers": offers},
            faq_ld(faqs), bc_ld(("USA", f"{SITE}/usa/"), ("Florida", f"{SITE}/florida/"), (s["kw"], url))]}
        write_page(f"florida/{s['slug']}/index.html", page(s["title"], s["description"], url, "img/a018.jpg", ld, body), url)

    # ---------- county pages: /florida/<county>-county/ ----------
    intros = [
        "I design logos and brand identities for businesses across {cn}, from {top} to the smallest communities in the county. Everything is remote, priced from $250, with a first brand board in 48 hours.",
        "{cn} is home to {n} cities, towns and communities, and I work with founders and small businesses in all of them. Human-designed logos and complete identities, delivered online at fixed prices.",
        "Whether your business is in {top} or a rural part of {cn}, you get the same thing: a short call, a first brand board within 48 hours, and a finished identity with source files and copyright.",
    ]
    for cn_short, ps in sorted(counties.items()):
        cn = f"{cn_short} County"
        cs = county_slug(cn_short)
        url = f"{SITE}/florida/{cs}/"
        ps = sorted(ps, key=lambda p: -p["pop"])
        withpage = [p for p in ps if p["slug"] and p["slug"] in city_by_slug]
        top_names = [p["name"] for p in ps[:3]]
        top = ", ".join(top_names[:-1]) + (" and " if len(top_names) > 1 else "") + top_names[-1]
        h = sum(map(ord, cn))
        intro = intros[h % len(intros)].format(cn=cn, top=top, n=len(ps))
        seat = next((p["name"] for p in ps if p["seat"]), None)
        metro = metro_of.get(cn_short)
        tzs = sorted({p.get("tz", "Eastern") for p in ps})
        place_html = ", ".join((f'<a href="/florida/{p["slug"]}/">{esc(p["name"])}</a>' if p in withpage else esc(p["name"])) for p in ps)
        secs = f"<h2>Cities, towns and communities in {esc(cn)}</h2><p>I serve every part of {esc(cn)}: {place_html}.</p>"
        about = []
        if seat:
            about.append(f"The county seat is {esc(seat)}")
        if metro:
            about.append(f"it's part of the {esc(metro)} metro area")
        about.append(f"local time is {' and '.join(tzs)} Time" + (", and Pakistan (where I work) is 9–10 hours ahead in Eastern Time or 10–11 in Central" if len(tzs) > 1 else
                     (", and Pakistan (where I work) is 9–10 hours ahead" if tzs == ["Eastern"] else ", and Pakistan (where I work) is 10–11 hours ahead")))
        cz = {}
        for z in zips:
            if z["county"] == cn_short:
                cz.setdefault(z["place"], []).append(z["zip"])
        if cz:
            def zl(pl):
                c_ = city_by_name.get((pl, cn_short))
                return f'<a href="/florida/{c_["slug"]}/">{esc(pl)}</a>' if c_ else esc(pl)
            secs += f"<h2>{esc(cn)} ZIP codes I serve</h2><p>" + "; ".join(f"{zl(pl)}: {', '.join(v)}" for pl, v in sorted(cz.items())) + ".</p>"
        secs += f"<h2>Working with {esc(cn)} businesses remotely</h2><p>{'; '.join(about)}. Calls are booked on Calendly in your own time zone, and a brief sent at the end of your day is worked on overnight.</p>"
        secs += "<h2>Florida services</h2><p>" + ", ".join(f'<a href="/florida/{s["slug"]}/">{esc(s["kw"])}</a>' for s in svcs) + ".</p>"
        if seat:
            first_faq = [f"Do you work with businesses in {seat} and the rest of {cn}?", f"Yes. All work is remote, so it doesn't matter whether you're in {seat} or a small community anywhere in {cn}."]
        else:
            first_faq = [f"Do you work with businesses across {cn}?", f"Yes. All work is remote, so I work with businesses in every part of {cn}."]
        faqs = [first_faq,
                [f"How much does a logo cost for a {cn} business?", "Fixed packages: $250, $450 or $1,050, paid once in US dollars, with source files and copyright included."],
                fl["hub"]["faqs"][2]]
        neighbors = sorted(counties, key=lambda k: (metro_of.get(k) != metro, k))
        near_c = [k for k in neighbors if k != cn_short][:8] if metro else []
        near_html = "".join(f'<a href="/florida/{county_slug(k)}/">{esc(k)} County</a>' for k in near_c)
        title = f"Logo Designer for {cn}, FL Businesses | Shahab"
        if len(title) > 60:
            title = f"Logo Designer for {cn}, FL | Shahab"
        desc = f"Human-designed logos and brand identities for businesses in {cn}, Florida, including {top}. Remote, from $250, first board in 48 hours."
        if len(desc) > 160:
            desc = f"Human-designed logos and brand identities for {cn}, Florida businesses. Remote, fixed prices from $250, first board in 48 hours."
        body = hero((("USA", "/usa/"), ("Florida", "/florida/"), (cn, None)), f"{cn}, FL · remote brand designer",
                    f"Logo and brand identity design in {cn}, Florida", intro) + f"""
<section class="band" style="padding-top:0"><div class="inner"><div class="svc">{secs}</div></div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Branding packages for {esc(cn)} businesses</h2><p class="lede">Fixed, one-time pricing in US dollars.</p></div>{plans_html()}</div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Recent brand identities</h2></div>{cards([works[(h + k) % len(works)] for k in range(3)])}</div></section>
{portfolio_html(port, h, esc, "More brand identities I've designed")}
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">{esc(cn)} branding FAQs</h2></div>{faq_html(faqs)}</div></section>
{cta_block("Let's design your brand", "Book a short call at a time that suits you. Your first full brand board arrives within 48 hours.")}
<section class="band" style="padding:56px 0"><div class="inner"><p class="cta-note" style="text-align:center;margin-bottom:16px">{'More counties in the ' + esc(metro) + ' area' if metro and near_html else 'Florida'}</p><div class="links-row"><a href="/florida/">All of Florida</a>{near_html}</div><p class="cta-note" style="text-align:center;margin:28px 0 16px">Services</p><div class="links-row">{svc_links_row()}</div></div></section>"""
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "Service", "name": f"Logo and brand identity design in {cn}, Florida", "serviceType": "Brand identity design", "description": desc, "url": url,
             "provider": provider, "areaServed": {"@type": "AdministrativeArea", "name": f"{cn}, Florida", "containedInPlace": area_fl}, "offers": offers},
            faq_ld(faqs), bc_ld(("USA", f"{SITE}/usa/"), ("Florida", f"{SITE}/florida/"), (cn, url))]}
        write_page(f"florida/{cs}/index.html", page(title, desc, url, "img/a018.jpg", ld, body), url)

    # ---------- hub: /florida/ ----------
    H = fl["hub"]
    url = f"{SITE}/florida/"
    by_metro = {}
    for k in sorted(counties):
        by_metro.setdefault(metro_of.get(k) or "Rural and small-town Florida", []).append(k)
    metro_pop = {m: sum(p["pop"] for k in ks for p in counties[k]) for m, ks in by_metro.items()}
    metro_html = ""
    for m in sorted(by_metro, key=lambda m: (m.startswith("Rural"), -metro_pop[m])):
        metro_html += f"<h3>{esc(m)}</h3><p>" + ", ".join(f'<a href="/florida/{county_slug(k)}/">{esc(k)} County</a>' for k in by_metro[m]) + "</p>"
    top = sorted(cities, key=lambda c: -c["pop"])
    city_links = "".join(f'<a href="/florida/{c["slug"]}/">{esc(c["name"])}</a>' for c in top)
    facts = "<div class=\"twrap\"><table class=\"ptable\"><thead><tr><th>Florida fact</th><th>Figure</th></tr></thead><tbody>" + "".join(
        f'<tr><td>{esc(k)}</td><td><a href="{u}" target="_blank" rel="noopener">{esc(v)}</a></td></tr>' for k, v, u in H["facts"]) + "</tbody></table></div>"
    svc_cards = "".join(f'<li><a href="/florida/{s["slug"]}/">{esc(s["kw"])}</a>: {esc(s["description"])}</li>' for s in svcs)
    body = hero((("USA", "/usa/"), ("Florida", None)), "Florida · remote brand designer", H["h1"], H["intro"]) + f"""
<section class="band" style="padding-top:0"><div class="inner"><div class="svc"><h2>Branding services for Florida businesses</h2><ul>{svc_cards}</ul>
<h2>Florida at a glance for new brands</h2>{facts}<p>Planning a name? Search <a href="https://dos.fl.gov/sunbiz/" target="_blank" rel="noopener">Sunbiz</a> first, and register a fictitious name if you'll trade under a name other than your legal or company name.</p>
<h2>Every Florida county</h2>{metro_html}<p>Looking for your ZIP code? See <a href="/florida/zip-codes/">all {len(zips):,} Florida ZIP codes I serve</a>.</p></div></div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">{len(top)} Florida cities and towns with their own page</h2><p class="lede">Every place with 10,000+ residents. Smaller towns, villages and communities are listed on each county page.</p></div><div class="links-row">{city_links}</div></div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Branding packages for Florida businesses</h2></div>{plans_html()}</div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Recent brand identities</h2></div>{cards(works[:3])}</div></section>
{portfolio_html(port, 3, esc, "Brand identities I've designed")}
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">Florida branding FAQs</h2></div>{faq_html(H["faqs"])}</div></section>
{cta_block("Let's design your Florida brand", "Book a short call at a time that suits you. Your first full brand board arrives within 48 hours.")}
<section class="band" style="padding:56px 0"><div class="inner"><p class="cta-note" style="text-align:center;margin-bottom:16px">Services</p><div class="links-row">{svc_links_row()}</div><p class="cta-note" style="text-align:center;margin:28px 0 16px"><a href="/usa/">All US states</a></p></div></section>"""
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Service", "name": H["h1"], "serviceType": "Brand identity design", "description": H["description"], "url": url, "provider": provider,
         "areaServed": area_fl, "offers": offers,
         "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Florida branding services", "itemListElement": [
             {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["kw"], "url": f"{SITE}/florida/{s['slug']}/"}} for s in svcs]}},
        faq_ld(H["faqs"]), bc_ld(("USA", f"{SITE}/usa/"), ("Florida", url))]}
    write_page("florida/index.html", page(H["title"], H["description"], url, "img/a018.jpg", ld, body), url)
    # ---------- ZIP directory: /florida/zip-codes/ ----------
    url = f"{SITE}/florida/zip-codes/"
    by_c = {}
    for z in zips:
        by_c.setdefault(z["county"], []).append(z)
    blocks = ""
    for k in sorted(by_c):
        rows = "".join(
            f'<span>{z["zip"]} · ' + (f'<a href="/florida/{city_by_name[(z["place"], k)]["slug"]}/">{esc(z["place"])}</a>' if (z["place"], k) in city_by_name else esc(z["place"])) + "</span><br>"
            for z in by_c[k])
        blocks += f'<h2 id="{county_slug(k)}"><a href="/florida/{county_slug(k)}/">{esc(k)} County</a> ({len(by_c[k])} ZIP codes)</h2><div class="ziplist">{rows}</div>'
    zfaqs = [["Do you serve my Florida ZIP code?", f"Yes. I work remotely with businesses in all {len(zips):,} Florida ZIP codes, from 32003 to 34997, at the same fixed prices from $250."],
             ["Does my location change the price or timeline?", "No. Every Florida client gets the same packages and a first brand board within 48 hours of the brief."]]
    title = "Florida ZIP Codes I Serve | Logo & Brand Design | Shahab"
    desc = f"Logo and brand identity design for businesses in every Florida ZIP code, all {len(zips):,}, listed by county. Remote, from $250, first board in 48 hours."
    body = hero((("USA", "/usa/"), ("Florida", "/florida/"), ("ZIP codes", None)), "Florida · every ZIP code",
                "Logo and branding for every Florida ZIP code",
                f"I work with businesses in all {len(zips):,} Florida ZIP codes. Find yours below, grouped by county, with links to your city or county page.") + f"""
<section class="band" style="padding-top:0"><div class="inner"><div class="svc">{blocks}</div></div></section>
<section class="band"><div class="inner"><div class="head rv-up"><h2 class="md">FAQs</h2></div>{faq_html(zfaqs)}</div></section>
{cta_block("Let's design your Florida brand", "Book a short call at a time that suits you. Your first full brand board arrives within 48 hours.")}"""
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Service", "name": "Logo and brand identity design for every Florida ZIP code", "serviceType": "Brand identity design", "description": desc,
         "url": url, "provider": provider, "areaServed": area_fl, "offers": offers},
        faq_ld(zfaqs), bc_ld(("USA", f"{SITE}/usa/"), ("Florida", f"{SITE}/florida/"), ("ZIP codes", url))]}
    write_page("florida/zip-codes/index.html", page(title, desc, url, "img/a018.jpg", ld, body), url)
    return {"metro_of": metro_of, "county_slug": county_slug, "services": svcs}
