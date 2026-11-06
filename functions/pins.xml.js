// Pinterest auto-publish feed. Serves only the pins whose scheduled date has arrived,
// so a new pin appears every day without rebuilding the site. Schedule: /pins-data.json
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

export async function onRequestGet({ request, env }) {
  const res = await env.ASSETS.fetch(new URL("/pins-data.json", request.url));
  const data = await res.json();
  const today = new Date().toISOString().slice(0, 10);
  const live = data.items.filter((p) => p.date <= today).slice(-150);
  const items = live.map((p) => `<item><title>${esc(p.title)}</title><link>${esc(p.link)}</link><guid isPermaLink="false">${esc(p.id)}</guid><pubDate>${new Date(p.date + "T09:00:00Z").toUTCString()}</pubDate><description>${esc(p.description)}</description><enclosure url="${esc(data.site + "/" + p.image)}" type="image/jpeg" length="0"/></item>`).join("");
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Shahab: branding pins</title><link>${data.site}/blog/</link><description>Brand identity work and branding guides from Shahab, a human brand designer.</description><language>en</language>${items}</channel></rss>`;
  return new Response(xml, { headers: { "content-type": "application/rss+xml; charset=utf-8", "cache-control": "public, max-age=3600" } });
}
