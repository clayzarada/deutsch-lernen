// Deutsch lernen Plus: the AI gateway.
//
// The app talks to this function exactly as it would talk to the Claude API (the Anthropic SDK just gets a
// different base URL), so every AI feature works unchanged. The function:
//   1. checks the caller's Supabase sign-in,
//   2. checks that Plus is active and this month's AI spending is under the limit,
//   3. forwards the request to Anthropic with OUR key (users never see it),
//   4. logs tokens and cost, and returns Anthropic's answer untouched.
// It also answers GET .../status with the account's plan and this month's usage.
//
// Secrets (Supabase dashboard -> Edge Functions -> Secrets):
//   ANTHROPIC_API_KEY      required
//   AI_MONTHLY_CAP_USD     optional, default 4.00 (a profile's ai_cap_usd overrides it)
import { createClient } from "npm:@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const ANTHROPIC_KEY = Deno.env.get("ANTHROPIC_API_KEY") ?? "";
const DEFAULT_CAP = Number(Deno.env.get("AI_MONTHLY_CAP_USD") ?? "4");

// USD per million tokens: input, output, cache read. Cache writes cost 1.25x input. Keep in step with app/usage.py.
const PRICES: Record<string, [number, number, number]> = {
  "claude-opus-5-5": [4.0, 20.0, 0.2],
  "claude-sonnet-5-5": [2.0, 10.0, 0.1],
  "claude-haiku-5-5": [0.1, 0.5, 0.01],
};
// Plus runs on Sonnet (main tasks) and Haiku (quick tasks). Anything else, Opus included, is switched to Sonnet.
const ALLOWED = ["claude-sonnet-5-5", "claude-haiku-5-5"];
const FALLBACK_MODEL = "claude-sonnet-5-5";
const WEB_SEARCH_PER_1000 = 10.0;
const MAX_TOKENS = 16000;
const MAX_BODY = 8_000_000;  // bytes; scanned page images are the biggest thing the app sends
const BETAS = new Set(["server-side-fallback-2026-07-01"]);

const admin = createClient(SUPABASE_URL, SERVICE_KEY, { auth: { persistSession: false } });

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });
}
// Errors in Anthropic's shape, so the app's SDK shows the message.
function fail(status: number, type: string, message: string) {
  return json({ type: "error", error: { type, message } }, status);
}

function price(model: string) {
  for (const name of Object.keys(PRICES)) if (model?.startsWith(name)) return PRICES[name];
  return PRICES["claude-opus-5-5"];
}

function monthStart() {
  const d = new Date();
  return new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), 1)).toISOString();
}

async function account(req: Request) {
  const auth = req.headers.get("authorization") ?? "";
  const token = auth.replace(/^Bearer\s+/i, "");
  if (!token) return null;
  const { data, error } = await admin.auth.getUser(token);
  if (error || !data?.user) return null;
  const user = data.user;
  let { data: profile } = await admin.from("profiles").select("*").eq("user_id", user.id).maybeSingle();
  if (!profile) {
    await admin.from("profiles").insert({ user_id: user.id, email: user.email });
    profile = { plan: "free", plus_until: null, ai_cap_usd: null };
  }
  const plus = profile.plan === "plus" && (!profile.plus_until || new Date(profile.plus_until) > new Date());
  const cap = profile.ai_cap_usd != null ? Number(profile.ai_cap_usd) : DEFAULT_CAP;
  const { data: rows } = await admin.from("ai_usage").select("cost_usd").eq("user_id", user.id).gte("created_at", monthStart());
  const used = (rows ?? []).reduce((s: number, r: { cost_usd: number }) => s + Number(r.cost_usd), 0);
  return { user, profile, plus, cap, used };
}

