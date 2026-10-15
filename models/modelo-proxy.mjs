#!/usr/bin/env node
// JARVIS MODELO-PROXY (gateway local) — un solo selector /model con los Claude de siempre MÁS
// modelos de otros proveedores, incluidos los gratuitos o de plan.
//
// Claude Code habla con UNA sola ANTHROPIC_BASE_URL por sesión. Este gateway mira el campo `model`:
//   · claude-* / alias (sonnet, opus…)   → api.anthropic.com BYTE A BYTE, con SUS credenciales
//                                           (el login de suscripción pasa intacto: no se lee ni se guarda).
//   · "proveedor/modelo"                  → ese proveedor (profiles/gateway.json). Si habla OpenAI
//                                           (NIM, Gemini, Ollama) se traduce Anthropic<->OpenAI.
//   · "auto/…"                            → cadena con respaldo: si uno falla (429, 5xx, red, timeout), pasa al
//                                           siguiente SIN que Claude Code lo note.
//
// SEGURIDAD (auditada 2026-10-03; ver backups/gateway-pre-review-2026-10-03 para el antes):
//   · Escucha SOLO en 127.0.0.1 y exige Host de loopback + ausencia de Origin/Sec-Fetch-Site: una página web
//     (CSRF, DNS rebinding) no puede usarlo. Las rutas que gastan llaves exigen además un token de sesión.
//   · La llave de un proveedor nunca viaja a otro; las URL base se restringen a hosts permitidos (https).
//   · No registra cuerpos, cabeceras ni llaves; los errores del upstream se sanean antes de guardarse/mostrarse.
//   · Se apaga solo tras IDLE_MIN minutos sin uso real (y nunca con peticiones en curso).
import http from "node:http";
import https from "node:https";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";
import { Readable } from "node:stream";
import { pedidoAOpenAI, respuestaAAnthropic, crearTraductorStream, errorAnthropic } from "./anthropic-openai.mjs";

const PORT = Number(process.env.MODELO_PROXY_PORT || 8787);
const IDLE_MIN = Number(process.env.MODELO_PROXY_IDLE_MIN || 10);
const MAX_BODY = 64 * 1024 * 1024;
const ANTHROPIC = new URL(process.env.MODELO_PROXY_ANTHROPIC || "https://api.anthropic.com");
const CONFIG_PATH = process.env.MODELO_PROXY_CONFIG || path.join(os.homedir(), ".claude", "profiles", "gateway.json");
const TOKEN = process.env.MODELO_PROXY_TOKEN || crypto.randomBytes(32).toString("hex"); // sin token explícito, nadie lo conoce → rutas bloqueadas
const MODELO_VALIDO = /^[\w.\-:/@+[\]]{1,120}$/;
// Hosts permitidos para las URL base (M3 de la auditoría): una llave solo viaja a estos destinos.
const HOSTS_OK = (process.env.MODELO_PROXY_HOSTS_OK || "openrouter.ai,api.z.ai,googleapis.com,nvidia.com,kilo.ai,x.ai,groq.com,mistral.ai,cerebras.ai").split(",");
const LOOPBACK = new Set(["127.0.0.1", "localhost", "[::1]"]);

// Registro en archivo (el gateway arranca oculto: sin esto una caída es indiagnosticable). Tope 1 MB: al pasarlo se rota a .1
const LOG_ARCHIVO = process.env.MODELO_PROXY_LOG || path.join(process.env.LOCALAPPDATA || os.tmpdir(), "claude-gateway", "gateway.log");
const LOG_MAX = 1_000_000;
try { fs.mkdirSync(path.dirname(LOG_ARCHIVO), { recursive: true }); if (fs.statSync(LOG_ARCHIVO).size > LOG_MAX) fs.renameSync(LOG_ARCHIVO, LOG_ARCHIVO + ".1"); } catch { /* sin archivo aún o sin permisos: se sigue sin registro */ }
const log = (...a) => {
  const linea = `${new Date().toISOString().slice(11, 19)} [gateway] ${a.map((x) => (typeof x === "string" ? x : String(x?.stack ?? x))).join(" ")}`;
  console.error(linea);
  try { fs.appendFileSync(LOG_ARCHIVO, linea + "\n"); } catch { /* el registro nunca debe tumbar el proxy */ }
};
const sinSecretos = (t) => String(t ?? "").replace(/[A-Za-z0-9_\-]{24,}/g, "***").replace(/\s+/g, " ").slice(0, 160);
const esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const hashT = (t) => crypto.createHash("sha256").update(String(t)).digest();

