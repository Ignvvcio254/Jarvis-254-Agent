// Prueba de integración del gateway: levanta un upstream FALSO que simula fallas y el proxy REAL apuntándole.
// Cubre los hallazgos del code-reviewer y del security-reviewer del 2026-10-03.
import test, { before, after } from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const aqui = path.dirname(fileURLToPath(import.meta.url));
const TOKEN = "token-de-prueba";
const hits = {}; const visto = { authAnthropic: null, tokenReenviado: null, colgadoCerrado: false };
let fake, proxy, PORT, FAKE;

const sse = (res, objs, fin = true) => { for (const o of objs) res.write(`data: ${JSON.stringify(o)}\n\n`); if (fin) res.write("data: [DONE]\n\n"); };
const contenido = (t) => ({ choices: [{ delta: { content: t } }] });

function crearFake() {
  return http.createServer((req, res) => {
    const partes = []; req.on("data", (c) => partes.push(c));
    req.on("end", () => {
      let b = {}; try { b = JSON.parse(Buffer.concat(partes).toString() || "{}"); } catch {}
      if (req.url === "/v1/messages") { // Anthropic falso (passthrough)
        visto.authAnthropic = req.headers.authorization || null; visto.tokenReenviado = req.headers["x-gateway-token"] || null;
        res.writeHead(200, { "content-type": "application/json" });
        return res.end(JSON.stringify({ type: "message", role: "assistant", content: [{ type: "text", text: "pasa-intacto" }], stop_reason: "end_turn", usage: { input_tokens: 1, output_tokens: 1 } }));
      }
      hits[b.model] = (hits[b.model] || 0) + 1;
      switch (b.model) {
        case "ok": res.writeHead(200, { "content-type": "text/event-stream" }); return sse(res, [contenido("hola"), contenido(" mundo"), { choices: [{ delta: {}, finish_reason: "stop" }] }, { choices: [], usage: { prompt_tokens: 11, completion_tokens: 3 } }]) || res.end();
        case "corte": res.writeHead(200, { "content-type": "text/event-stream" }); sse(res, [contenido("a medias")], false); return setTimeout(() => res.destroy(), 50);
        case "error200": res.writeHead(200, { "content-type": "text/event-stream" }); sse(res, [{ error: { message: "boom-upstream" } }]); return res.end();
        case "ok2": res.writeHead(200, { "content-type": "text/event-stream" }); return sse(res, [contenido("respaldo-cuota"), { choices: [{ delta: {}, finish_reason: "stop" }] }]) || res.end();
        case "ra429": res.writeHead(429, { "content-type": "application/json", "retry-after": "1" }); return res.end(JSON.stringify({ error: "limite" }));
        case "lento": return; // nunca responde
        case "400": res.writeHead(400, { "content-type": "application/json" }); return res.end(JSON.stringify({ error: "malo" }));
        case "xss400": res.writeHead(400, { "content-type": "text/plain" }); return res.end("<script>alert(1)</script>");
        case "colgado": res.writeHead(200, { "content-type": "text/event-stream" }); sse(res, [contenido("empiezo")], false); res.on("close", () => { visto.colgadoCerrado = true; }); return;
        case "length_tool": res.writeHead(200, { "content-type": "text/event-stream" }); return sse(res, [{ choices: [{ delta: { tool_calls: [{ index: 0, id: "t1", function: { name: "Read", arguments: "{\"p\":" } }] } }] }, { choices: [{ delta: {}, finish_reason: "length" }] }]) || res.end();
        default: res.writeHead(404); return res.end("no");
      }
    });
  });
}

const peticion = (opts, cuerpo) => new Promise((resolve, reject) => {
  const r = http.request({ host: "127.0.0.1", port: PORT, ...opts }, (res) => { let t = ""; res.on("data", (c) => (t += c)); res.on("end", () => resolve({ status: res.statusCode, texto: t })); });
  r.on("error", reject); r.end(cuerpo);
});
const mensajes = (model, headers = {}, extra = {}) => peticion({ path: "/v1/messages", method: "POST", headers: { "content-type": "application/json", host: `127.0.0.1:${PORT}`, "x-gateway-token": TOKEN, ...headers } },
  JSON.stringify({ model, max_tokens: 50, stream: true, messages: [{ role: "user", content: "hola" }], ...extra }));
const get = (p, headers = {}) => peticion({ path: p, method: "GET", headers: { host: `127.0.0.1:${PORT}`, ...headers } });
const stats = async () => JSON.parse((await get("/__stats", { "x-gateway-token": TOKEN })).texto);