Deno.serve(async (req) => {
  const url = new URL(req.url);
  const acct = await account(req);
  if (!acct) return fail(401, "authentication_error", "Your sign-in has expired. Sign in again under Settings → Account.");

  if (req.method === "GET" && url.pathname.endsWith("/status")) {
    return json({
      email: acct.user.email, plan: acct.profile.plan, plus: acct.plus, plus_until: acct.profile.plus_until,
      used_usd: Math.round(acct.used * 10000) / 10000, cap_usd: acct.cap,
      used_pct: acct.cap ? Math.min(100, Math.round((100 * acct.used) / acct.cap)) : 0,
    });
  }

  if (req.method !== "POST" || !url.pathname.endsWith("/v1/messages")) return fail(404, "not_found_error", "Unknown path.");
  if (!acct.plus) return fail(403, "permission_error", "AI features need Deutsch lernen Plus, or your own Claude API key under Settings.");
  if (acct.used >= acct.cap) {
    return fail(429, "rate_limit_error", "You've reached this month's AI limit for Plus. AI features come back at the start of next month; everything else keeps working.");
  }
  if (!ANTHROPIC_KEY) return fail(500, "api_error", "The AI service isn't configured yet.");

  const raw = await req.text();
  if (raw.length > MAX_BODY) return fail(413, "invalid_request_error", "That request is too large.");
  let b: Record<string, any>;
  try { b = JSON.parse(raw); } catch { return fail(400, "invalid_request_error", "Bad request body."); }
  if (b.stream) return fail(400, "invalid_request_error", "Streaming isn't supported.");
  // Only the fields the app uses; anything else (other tools, MCP servers, containers...) is dropped.
  const body: Record<string, unknown> = {
    model: ALLOWED.includes(String(b.model)) ? b.model : FALLBACK_MODEL,
    max_tokens: Math.min(Number(b.max_tokens) || 4000, MAX_TOKENS),
    messages: b.messages, system: b.system, output_config: b.output_config,
  };
  if (b.fallbacks === "default") body.fallbacks = "default";
  const ws = Array.isArray(b.tools) ? b.tools.find((t: any) => String(t?.type).startsWith("web_search_")) : null;
  if (ws) body.tools = [{ type: ws.type, name: "web_search", max_uses: Math.min(Number(ws.max_uses) || 5, 5) }];
  // Rough worst case for this call, so a burst of requests can't run far past the monthly limit.
  const [epi, epo] = price(String(body.model));
  // Base64 image data isn't text: count each image as ~2,000 tokens instead of by its length.
  const images = (raw.match(/"data":"[A-Za-z0-9+\/=]{200,}"/g) || []).length;
  const textLen = raw.replace(/"data":"[A-Za-z0-9+\/=]{200,}"/g, '"data":""').length;
  const estimate = (textLen / 3 + images * 2000) * epi / 1e6 + Number(body.max_tokens) * epo / 1e6 + (ws ? 5 * WEB_SEARCH_PER_1000 / 1000 : 0);
  if (acct.used + estimate > acct.cap * 1.05) {
    return fail(429, "rate_limit_error", "You've reached this month's AI limit for Plus. AI features come back at the start of next month; everything else keeps working.");
  }
  const feature = (req.headers.get("x-dl-feature") ?? "").slice(0, 40) || null;

  const headers: Record<string, string> = {
    "content-type": "application/json",
    "x-api-key": ANTHROPIC_KEY,
    "anthropic-version": req.headers.get("anthropic-version") ?? "2023-06-01",
  };
  const beta = (req.headers.get("anthropic-beta") ?? "").split(",").map((s) => s.trim()).filter((s) => BETAS.has(s)).join(",");
  if (beta) headers["anthropic-beta"] = beta;

  const upstream = await fetch("https://api.anthropic.com/v1/messages" + (url.searchParams.get("beta") === "true" ? "?beta=true" : ""), {
    method: "POST", headers, body: JSON.stringify(body),
  });
  const text = await upstream.text();

  if (upstream.ok) {
    try {
      const r = JSON.parse(text);
      const u = r.usage ?? {};
      const inp = u.input_tokens ?? 0, out = u.output_tokens ?? 0;
      const cread = u.cache_read_input_tokens ?? 0, cwrite = u.cache_creation_input_tokens ?? 0;
      const searches = u.server_tool_use?.web_search_requests ?? 0;
      const [pi, po, pc] = price(r.model ?? String(body.model));
      const cost = (inp * pi + out * po + cread * pc + cwrite * pi * 1.25) / 1e6 + searches * WEB_SEARCH_PER_1000 / 1000;
      await admin.from("ai_usage").insert({
        user_id: acct.user.id, feature, model: r.model ?? body.model, input_tokens: inp, output_tokens: out,
        cache_read: cread, cache_write: cwrite, web_searches: searches, cost_usd: cost,
      });
    } catch (e) {
      console.error("usage log failed", e);
    }
  } else if (upstream.status === 401 || upstream.status === 403) {
    console.error("Anthropic rejected the server key", upstream.status, text.slice(0, 300));
    return fail(502, "api_error", "The AI service is having trouble. Please try again later.");
  }
  return new Response(text, { status: upstream.status, headers: { "content-type": "application/json" } });
});