// Un gateway no puede morir por una petición mala: se registra y se sigue.
process.on("uncaughtException", (e) => log("excepción no capturada:", e?.message));
process.on("unhandledRejection", (e) => log("promesa rechazada:", e?.message ?? e));

// ---------- configuración ----------
const resolverEnv = (v) => (typeof v === "string" && v.startsWith("env:") ? process.env[v.slice(4)] || "" : v);
function baseSegura(id, base) {
  if (!base) return "";
  try {
    const u = new URL(base);
    if (LOOPBACK.has(u.hostname) || LOOPBACK.has(`[${u.hostname}]`)) return u.protocol === "http:" || u.protocol === "https:" ? base : "";
    if (u.protocol !== "https:") { log(`proveedor ${id}: base ${u.hostname} NO es https → deshabilitado`); return ""; }
    if (!HOSTS_OK.some((h) => u.hostname === h || u.hostname.endsWith("." + h))) { log(`proveedor ${id}: host ${u.hostname} fuera de la lista permitida → deshabilitado`); return ""; }
    return base;
  } catch { return ""; }
}
let cfg;
try { cfg = JSON.parse(fs.readFileSync(CONFIG_PATH, "utf8")); } catch (e) { log("config ilegible:", e.message); process.exit(1); }
const proveedores = Object.create(null);
for (const [id, p] of Object.entries(cfg.providers || {})) proveedores[id] = { id, ...p, base: baseSegura(id, resolverEnv(p.base)), llave: p.key ? resolverEnv(p.key) : "" };
const combos = Object.assign(Object.create(null), cfg.combos || {});
const COOLDOWN_MS = (cfg.cooldown_s ?? 60) * 1000;
const IDLE_CHUNK_MS = (cfg.idle_chunk_s ?? 90) * 1000; // sin ningún byte del upstream durante este tiempo → se corta con error