before(async () => {
  fake = crearFake(); await new Promise((r) => fake.listen(0, "127.0.0.1", r)); FAKE = fake.address().port;
  PORT = 20000 + Math.floor(Math.random() * 20000);
  const cfgPath = path.join(os.tmpdir(), `gw-test-${PORT}.json`);
  fs.writeFileSync(cfgPath, JSON.stringify({ providers: { fake: { kind: "openai", base: `http://127.0.0.1:${FAKE}`, key: null, maxOut: 1000, maxTools: 128 },
      fakeq: { kind: "openai", base: `http://127.0.0.1:${FAKE}`, key: null, maxOut: 1000, maxTools: 128, cuota_peticiones_hora: 2 } },
    combos: { "auto/lento": ["fake/lento", "fake/ok"], "auto/400": ["fake/400", "fake/ok"], "auto/q": ["fakeq/ok", "fake/ok2"], "auto/ra": ["fake/ra429", "fake/ok"] }, ttfb_s: 1, ttfb_ultimo_s: 5, cooldown_s: 60 }));
  proxy = spawn(process.execPath, [path.join(aqui, process.env.PROXY_FILE || "modelo-proxy.mjs")], { env: { PATH: process.env.PATH, SystemRoot: process.env.SystemRoot, USERPROFILE: process.env.USERPROFILE,
    MODELO_PROXY_PORT: String(PORT), MODELO_PROXY_CONFIG: cfgPath, MODELO_PROXY_TOKEN: TOKEN, MODELO_PROXY_ANTHROPIC: `http://127.0.0.1:${FAKE}`, MODELO_PROXY_IDLE_MIN: "5" }, stdio: ["ignore", "ignore", "ignore"] });
  for (let i = 0; i < 40; i++) { try { if ((await get("/__proxy_health")).status === 200) return; } catch {} await new Promise((r) => setTimeout(r, 150)); }
  throw new Error("el proxy no arrancó");
});
after(() => { proxy?.kill(); fake?.close(); fake?.closeAllConnections?.(); });

test("stream normal: traduce a eventos Anthropic con usage de entrada", async () => {
  const r = await mensajes("fake/ok");
  assert.equal(r.status, 200);
  assert.ok(r.texto.includes("hola") && r.texto.includes(" mundo") && r.texto.includes("message_stop"));
  assert.ok(r.texto.includes('"input_tokens":11'));
});

test("corte a mitad de stream → evento error, NO un final exitoso", async () => {
  const r = await mensajes("fake/corte");
  assert.ok(r.texto.includes("event: error"), "debe avisar el corte");
  assert.ok(!r.texto.includes("message_stop"), "no debe simular éxito");
});

test("error dentro de un 200 → evento error con el mensaje", async () => {
  const r = await mensajes("fake/error200");
  assert.ok(r.texto.includes("event: error") && r.texto.includes("boom-upstream"));
  assert.ok(!r.texto.includes("message_stop"));
});

test("max_tokens por límite declara max_tokens, no tool_use", async () => {
  const r = await mensajes("fake/length_tool");
  assert.ok(r.texto.includes('"stop_reason":"max_tokens"'), r.texto.slice(-300));
});

test("modelo lento cede al siguiente de la cadena (ttfb) y cuenta un respaldo", async () => {
  const t0 = Date.now();
  const r = await mensajes("auto/lento");
  assert.ok(r.texto.includes("hola"), "debe responder el respaldo");
  assert.ok(Date.now() - t0 < 4000, "no debe esperar más que el ttfb + respaldo");
  assert.ok((await stats()).fallbacks >= 1);
});

test("un 400 NO castiga con cooldown: la 2ª petición vuelve a intentar el mismo modelo", async () => {
  hits["400"] = 0;
  await mensajes("auto/400"); await mensajes("auto/400");
  assert.equal(hits["400"], 2, "el 400 debe reintentarse (no hay cooldown por error de la petición)");
});

test("seguridad: Host ajeno → 421; Origin/Sec-Fetch-Site → 403; sin token → 401", async () => {
  assert.equal((await mensajes("fake/ok", { host: "evil.test" })).status, 421);
  assert.equal((await mensajes("fake/ok", { origin: "http://evil.test" })).status, 403);
  assert.equal((await mensajes("fake/ok", { "sec-fetch-site": "cross-site" })).status, 403);
  assert.equal((await mensajes("fake/ok", { "x-gateway-token": "otro" })).status, 401);
  assert.equal((await get("/__stats")).status, 401);
  assert.equal((await get("/__panel")).status, 401);
  assert.equal((await get("/__stats", { "x-gateway-token": TOKEN })).status, 200);
});

