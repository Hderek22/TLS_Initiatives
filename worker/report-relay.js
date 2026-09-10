export default {
  async fetch(request, env) {
    const allowedOrigin = env.ALLOWED_ORIGIN || "https://hderek22.github.io";
    const corsHeaders = {
      "Access-Control-Allow-Origin": allowedOrigin,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, X-Relay-Secret",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }
    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405, headers: corsHeaders });
    }
    if (request.headers.get("X-Relay-Secret") !== env.RELAY_SHARED_SECRET) {
      return json({ error: "Unauthorized" }, 401, corsHeaders);
    }

    let body;
    try {
      body = await request.json();
    } catch (e) {
      return json({ error: "Invalid JSON" }, 400, corsHeaders);
    }

    const { to, subject, html, text, attachments } = body;
    if (!to || !Array.isArray(to) || !to.length || !subject || !html) {
      return json({ error: "Missing required fields (to, subject, html)" }, 400, corsHeaders);
    }
    if (to.length > 50) {
      return json({ error: "Too many recipients" }, 400, corsHeaders);
    }
    if (Array.isArray(attachments) && attachments.length > 60) {
      return json({ error: "Too many attachments" }, 400, corsHeaders);
    }

    const resendPayload = {
      from: env.FROM_ADDRESS,
      to,
      subject,
      html,
      text: text || undefined,
      attachments: (attachments || []).map(a => ({
        filename: a.filename,
        content: a.contentBase64,
        content_type: a.contentType,
        content_id: a.cid,
      })),
    };

    const resendRes = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(resendPayload),
    });

    const resendBody = await resendRes.text();
    if (!resendRes.ok) {
      return json({ error: "Resend API error", detail: resendBody }, 502, corsHeaders);
    }

    return new Response(resendBody, { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } });
  },
};

function json(obj, status, corsHeaders) {
  return new Response(JSON.stringify(obj), { status, headers: { ...corsHeaders, "Content-Type": "application/json" } });
}
