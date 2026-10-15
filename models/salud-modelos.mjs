#!/usr/bin/env node
// SALUD DE MODELOS — prueba de punta a punta cada fila del selector /model a través del gateway REAL.
// Por modelo, dos pasos (cada uno con un código ÚNICO, sin archivos compartidos → sin contaminación):
//   1. conversación simple: ¿responde?  2. herramientas: ¿emite tool_use y usa el tool_result? (Claude Code vive de esto)
// Uso:  node salud-modelos.mjs                 todos los modelos no-Claude del selector
//       node salud-modelos.mjs --modelos a,b   solo esos
//       node salud-modelos.mjs --json          salida JSON      --escribir   guarda estado en profiles/salud-modelos.json
// Requiere el gateway vivo (lo levanta `claude-multi`); lee el token de %LOCALAPPDATA%\claude-gateway\token.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import crypto from "node:crypto";

const args = process.argv.slice(2);
const opt = (n, d) => { const i = args.indexOf("--" + n); return i >= 0 && args[i + 1] && !args[i + 1].startsWith("--") ? args[i + 1] : d; };
const PUERTO = process.env.MODELO_PROXY_PORT || 8787;
const BASE = `http://127.0.0.1:${PUERTO}`;
const token = fs.readFileSync(path.join(process.env.LOCALAPPDATA || "", "claude-gateway", "token"), "utf8").trim();
const perfil = JSON.parse(fs.readFileSync(path.join(os.homedir(), ".claude", "profiles", "multi.settings.json"), "utf8"));
const TIMEOUT_MS = Number(opt("timeout", 90)) * 1000;

const lista = opt("modelos", "") ? opt("modelos").split(",").map((s) => s.trim())
  : perfil.modelPicker.options.map((o) => o.model).filter((m) => m.includes("/"));

async function llamar(model, messages, tools) {
  const t0 = Date.now();
  try {
    const r = await fetch(BASE + "/v1/messages", {
      method: "POST", headers: { "content-type": "application/json", "x-gateway-token": token, "anthropic-version": "2023-06-01" },
      body: JSON.stringify({ model, max_tokens: 1500, messages, ...(tools ? { tools } : {}) }), signal: AbortSignal.timeout(TIMEOUT_MS),
    });
    const texto = await r.text();
    let j = null; try { j = JSON.parse(texto); } catch { /* no JSON */ }
    return { status: r.status, j, texto, ms: Date.now() - t0 };
  } catch (e) { return { status: 0, j: null, texto: String(e.message || e), ms: Date.now() - t0 }; }
}
const textoDe = (j) => (j?.content || []).filter((b) => b.type === "text").map((b) => b.text).join(" ");

async function probar(model) {
  const clave = "OK-" + crypto.randomBytes(3).toString("hex");
  const a = await llamar(model, [{ role: "user", content: `Responde exactamente con esta palabra y nada más: ${clave}` }]);
  const conversa = a.status === 200 && textoDe(a.j).includes(clave);
  const res = { modelo: model, conversa, ms_conversa: a.ms, herramientas: false, ms_herramientas: null, error: null };
  if (!conversa) { res.error = a.status === 200 ? "respuesta sin la palabra pedida" : `HTTP ${a.status}: ${a.texto.slice(0, 160)}`; return res; }
  const codigo = "PIPELINE-" + crypto.randomInt(1000, 9999);
  const tools = [{ name: "leer_archivo", description: "Lee un archivo del disco y devuelve su contenido.", input_schema: { type: "object", properties: { ruta: { type: "string" } }, required: ["ruta"] } }];
  const m1 = [{ role: "user", content: "Usa la herramienta leer_archivo para leer secreto.txt y dime el código que contiene." }];
  const b = await llamar(model, m1, tools);
  const uso = (b.j?.content || []).find((x) => x.type === "tool_use");
  res.ms_herramientas = b.ms;
  if (!uso) { res.error = b.status === 200 ? "no emitió tool_use" : `HTTP ${b.status}: ${b.texto.slice(0, 160)}`; return res; }
  const m2 = [...m1, { role: "assistant", content: b.j.content }, { role: "user", content: [{ type: "tool_result", tool_use_id: uso.id, content: `El código es ${codigo}` }] }];
  const c = await llamar(model, m2, tools);
  res.ms_herramientas = b.ms + c.ms;
  res.herramientas = c.status === 200 && textoDe(c.j).includes(codigo);
  if (!res.herramientas) res.error = c.status === 200 ? "no usó el tool_result (no devolvió el código)" : `HTTP ${c.status}: ${c.texto.slice(0, 160)}`;
  return res;
}

const resultados = [];
for (const m of lista) { // de uno en uno: no saturar cuotas ni ensuciar la medición
  const r = await probar(m); resultados.push(r);
  if (!args.includes("--json")) console.log(`${r.herramientas ? "OK   " : r.conversa ? "PARCIAL" : "FALLA"} ${m.padEnd(52)} conversa ${r.conversa ? "sí" : "no"} (${(r.ms_conversa / 1000).toFixed(1)} s) · herramientas ${r.herramientas ? "sí" : "no"}${r.ms_herramientas ? ` (${(r.ms_herramientas / 1000).toFixed(1)} s)` : ""}${r.error ? "  ← " + r.error.replace(/\s+/g, " ").slice(0, 110) : ""}`);
}
if (args.includes("--json")) console.log(JSON.stringify(resultados, null, 1));
if (args.includes("--escribir")) fs.writeFileSync(path.join(os.homedir(), ".claude", "profiles", "salud-modelos.json"), JSON.stringify({ fecha: new Date().toISOString(), resultados }, null, 1));
const ok = resultados.filter((r) => r.herramientas).length;
if (!args.includes("--json")) console.log(`\n${ok} de ${resultados.length} funcionan completos (conversación + herramientas).`);