// ---------- estado y estadísticas ----------
let ultimoUso = Date.now();
let activos = 0;
const stats = { inicio: new Date().toISOString(), peticiones: 0, claude: 0, rechazadas: 0, porDestino: Object.create(null), fallbacks: 0, ultimosErrores: [] };
const enfriando = new Map();
const lats = new Map(); // etiqueta -> últimas 200 latencias (ms hasta el primer byte) para p50/p95
const pct = (a, p) => { if (!a?.length) return null; const o = [...a].sort((x, y) => x - y); return o[Math.min(o.length - 1, Math.floor((p / 100) * o.length))]; };
const uso = new Map(); // provId -> { dia, tokens, hora, peticiones }: base de las cuotas por proveedor
function usoDe(id) {
  const iso = new Date().toISOString(); const dia = iso.slice(0, 10), hora = iso.slice(0, 13);
  let u = uso.get(id); if (!u) { u = { dia, tokens: 0, hora, peticiones: 0 }; uso.set(id, u); }
  if (u.dia !== dia) { u.dia = dia; u.tokens = 0; }
  if (u.hora !== hora) { u.hora = hora; u.peticiones = 0; }
  return u;
}
// Se salta un proveedor ANTES de agotar su cuota gratuita, en vez de esperar al 429 (p. ej. Kilo: 200 peticiones/hora/IP).
function sinCuota(prov) {
  const u = usoDe(prov.id);
  if (prov.cuota_peticiones_hora && u.peticiones >= prov.cuota_peticiones_hora) return `cuota de ${prov.cuota_peticiones_hora} peticiones/hora agotada`;
  if (prov.cuota_tokens_dia && u.tokens >= prov.cuota_tokens_dia) return `cuota diaria de ${prov.cuota_tokens_dia} tokens agotada`;
  return null;
}
const jitter = (ms) => Math.round(ms * (0.8 + Math.random() * 0.4)); // ±20 %: evita que varias sesiones reintenten a la vez
const leerRetryAfter = (h) => { if (!h) return 0; const n = Number(h); if (Number.isFinite(n)) return n * 1000; const t = Date.parse(h); return Number.isFinite(t) ? Math.max(0, t - Date.now()) : 0; };
function estadisticas() {
  const latencia = {}; for (const [k, v] of lats) latencia[k] = { n: v.length, p50_ms: pct(v, 50), p95_ms: pct(v, 95) };
  const cuotas = {};
  for (const p of Object.values(proveedores)) if (p.cuota_peticiones_hora || p.cuota_tokens_dia) { const u = usoDe(p.id); cuotas[p.id] = { peticiones_hora: u.peticiones, limite_hora: p.cuota_peticiones_hora ?? null, tokens_dia: u.tokens, limite_tokens_dia: p.cuota_tokens_dia ?? null }; }
  return { ...stats, latencia, cuotas };
}
const cuenta = (k, campo) => {
  if (!stats.porDestino[k] && Object.keys(stats.porDestino).length >= 100) k = "otros";
  const d = (stats.porDestino[k] ||= { ok: 0, fallo: 0, tokensIn: 0, tokensOut: 0 });
  d[campo]++; return d;
};
const anotarError = (txt) => { stats.ultimosErrores.unshift(`${new Date().toISOString().slice(11, 19)} ${sinSecretos(txt)}`); stats.ultimosErrores.length = Math.min(stats.ultimosErrores.length, 15); };
setInterval(() => { if (activos === 0 && Date.now() - ultimoUso > IDLE_MIN * 60_000) { log(`inactivo ${IDLE_MIN} min → apagando`); process.exit(0); } }, 30_000).unref();

// ---------- ruteo ----------
function resolverCadena(modelo) {
  if (Object.hasOwn(combos, modelo)) return combos[modelo].map(parsearDestino).filter(Boolean);
  const d = parsearDestino(modelo);
  return d ? [d] : null;
}
function parsearDestino(m) {
  if (typeof m !== "string" || !m.includes("/")) return null;
  const i = m.indexOf("/");
  const pref = m.slice(0, i);
  // Sin respaldo implícito a OpenRouter: un "vendor/modelo" sin prefijo declarado NO gasta ninguna llave de pago.
  return Object.hasOwn(proveedores, pref) ? { prov: proveedores[pref], modelo: m.slice(i + 1), etiqueta: m } : null;
}
const HOP = new Set(["connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailer", "transfer-encoding", "upgrade", "host", "content-length", "x-gateway-token"]);

function recortar(body, max) {
  const t = body.tools;
  if (!Array.isArray(t) || !max || t.length <= max) return 0;
  const nativas = t.filter((x) => !String(x?.name || "").startsWith("mcp__"));
  const mcp = t.filter((x) => String(x?.name || "").startsWith("mcp__"));
  body.tools = [...nativas.slice(0, max), ...mcp.slice(0, Math.max(0, max - nativas.length))];
  return t.length - body.tools.length;
}