test("Claude pasa SIN token, con su Authorization intacto, y el token del gateway no se reenvía", async () => {
  const r = await mensajes("sonnet", { authorization: "Bearer oauth-del-usuario", "x-gateway-token": TOKEN });
  assert.ok(r.texto.includes("pasa-intacto"));
  assert.equal(visto.authAnthropic, "Bearer oauth-del-usuario");
  assert.equal(visto.tokenReenviado, null, "el token del gateway NO debe llegar a Anthropic");
  const sinToken = await mensajes("sonnet", { authorization: "Bearer x", "x-gateway-token": "" });
  assert.ok(sinToken.texto.includes("pasa-intacto"), "Claude no necesita el token");
});

test("nombres hostiles no tumban el proxy ni gastan llaves: constructor/__proto__/toString, prefijo desconocido, modelo inválido", async () => {
  for (const m of ["constructor", "__proto__", "toString", "hasOwnProperty"]) { const r = await mensajes(m); assert.ok(r.status < 500, `${m} → ${r.status}`); }
  const desconocido = await mensajes("zzz/modelo");
  assert.equal(desconocido.status, 400); assert.ok(desconocido.texto.includes("modelo desconocido"));
  assert.equal((await mensajes("or/<img src=x>")).status, 400);
  assert.equal((await get("/__proxy_health")).status, 200, "el proxy sigue vivo");
});

test("el panel escapa el HTML que viene del upstream (sin XSS)", async () => {
  await mensajes("fake/xss400");
  const panel = (await get("/__panel", { "x-gateway-token": TOKEN })).texto;
  assert.ok(!panel.includes("<script>alert"), "no debe haber HTML sin escapar");
  assert.ok(panel.includes("&lt;script&gt;"));
});

test("si el cliente cancela, se corta también la conexión hacia el upstream", async () => {
  visto.colgadoCerrado = false;
  await new Promise((resolve) => {
    const req = http.request({ host: "127.0.0.1", port: PORT, path: "/v1/messages", method: "POST", headers: { "content-type": "application/json", host: `127.0.0.1:${PORT}`, "x-gateway-token": TOKEN } }, (res) => { res.once("data", () => { req.destroy(); resolve(); }); });
    req.on("error", () => {}); req.end(JSON.stringify({ model: "fake/colgado", max_tokens: 5, stream: true, messages: [{ role: "user", content: "x" }] }));
  });
  for (let i = 0; i < 30 && !visto.colgadoCerrado; i++) await new Promise((r) => setTimeout(r, 100));
  assert.ok(visto.colgadoCerrado, "el upstream debe ver la conexión cerrada");
});

test("la ruta health prueba que es ESTE proxy (HMAC del nonce con el token)", async () => {
  const { createHmac } = await import("node:crypto");
  const j = JSON.parse((await get("/__proxy_health?n=abc123")).texto);
  assert.equal(j.proof, createHmac("sha256", TOKEN).update("abc123").digest("hex"));
});

test("cuota por hora: tras agotarla el proveedor se salta ANTES de recibir un 429 y responde el respaldo", async () => {
  const a = await mensajes("auto/q"), b = await mensajes("auto/q"), c = await mensajes("auto/q");
  assert.ok(a.texto.includes("hola") && b.texto.includes("hola"), "las dos primeras las atiende el proveedor con cuota");
  assert.ok(c.texto.includes("respaldo-cuota"), "la 3ª debe ir directo al respaldo");
  const st = await stats();
  assert.equal(st.cuotas.fakeq.peticiones_hora, 2, "la petición saltada no cuenta como uso");
  assert.equal(st.cuotas.fakeq.limite_hora, 2);
});

test("Retry-After: el cooldown sigue lo que dice el proveedor (1 s), no los 60 s fijos", async () => {
  hits.ra429 = 0;
  await mensajes("auto/ra");                       // 429 con retry-after:1 → cae al respaldo y queda en cooldown ~1 s
  assert.equal(hits.ra429, 1);
  await mensajes("auto/ra");                       // inmediatamente: debe saltarse ra429 (en cooldown)
  assert.equal(hits.ra429, 1, "durante el cooldown no se vuelve a llamar");
  await new Promise((r) => setTimeout(r, 1500));   // pasa el Retry-After (+jitter máx 1,2 s)
  await mensajes("auto/ra");
  assert.equal(hits.ra429, 2, "pasado el Retry-After vuelve a intentarlo (con 60 s fijos NO lo haría)");
});

