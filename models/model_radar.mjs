#!/usr/bin/env node
// RADAR DE MODELOS — "nunca quedarse con lo que tenemos".
// Consulta EN VIVO los catálogos de los proveedores que usa el gateway (NVIDIA NIM, Kilo, OpenRouter, Gemini),
// guarda una instantánea fechada y la compara con la anterior: qué modelos son NUEVOS, cuáles desaparecieron,
// cuáles cambiaron de gratis a pago y cuáles EXPIRAN pronto (como Space Bunny Alpha). También lista los recientes
// por fecha de creación y propone candidatos para probar con el banco de código.
//
//   node model_radar.mjs                  informe (guarda instantánea y compara con la anterior)
//   node model_radar.mjs --dias 30        ventana de "recientes" (por defecto 45)
//   node model_radar.mjs --sin-guardar    solo mira, no escribe instantánea
//   node model_radar.mjs --json           salida JSON (para otras herramientas)
//
// Las llaves (NVIDIA, Gemini) salen del entorno o de ~/.claude/.env (o JARVIS_ENV_FILE); no se imprimen ni se guardan.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const DIR = process.env.RADAR_DIR || path.join(os.homedir(), ".claude", "metrics", "radar");
const ENV_LOCAL = process.env.JARVIS_ENV_FILE || path.join(os.homedir(), ".claude", ".env");
const args = process.argv.slice(2);
const opt = (n, d) => { const i = args.indexOf("--" + n); return i >= 0 && args[i + 1] && !args[i + 1].startsWith("--") ? args[i + 1] : d; };
const flag = (n) => args.includes("--" + n);