async function intentar(destino, body, ttfbMs, cliente) {
  const { prov, modelo } = destino;
  if (!prov.base) return { ok: false, status: 0, msg: `${prov.id}: sin URL base válida (¿falta variable de entorno o host no permitido?)` };
  if (prov.key && !prov.llave) return { ok: false, status: 401, msg: `${prov.id}: falta la llave (${prov.key})` };
  const cuerpo = structuredClone(body);
  const quitadas = recortar(cuerpo, prov.maxTools);
  const aviso = quitadas ? ` (recortó ${quitadas} herramientas MCP)` : "";
  let url, headers, payload;
  if (prov.kind === "openai") {
    payload = pedidoAOpenAI(cuerpo, { maxOut: prov.maxOut || 8192, modelo, extraToolCall: prov.extraToolCall || null });
    url = prov.base.replace(/\/$/, "") + "/chat/completions";
    headers = { "content-type": "application/json", ...(prov.llave ? { authorization: `Bearer ${prov.llave}` } : {}) };
  } else {
    delete cuerpo.context_management;
    cuerpo.model = modelo;
    cuerpo.max_tokens = Math.min(cuerpo.max_tokens ?? prov.maxOut ?? 32000, prov.maxOut ?? 64000); // tope también aquí (gasto acotado)
    payload = cuerpo;
    url = prov.base.replace(/\/$/, "") + "/v1/messages";
    headers = { "content-type": "application/json", "anthropic-version": "2023-06-01", ...(prov.auth === "x-api-key" ? { "x-api-key": prov.llave } : { authorization: `Bearer ${prov.llave}` }) };
  }
  const t0 = Date.now();
  const ctlTtfb = new AbortController();
  const stall = new AbortController();
  const reloj = setTimeout(() => ctlTtfb.abort(), ttfbMs); // tope hasta el primer byte: un modelo saturado cede su turno
  const signal = AbortSignal.any([ctlTtfb.signal, cliente.signal, stall.signal]);
  let r;
  try { r = await fetch(url, { method: "POST", headers, body: JSON.stringify(payload), signal, redirect: "error" }); } // redirect:error → la llave jamás sigue una redirección
  catch (e) {
    const msg = cliente.signal.aborted ? `${destino.etiqueta}: el cliente canceló` : ctlTtfb.signal.aborted ? `${destino.etiqueta}: sin respuesta en ${Math.round(ttfbMs / 1000)} s` : `${destino.etiqueta}: red (${e.cause?.code || e.message})`;
    return { ok: false, status: 0, msg, cancelado: cliente.signal.aborted };
  } finally { clearTimeout(reloj); }
  if (!r.ok) {
    const txt = await Promise.race([r.text().catch(() => ""), new Promise((ok) => setTimeout(() => ok(""), 5000))]); // un cuerpo de error colgado no bloquea el respaldo
    return { ok: false, status: r.status, retryAfterMs: leerRetryAfter(r.headers.get("retry-after")), msg: `${destino.etiqueta}: HTTP ${r.status} ${sinSecretos(txt)}` };
  }
  return { ok: true, aviso, ms: Date.now() - t0, escribir: (res, stream) => entregar(res, r, prov, destino.etiqueta, body.model, stream, cliente, stall) };
}

const vivo = (res) => !res.destroyed && !res.writableEnded;