test("estadísticas: latencia p50/p95 por destino", async () => {
  await mensajes("fake/ok"); await mensajes("fake/ok");
  const st = await stats();
  const l = st.latencia["fake/ok"];
  assert.ok(l && l.n >= 2 && Number.isFinite(l.p50_ms) && Number.isFinite(l.p95_ms) && l.p95_ms >= l.p50_ms, JSON.stringify(l));
});

// Un proxy aparte con el "Anthropic" caído: simula la red que falla a ratos al conectar (p. ej. TLS con cert ajeno).
async function proxyConAnthropic(puertoAnthropic) {
  const puerto = 20000 + Math.floor(Math.random() * 20000);
  const cfg = path.join(os.tmpdir(), `gw-retry-${puerto}.json`);
  fs.writeFileSync(cfg, JSON.stringify({ providers: {}, combos: {} }));
  const p = spawn(process.execPath, [path.join(aqui, process.env.PROXY_FILE || "modelo-proxy.mjs")], { env: { PATH: process.env.PATH, SystemRoot: process.env.SystemRoot, USERPROFILE: process.env.USERPROFILE,
    MODELO_PROXY_PORT: String(puerto), MODELO_PROXY_CONFIG: cfg, MODELO_PROXY_TOKEN: TOKEN, MODELO_PROXY_ANTHROPIC: `http://127.0.0.1:${puertoAnthropic}`, MODELO_PROXY_IDLE_MIN: "5" }, stdio: ["ignore", "ignore", "ignore"] });
  for (let i = 0; i < 40; i++) { try { const r = await new Promise((ok, no) => { const q = http.request({ host: "127.0.0.1", port: puerto, path: "/__proxy_health", headers: { host: `127.0.0.1:${puerto}` } }, (x) => { x.resume(); ok(x.statusCode); }); q.on("error", no); q.end(); }); if (r === 200) break; } catch {} await new Promise((r) => setTimeout(r, 150)); }
  const llamar = () => new Promise((resolve, reject) => { const q = http.request({ host: "127.0.0.1", port: puerto, path: "/v1/messages", method: "POST", headers: { "content-type": "application/json", host: `127.0.0.1:${puerto}` } }, (x) => { let t = ""; x.on("data", (c) => (t += c)); x.on("end", () => resolve({ status: x.statusCode, texto: t })); }); q.on("error", reject); q.end(JSON.stringify({ model: "sonnet", max_tokens: 5, messages: [{ role: "user", content: "hola" }] })); });
  return { p, llamar };
}

test("si Anthropic no es alcanzable AL CONECTAR, se reintenta y se recupera sola cuando vuelve", async () => {
  const libre = await new Promise((r) => { const s = http.createServer(); s.listen(0, "127.0.0.1", () => { const pt = s.address().port; s.close(() => r(pt)); }); });
  const { p, llamar } = await proxyConAnthropic(libre);
  let tardio;
  try {
    const respuesta = llamar(); // sale con el puerto cerrado → ECONNREFUSED → reintenta
    await new Promise((r) => setTimeout(r, 500));
    tardio = http.createServer((req, res) => { req.resume(); res.writeHead(200, { "content-type": "application/json" }); res.end(JSON.stringify({ type: "message", content: [{ type: "text", text: "volvio" }] })); });
    await new Promise((r) => tardio.listen(libre, "127.0.0.1", r));
    const r = await respuesta;
    assert.equal(r.status, 200, r.texto);
    assert.ok(r.texto.includes("volvio"));
  } finally { p.kill(); tardio?.close(); tardio?.closeAllConnections?.(); }
});

test("si Anthropic sigue inalcanzable, el 502 dice cuántos intentos y no queda mudo", async () => {
  const libre = await new Promise((r) => { const s = http.createServer(); s.listen(0, "127.0.0.1", () => { const pt = s.address().port; s.close(() => r(pt)); }); });
  const { p, llamar } = await proxyConAnthropic(libre);
  try {
    const r = await llamar();
    assert.equal(r.status, 502);
    assert.ok(/4 intentos/.test(r.texto), r.texto);
  } finally { p.kill(); }
});
