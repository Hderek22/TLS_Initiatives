# TLS Report Relay

Cloudflare Worker that sends the Progression Report by email as real HTML
with inline (CID) photo attachments, so each photo renders under the
section it belongs to — including in Outlook. The app posts the report
JSON here; this Worker forwards it to Resend, which does the actual
sending.

The app never talks to Resend directly and never holds the Resend API
key — only this Worker does, as an encrypted secret.

## One-time setup

1. **Resend** (resend.com) — create an account, add and verify a sending
   domain (Resend gives you DNS records to add), then create an API key.
   You need a domain you control for this; you can't send from a shared
   domain.

2. **Cloudflare** — create a free account at dash.cloudflare.com if you
   don't have one.

3. **Deploy the Worker.** Easiest via the dashboard: Workers & Pages →
   Create → paste in `report-relay.js` → Deploy. Or with the CLI:
   ```
   npm install -g wrangler
   wrangler login
   cd worker
   wrangler deploy
   ```

4. **Edit `wrangler.toml`** (or the dashboard's Variables tab) — set
   `FROM_ADDRESS` to an address at your verified Resend domain, and
   confirm `ALLOWED_ORIGIN` matches where the app is hosted.

5. **Set the two secrets** — never put these in a committed file:
   ```
   wrangler secret put RESEND_API_KEY
   wrangler secret put RELAY_SHARED_SECRET
   ```
   For `RELAY_SHARED_SECRET`, make up any random string, e.g.
   `openssl rand -hex 24`. It's not a real secret — it'll be visible in
   the app's client-side code — it just raises the bar against casual
   abuse of your Resend quota. The actual secret (`RESEND_API_KEY`)
   never leaves the Worker.

6. **Note the Worker's URL** (shown after deploy, e.g.
   `https://tls-report-relay.<you>.workers.dev`). Give that URL and the
   `RELAY_SHARED_SECRET` value to whoever maintains `index.html` — they
   go in the `RELAY_URL` / `RELAY_SHARED_SECRET` constants near the top
   of the `sendEmail` code.

## Testing

Submit a report from the app (ideally `/preview/` first) and confirm the
email arrives with photos inline under their sections. If the Worker is
unreachable or misconfigured, the app silently falls back to its
existing share-sheet/mailto behavior — nothing breaks either way.