async function entregar(res, r, prov, etiqueta, modeloPedido, stream, cliente, stall) {
  const d = cuenta(etiqueta, "ok");
  if (prov.kind === "anthropic") { // ya habla Anthropic: se reenvía tal cual, pero un corte NO se disfraza de final exitoso
    res.writeHead(200, { "content-type": r.headers.get("content-type") || "application/json" });
    if (!r.body) return res.end();
    const src = Readable.fromWeb(r.body);
    src.on("error", (e) => { log(`${etiqueta}: stream cortado (${e.message})`); anotarError(`${etiqueta}: stream cortado`); res.destroy(); });
    src.pipe(res);
    return;
  }
  if (!stream) {
    let j;
    try { j = await r.json(); } catch (e) { res.writeHead(502, { "content-type": "application/json" }); return res.end(JSON.stringify(errorAnthropic(502, `gateway: respuesta ilegible de ${etiqueta}`))); }
    d.tokensIn += j.usage?.prompt_tokens || 0; d.tokensOut += j.usage?.completion_tokens || 0;
    usoDe(prov.id).tokens += (j.usage?.prompt_tokens || 0) + (j.usage?.completion_tokens || 0);
    res.writeHead(200, { "content-type": "application/json" });
    return res.end(JSON.stringify(respuestaAAnthropic(j, modeloPedido)));
  }
  res.writeHead(200, { "content-type": "text/event-stream", "cache-control": "no-cache", connection: "keep-alive" });
  const t = crearTraductorStream(modeloPedido);
  let ultimo = Date.now();
  const ping = setInterval(() => { if (vivo(res)) res.write(t.ping()); }, 8000); // los modelos que razonan tardan: conexión viva
  const vigia = setInterval(() => { if (Date.now() - ultimo > IDLE_CHUNK_MS) stall.abort(); }, 5000); // upstream mudo → se corta
  let resto = "", ultimoUsage = null, falloMsg = null;
  const procesar = (linea) => {
    if (!linea.startsWith("data:")) return;
    const dato = linea.slice(5).trim();
    if (!dato || dato === "[DONE]") return;
    let c; try { c = JSON.parse(dato); } catch { return; } // línea parcial/no JSON
    if (c.usage) ultimoUsage = c.usage;
    const out = t.chunk(c);
    if (out && vivo(res)) res.write(out);
  };
  try {
    for await (const trozo of Readable.fromWeb(r.body)) {
      ultimo = Date.now();
      resto += trozo.toString("utf8");
      let i;
      while ((i = resto.indexOf("\n")) >= 0) { procesar(resto.slice(0, i).trim()); resto = resto.slice(i + 1); }
    }
    if (resto.trim()) procesar(resto.trim()); // última línea sin salto final
  } catch (e) {
    falloMsg = cliente.signal.aborted ? null : stall.signal.aborted ? `${etiqueta}: sin datos durante ${IDLE_CHUNK_MS / 1000} s` : `${etiqueta}: stream cortado (${e.message})`;
  }
  clearInterval(ping); clearInterval(vigia);
  if (ultimoUsage) { d.tokensIn += ultimoUsage.prompt_tokens || 0; d.tokensOut += ultimoUsage.completion_tokens || 0; usoDe(prov.id).tokens += (ultimoUsage.prompt_tokens || 0) + (ultimoUsage.completion_tokens || 0); }
  if (falloMsg) { log(falloMsg); anotarError(falloMsg); cuenta(etiqueta, "fallo"); if (vivo(res)) res.write(t.error(falloMsg)); }
  else if (vivo(res)) res.write(t.fin());
  if (vivo(res)) res.end();
}

