// Saves every website enquiry to the Cloudflare D1 database "site-enquiries",
// so no message is lost even if the email service has a problem.
const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json" } });

export async function onRequestPost({ request, env }) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ ok: false, error: "Invalid request" }, 400);
  }
  if (body.website) return json({ ok: true }); // honeypot: silently drop bots

  const clean = (v, max) => String(v ?? "").trim().slice(0, max);
  const name = clean(body.name, 120);
  const email = clean(body.email, 200);
  const type = clean(body.type, 120);
  const message = clean(body.message, 5000);
  if (!name || !message || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ ok: false, error: "Missing or invalid fields" }, 400);
  }

  await env.DB.prepare(
    "INSERT INTO enquiries (name, email, project_type, message, page, country, user_agent) VALUES (?, ?, ?, ?, ?, ?, ?)"
  )
    .bind(name, email, type, message, clean(request.headers.get("referer"), 300),
      clean(request.cf?.country, 8), clean(request.headers.get("user-agent"), 300))
    .run();

  return json({ ok: true });
}