function leerEnv(nombre) {
  if (process.env[nombre]) return process.env[nombre];
  try { const l = fs.readFileSync(ENV_LOCAL, "utf8").split(/\r?\n/).find((x) => new RegExp(`^\\s*${nombre}\\s*=`).test(x)); return l ? l.split("=").slice(1).join("=").trim().replace(/^["']|["']$/g, "") : ""; } catch { return ""; }
}
const getJson = async (url, headers = {}) => { const r = await fetch(url, { headers, signal: AbortSignal.timeout(25000) }); if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); };
const ahora = Date.now();
const gratis = (p) => !!p && Number(p.prompt) === 0 && Number(p.completion) === 0;

// Cada fuente devuelve [{fuente,id,creado,ctx,tools,gratis,expira}]
const FUENTES = {
  async openrouter() {
    const j = await getJson("https://openrouter.ai/api/v1/models");
    return j.data.map((m) => ({ fuente: "openrouter", id: m.id, creado: m.created ? m.created * 1000 : null, ctx: m.context_length ?? null, tools: (m.supported_parameters || []).includes("tools"), gratis: gratis(m.pricing), expira: m.expiration_date || null }));
  },
  async kilo() {
    const j = await getJson("https://api.kilo.ai/api/gateway/models");
    return j.data.map((m) => ({ fuente: "kilo", id: m.id, creado: m.created ? m.created * 1000 : null, ctx: m.context_length ?? null, tools: (m.supported_parameters || m.features || []).toString().includes("tool"), gratis: /:free$/.test(m.id) || gratis(m.pricing), expira: m.expiration_date || null }));
  },
  async nim() {
    const base = leerEnv("NVIDIA_BASE_URL"), key = leerEnv("NVIDIA_API_KEY");
    if (!base || !key) throw new Error("sin NVIDIA_BASE_URL/NVIDIA_API_KEY");
    const j = await getJson(base.replace(/\/$/, "") + "/models", { authorization: "Bearer " + key });
    return j.data.map((m) => ({ fuente: "nim", id: m.id, creado: m.created ? m.created * 1000 : null, ctx: null, tools: null, gratis: true, expira: null }));
  },
  async gemini() {
    const key = leerEnv("GEMINI_API_KEY");
    if (!key) throw new Error("sin GEMINI_API_KEY");
    const j = await getJson("https://generativelanguage.googleapis.com/v1beta/openai/models", { authorization: "Bearer " + key });
    return j.data.map((m) => ({ fuente: "gemini", id: m.id.replace(/^models\//, ""), creado: null, ctx: null, tools: null, gratis: null, expira: null }));
  },
};

const clave = (m) => `${m.fuente}|${m.id}`;
const NO_CHAT = /embed|tts|image|imagen|veo|lyria|riva|guard|safety|reward|rerank|parse|clip|vila|neva|whisper|transcribe|audio|live|robotics|deplot|kosmos|fuyu|vision-embed/i;
const PISTA_CODIGO = /code|coder|codestral|devstral|laguna|north|kimi|glm|deepseek|qwen|nemotron|gpt-oss|step|minimax|ling|gemini|gemma|llama|mistral/i;

export function diferencias(prev, actual, { expiraEnDias = 14 } = {}) {
  const pm = new Map(prev.map((m) => [clave(m), m])), am = new Map(actual.map((m) => [clave(m), m]));
  const nuevos = actual.filter((m) => !pm.has(clave(m)));
  const desaparecidos = prev.filter((m) => !am.has(clave(m)));
  const dejaronDeSerGratis = actual.filter((m) => pm.has(clave(m)) && pm.get(clave(m)).gratis === true && m.gratis === false);
  const expiran = actual.filter((m) => m.expira && new Date(m.expira).getTime() - ahora < expiraEnDias * 864e5 && new Date(m.expira).getTime() > ahora - 864e5);
  return { nuevos, desaparecidos, dejaronDeSerGratis, expiran };
}

export function candidatos(modelos, dias) {
  return modelos
    .filter((m) => m.creado && ahora - m.creado < dias * 864e5 && !NO_CHAT.test(m.id) && m.tools !== false && (m.ctx == null || m.ctx >= 100_000))
    .map((m) => ({ ...m, puntos: (m.gratis ? 3 : 0) + (PISTA_CODIGO.test(m.id) ? 2 : 0) + (m.tools ? 1 : 0) + ((m.ctx ?? 0) >= 500_000 ? 1 : 0) - (m.expira ? 3 : 0) }))
    .sort((a, b) => b.puntos - a.puntos || b.creado - a.creado);
}

async function main() {
  const dias = Number(opt("dias", 45));
  const resultados = {}, errores = {};
  await Promise.all(Object.entries(FUENTES).map(async ([k, f]) => { try { resultados[k] = await f(); } catch (e) { errores[k] = e.message; } }));
  const actual = Object.values(resultados).flat();
  fs.mkdirSync(DIR, { recursive: true });
  const latest = path.join(DIR, "latest.json");
  let prev = null; try { prev = JSON.parse(fs.readFileSync(latest, "utf8")); } catch { /* primera vez */ }
  const dif = prev ? diferencias(prev.modelos.filter((m) => resultados[m.fuente]), actual) : null; // solo compara fuentes que respondieron hoy
  const recientes = candidatos(actual, dias);
  const informe = { fecha: new Date().toISOString(), conteo: Object.fromEntries(Object.entries(resultados).map(([k, v]) => [k, v.length])), errores, primeraVez: !prev, desde: prev?.fecha ?? null, dif, expiran: diferencias([], actual).expiran, recientes: recientes.slice(0, 25) };
  if (!flag("sin-guardar")) {
    const hoy = new Date().toISOString().slice(0, 10);
    fs.writeFileSync(path.join(DIR, `snapshot-${hoy}.json`), JSON.stringify({ fecha: informe.fecha, modelos: actual }));
    fs.writeFileSync(latest, JSON.stringify({ fecha: informe.fecha, modelos: actual }));
  }
  if (flag("json")) return console.log(JSON.stringify(informe, null, 1));

  console.log(`=== RADAR DE MODELOS · ${informe.fecha.slice(0, 16).replace("T", " ")} UTC ===`);
  console.log("catálogos:", Object.entries(informe.conteo).map(([k, v]) => `${k} ${v}`).join(" · "), Object.keys(errores).length ? ` | FALLÓ: ${Object.entries(errores).map(([k, v]) => `${k} (${v})`).join(", ")}` : "");
  if (informe.primeraVez) console.log("(primera instantánea: guardada como línea base; la próxima vez habrá diferencias)");
  else {
    console.log(`\n── Cambios desde ${informe.desde.slice(0, 16).replace("T", " ")} ──`);
    console.log(`nuevos: ${dif.nuevos.length} | desaparecidos: ${dif.desaparecidos.length} | dejaron de ser gratis: ${dif.dejaronDeSerGratis.length}`);
    for (const m of dif.nuevos.filter((x) => !NO_CHAT.test(x.id)).slice(0, 30)) console.log(`  + ${m.fuente.padEnd(10)} ${m.id}${m.gratis ? "  [gratis]" : ""}${m.ctx ? "  ctx " + m.ctx : ""}`);
    for (const m of dif.desaparecidos.slice(0, 15)) console.log(`  - ${m.fuente.padEnd(10)} ${m.id}`);
    for (const m of dif.dejaronDeSerGratis) console.log(`  $ ${m.fuente.padEnd(10)} ${m.id} ya NO es gratis`);
  }
  if (informe.expiran.length) { console.log("\n── EXPIRAN pronto ──"); for (const m of informe.expiran) console.log(`  ! ${m.fuente.padEnd(10)} ${m.id} → ${m.expira}`); }
  console.log(`\n── Candidatos recientes (últimos ${dias} días, con herramientas, ctx ≥100k; gratis y con pinta de código primero) ──`);
  for (const m of informe.recientes) console.log(`  ${new Date(m.creado).toISOString().slice(0, 10)}  ${m.fuente.padEnd(10)} ${m.id.padEnd(54)} ${m.gratis ? "GRATIS " : "pago   "} ctx ${String(m.ctx ?? "?").padStart(8)}${m.expira ? "  (expira " + m.expira + ")" : ""}`);
  console.log("\nSiguiente paso: probar los candidatos con el banco de código y agregarlos a gateway.json solo si pasan.");
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) main().catch((e) => { console.error("radar:", e.message); process.exit(1); });