async function servirNoClaude(req, res, body, cadena, cliente) {
  stats.peticiones++;
  const errores = [];
  let ultimoStatus = 502;
  for (const [n, destino] of cadena.entries()) {
    if (cliente.signal.aborted) return;
    const clave = `${destino.prov.id}|${destino.modelo}`;
    if ((enfriando.get(clave) || 0) > Date.now() && n < cadena.length - 1) { errores.push(`${destino.etiqueta}: en cooldown`); continue; }
    const motivoCuota = sinCuota(destino.prov);
    if (motivoCuota) { errores.push(`${destino.etiqueta}: ${motivoCuota}`); ultimoStatus = 429; continue; } // no cuenta como fallo ni enfría
    usoDe(destino.prov.id).peticiones++;
    const ttfbMs = (n < cadena.length - 1 ? (cfg.ttfb_s ?? 30) : (cfg.ttfb_ultimo_s ?? 120)) * 1000; // los intermedios ceden rápido
    const r = await intentar(destino, body, ttfbMs, cliente);
    if (r.ok) {
      log(`${destino.etiqueta}${r.aviso} → 200${n ? ` (respaldo #${n})` : ""}`);
      const hist = lats.get(destino.etiqueta) || []; hist.push(r.ms); if (hist.length > 200) hist.shift(); lats.set(destino.etiqueta, hist);
      if (n) stats.fallbacks++;
      return r.escribir(res, !!body.stream);
    }
    if (r.cancelado) return;
    cuenta(destino.etiqueta, "fallo");
    // Cooldown SOLO por fallos del proveedor (red, 429, 5xx). Un 400/401 es culpa de ESTA petición: no castiga a las demás.
    if (r.status === 0 || r.status === 429 || r.status >= 500) {
      // Si el proveedor dice cuánto esperar (Retry-After), se respeta; con jitter para no reintentar todos a la vez.
      const base = r.status === 429 && r.retryAfterMs ? Math.min(Math.max(r.retryAfterMs, 1000), 600_000) : COOLDOWN_MS;
      enfriando.set(clave, Date.now() + jitter(base));
    }
    ultimoStatus = r.status || 502;
    errores.push(r.msg); log(r.msg); anotarError(r.msg);
  }
  if (!res.headersSent) res.writeHead(ultimoStatus >= 400 ? ultimoStatus : 502, { "content-type": "application/json" });
  res.end(JSON.stringify(errorAnthropic(ultimoStatus, `gateway: ningún destino respondió → ${errores.join(" | ")}`)));
}

// ---------- servidor ----------
function panel() {
  const e = estadisticas();
  const filas = Object.entries(stats.porDestino).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${v.ok}</td><td>${v.fallo}</td><td>${v.tokensIn}</td><td>${v.tokensOut}</td><td>${e.latencia[k]?.p50_ms ?? "—"}</td><td>${e.latencia[k]?.p95_ms ?? "—"}</td></tr>`).join("");
  const cuotasHtml = Object.entries(e.cuotas).map(([k, c]) => `<li><b>${esc(k)}</b>: ${c.peticiones_hora}${c.limite_hora ? "/" + c.limite_hora : ""} peticiones esta hora · ${c.tokens_dia}${c.limite_tokens_dia ? "/" + c.limite_tokens_dia : ""} tokens hoy</li>`).join("");
  const provs = Object.values(proveedores).map((p) => `<li><b>${esc(p.id)}</b> (${esc(p.kind)}) — ${p.base ? "URL ok" : "sin URL válida"}, ${p.key ? (p.llave ? "llave cargada" : "SIN llave") : "sin llave requerida"}</li>`).join("");
  return `<!doctype html><meta charset=utf-8><title>Gateway de modelos</title><body style="font:15px system-ui;max-width:800px;margin:2rem auto;padding:0 1rem">
<h1>Gateway de modelos</h1><p>Peticiones Claude (pasan intactas): <b>${stats.claude}</b> · no-Claude: <b>${stats.peticiones}</b> · respaldos usados: <b>${stats.fallbacks}</b> · rechazadas por seguridad: <b>${stats.rechazadas}</b> · desde ${esc(stats.inicio)}</p>
<h2>Proveedores</h2><ul>${provs}</ul><h2>Por destino</h2>
<table border=1 cellpadding=6 style="border-collapse:collapse"><tr><th>destino</th><th>ok</th><th>fallo</th><th>tokens in</th><th>tokens out</th><th>p50 ms</th><th>p95 ms</th></tr>${filas || "<tr><td colspan=7>sin tráfico aún</td></tr>"}</table>
<h2>Cuotas</h2><ul>${cuotasHtml || "<li>ninguna configurada</li>"}</ul>
<h2>Últimos errores</h2><pre>${esc(stats.ultimosErrores.join("\n") || "ninguno")}</pre>`;
}

const HOSTS_PERMITIDOS = new Set([`127.0.0.1:${PORT}`, `localhost:${PORT}`]);
function rechazar(res, codigo, msg) { stats.rechazadas++; res.writeHead(codigo, { "content-type": "text/plain" }); res.end(msg); }
const conToken = (req, url) => { const t = req.headers["x-gateway-token"] || url.searchParams.get("t") || ""; return crypto.timingSafeEqual(hashT(t), hashT(TOKEN)); };

const server = http.createServer((req, res) => {
  // Anti CSRF / DNS-rebinding: Claude Code (Node) no manda Origin ni Sec-Fetch-*; un navegador sí.
  if (!HOSTS_PERMITIDOS.has(String(req.headers.host || "").toLowerCase())) return rechazar(res, 421, "host no permitido");
  if (req.headers.origin || (req.headers["sec-fetch-site"] && req.headers["sec-fetch-site"] !== "none")) return rechazar(res, 403, "origen no permitido");
  if (!String(req.url || "").startsWith("/")) return rechazar(res, 400, "ruta inválida");
  const url = new URL(req.url, `http://127.0.0.1:${PORT}`);

  if (url.pathname === "/__proxy_health") { // el lanzador comprueba que quien responde es ESTE proxy (conoce el token)
    const n = url.searchParams.get("n") || "";
    res.writeHead(200, { "content-type": "application/json" });
    return res.end(JSON.stringify({ ok: true, proof: n ? crypto.createHmac("sha256", TOKEN).update(n).digest("hex") : undefined }));
  }
  if (url.pathname === "/__stats" || url.pathname === "/__panel") {
    if (!conToken(req, url)) return rechazar(res, 401, "token requerido");
    ultimoUso = Date.now();
    const cab = { "x-content-type-options": "nosniff", "content-security-policy": "default-src 'none'; style-src 'unsafe-inline'" };
    if (url.pathname === "/__stats") { res.writeHead(200, { ...cab, "content-type": "application/json" }); return res.end(JSON.stringify(estadisticas(), null, 1)); }
    res.writeHead(200, { ...cab, "content-type": "text/html; charset=utf-8" }); return res.end(panel());
  }

  ultimoUso = Date.now();
  activos++;
  let contado = true;
  const fin = () => { if (contado) { contado = false; activos--; } };
  res.on("close", fin);
  const cliente = new AbortController();
  res.on("close", () => { if (!res.writableFinished) cliente.abort(); }); // el cliente se fue (Esc): se cancela todo lo de arriba

  const chunks = []; let tam = 0;
  req.on("data", (c) => { tam += c.length; if (tam > MAX_BODY) { rechazar(res, 413, "body demasiado grande"); req.destroy(); return; } chunks.push(c); });
  req.on("error", () => res.destroy());
  req.on("end", async () => {
    try {
      const crudo = Buffer.concat(chunks);
      const ruta = url.pathname;
      const esMensajes = req.method === "POST" && /\/v1\/messages(\/count_tokens)?$/.test(ruta);
      let body = null;
      if (esMensajes && crudo.length) { try { body = JSON.parse(crudo.toString("utf8")); } catch { body = null; } }
      if (body && typeof body.model === "string" && !MODELO_VALIDO.test(body.model)) return rechazar(res, 400, "modelo inválido");
      const cadena = body ? resolverCadena(body.model) : null;

      if (body && typeof body.model === "string" && body.model.includes("/") && !cadena) {
        res.writeHead(400, { "content-type": "application/json" });
        return res.end(JSON.stringify(errorAnthropic(400, `gateway: modelo desconocido "${sinSecretos(body.model)}". Use un prefijo de proveedor declarado (${Object.keys(proveedores).join("/, ")}/) o un auto/…`)));
      }
      if (body && cadena) { // ruta que GASTA llaves: exige token de sesión
        if (!conToken(req, url)) return rechazar(res, 401, "token requerido");
        if (/count_tokens$/.test(ruta)) { // no existe fuera de Anthropic: estimación (≈4 caracteres/token)
          res.writeHead(200, { "content-type": "application/json" });
          return res.end(JSON.stringify({ input_tokens: Math.ceil(JSON.stringify({ s: body.system, m: body.messages, t: body.tools }).length / 4) }));
        }
        return await servirNoClaude(req, res, body, cadena, cliente);
      }
      // Claude y todo lo demás (login, telemetría, listados…): pasa intacto a Anthropic con SUS credenciales.
      stats.claude += body ? 1 : 0;
      // Diagnóstico: cuántas herramientas viajan en la petición de Claude (¿tool search activo? ¿diferidas?).
      if (body && Array.isArray(body.tools)) stats.ultimaPeticionClaude = { modelo: sinSecretos(body.model), herramientas: body.tools.length, diferidas: body.tools.filter((t) => t && t.defer_loading).length, mcp: body.tools.filter((t) => String(t?.name || "").startsWith("mcp__")).length, con_tool_search: body.tools.some((t) => /tool_search/i.test(String(t?.type || t?.name || ""))) };
      const headers = {};
      for (const [k, v] of Object.entries(req.headers)) if (!HOP.has(k)) headers[k] = v;
      const destino = new URL(ANTHROPIC.origin + req.url);
      const lib = destino.protocol === "http:" ? http : https;
      // Errores de CONEXIÓN (antes de que Anthropic reciba nada): se reintenta, es seguro porque la petición nunca salió.
      // Una red que intercepta TLS a ratos (cert de otro host) falla así de forma intermitente.
      const ERR_CONEXION = new Set(["ERR_TLS_CERT_ALTNAME_INVALID", "ECONNRESET", "ECONNREFUSED", "ETIMEDOUT", "ENOTFOUND", "EAI_AGAIN", "EPIPE", "UNABLE_TO_VERIFY_LEAF_SIGNATURE", "SELF_SIGNED_CERT_IN_CHAIN", "CERT_HAS_EXPIRED"]);
      let actual = null;
      res.on("close", () => { if (!res.writableFinished && actual) actual.destroy(); }); // cliente cancelado → se corta también hacia Anthropic
      const enviar = (intento) => {
        let respondio = false;
        const up = lib.request({ hostname: destino.hostname, port: destino.port || (destino.protocol === "http:" ? 80 : 443), method: req.method, path: destino.pathname + destino.search, headers: { ...headers, host: destino.host, ...(crudo.length ? { "content-length": crudo.length } : {}) } }, (r) => {
          respondio = true;
          const salida = {}; for (const [k, v] of Object.entries(r.headers)) if (!HOP.has(k)) salida[k] = v;
          res.writeHead(r.statusCode || 502, salida);
          r.on("error", () => res.destroy());
          r.on("aborted", () => res.destroy());
          r.pipe(res);
          if (body) r.on("end", () => log(`anthropic ${sinSecretos(body.model)} → ${r.statusCode}`));
        });
        actual = up;
        up.on("error", (e) => {
          log(`anthropic: ${e.code || e.message}${intento ? ` (intento ${intento + 1})` : ""}`);
          if (res.destroyed || res.writableEnded) return;
          if (!respondio && !res.headersSent && ERR_CONEXION.has(e.code) && intento < 3) { setTimeout(() => enviar(intento + 1), 400 * (intento + 1)); return; }
          if (!res.headersSent) {
            const certRaro = /CERT|TLS/.test(e.code || "");
            const msg = certRaro ? `gateway: la red devolvió un certificado TLS que no corresponde a Anthropic (${e.code}) tras ${intento + 1} intentos. Es la red (¿INACAP/proxy corporativo?), no su sesión: reintente o cambie de red.` : `gateway: no llegué a Anthropic (${e.code || e.message}) tras ${intento + 1} intentos`;
            res.writeHead(502, { "content-type": "application/json" }); res.end(JSON.stringify(errorAnthropic(502, msg)));
          } else res.destroy(); // ya había empezado a responder: no se mezcla JSON dentro de un SSE
        });
        up.end(crudo.length ? crudo : undefined);
      };
      enviar(0);
    } catch (e) {
      log("error interno:", e.message);
      if (!res.headersSent) { res.writeHead(500, { "content-type": "application/json" }); res.end(JSON.stringify(errorAnthropic(500, "gateway: error interno"))); }
      else res.destroy();
    }
  });
});

server.listen(PORT, "127.0.0.1", () => log(`escuchando en 127.0.0.1:${PORT} · proveedores=${Object.keys(proveedores).join(",")} · combos=${Object.keys(combos).join(",")} · idle=${IDLE_MIN}min`));
server.on("error", (e) => { log("no pude escuchar:", e.code || e.message); process.exit(1); });
