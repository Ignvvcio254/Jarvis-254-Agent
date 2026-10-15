#!/usr/bin/env node
// JARVIS EVAL — measures the agent with objective tests of its own rules.
//
//   node jarvis-eval.mjs --selftest            checks the graders WITHOUT calling any model
//   node jarvis-eval.mjs --list                lists the tasks
//   node jarvis-eval.mjs [--model sonnet] [--only a,b] [--gateway] [--timeout 150]
//   node jarvis-eval.mjs --report              compares the last two runs and flags regressions
//
// Each task runs in its own temp directory with `claude -p` (stream-json, to see which tools were used).
// Your real hooks and CLAUDE.md load (it is YOUR harness being measured) but no MCP servers
// (empty --strict-mcp-config): saves memory and avoids external effects. --gateway uses the multi-model
// launcher, so OTHER models (nim/…, gem/…) can be compared on exactly the same tasks.
// Cost: each task is a full session; use sparingly.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { TAREAS } from "./tareas.mjs";

const aqui = path.dirname(fileURLToPath(import.meta.url));
const HIST = path.join(os.homedir(), ".claude", "metrics", "eval_history.jsonl");
const WIN = process.platform === "win32";
// The real binary, spawned WITHOUT a shell (a shell would split the prompt). CLAUDE_BIN overrides.
function resolverClaude() {
  if (process.env.CLAUDE_BIN) return process.env.CLAUDE_BIN;
  if (!WIN) return "claude";
  const candidatos = [
    path.join(os.homedir(), ".local", "bin", "claude.exe"),
    path.join(process.env.APPDATA || "", "npm", "node_modules", "@anthropic-ai", "claude-code", "bin", "claude.exe"),
  ];
  for (const dirPath of (process.env.PATH || "").split(path.delimiter)) candidatos.push(path.join(dirPath, "claude.exe"));
  return candidatos.find((c) => c && fs.existsSync(c)) || "claude.exe";
}
const CLAUDE = resolverClaude();
const MCP_VACIO = path.join(aqui, "mcp-vacio.json");
const args = process.argv.slice(2);
const opt = (n, d) => { const i = args.indexOf("--" + n); return i >= 0 && args[i + 1] && !args[i + 1].startsWith("--") ? args[i + 1] : d; };
const flag = (n) => args.includes("--" + n);

function selftest() {
  let fallos = 0;
  for (const t of TAREAS) {
    for (const bien of [true, false]) {
      const d = fs.mkdtempSync(path.join(os.tmpdir(), "jeval-st-"));
      try {
        const ctx = t.simular(d, bien);
        const r = t.grade({ ...ctx, dir: d });
        const ok = r.pass === bien;
        if (!ok) fallos++;
        console.log(`${ok ? "OK  " : "FAIL "} ${t.id.padEnd(30)} case ${bien ? "good" : "bad "} → pass=${r.pass} (${r.detalle})`);
      } finally { if (path.basename(d).startsWith("jeval-st-")) fs.rmSync(d, { recursive: true, force: true }); }
    }
  }
  console.log(fallos ? `\n${fallos} grader(s) badly calibrated` : "\nEvery grader tells the good case from the bad one.");
  process.exit(fallos ? 1 : 0);
}

function correr(tarea, dir, modelo, gateway, timeoutS) {
  return new Promise((resolve) => {
    const base = ["-p", tarea.prompt, "--output-format", "stream-json", "--verbose", "--model", modelo, "--permission-mode", "acceptEdits",
      "--allowedTools", "Bash,Read,Write,Edit,Glob,Grep", "--strict-mcp-config", "--mcp-config", MCP_VACIO];
    const [cmd, cargs] = gateway
      ? (WIN ? ["pwsh", ["-NoProfile", "-File", path.join(os.homedir(), ".claude", "scripts", "claude-multi.ps1"), ...base]]
             : ["bash", [path.join(os.homedir(), ".claude", "scripts", "claude-multi.sh"), ...base]])
      : [CLAUDE, base];
    const p = spawn(cmd, cargs, { cwd: dir, stdio: ["ignore", "pipe", "pipe"] });
    let out = ""; const t0 = Date.now(); let vencio = false;
    const reloj = setTimeout(() => { vencio = true; p.kill(); }, timeoutS * 1000);
    p.stdout.on("data", (c) => (out += c));
    p.on("close", () => {
      clearTimeout(reloj);
      const tools = []; let texto = "", uso = {}, costo = null;
      for (const l of out.split("\n")) {
        if (!l.trim().startsWith("{")) continue;
        let o; try { o = JSON.parse(l); } catch { continue; }
        if (o.type === "assistant") for (const b of o.message?.content || []) if (b.type === "tool_use") tools.push({ name: b.name, input: b.input });
        if (o.type === "result") { texto = o.result || ""; uso = o.usage || {}; costo = o.total_cost_usd ?? null; }
      }
      resolve({ texto, tools, uso, costo, seg: Math.round((Date.now() - t0) / 100) / 10, vencio });
    });
  });
}

async function ejecutar() {
  const modelo = opt("model", "sonnet");
  const gateway = flag("gateway");
  const timeoutS = Number(opt("timeout", 150));
  const solo = opt("only", "") ? opt("only", "").split(",") : null;
  const tareas = TAREAS.filter((t) => !solo || solo.includes(t.id));
  if (!gateway && path.isAbsolute(CLAUDE) && !fs.existsSync(CLAUDE)) { console.error("CLAUDE_BIN not found: " + CLAUDE); process.exit(1); }
  fs.mkdirSync(path.dirname(HIST), { recursive: true });
  const corrida = new Date().toISOString();
  let pasan = 0;
  console.log(`Run ${corrida} · model=${modelo}${gateway ? " (via gateway)" : ""} · ${tareas.length} tasks\n`);
  for (const t of tareas) {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "jeval-"));
    try {
      t.setup(dir);
      const r = await correr(t, dir, modelo, gateway, timeoutS);
      const v = r.vencio ? { pass: false, detalle: `timeout ${timeoutS}s` } : t.grade({ dir, texto: r.texto, tools: r.tools });
      if (v.pass) pasan++;
      console.log(`${v.pass ? "PASS " : "FAIL "} ${t.id.padEnd(30)} ${String(r.seg).padStart(6)}s  ${v.detalle}`);
      fs.appendFileSync(HIST, JSON.stringify({ corrida, modelo: modelo + (gateway ? "@gw" : ""), tarea: t.id, pass: v.pass, detalle: v.detalle, respuesta: String(r.texto ?? "").slice(0, 600), seg: r.seg, usd_equiv: r.costo, tokens_out: r.uso?.output_tokens ?? null }) + "\n");
    } finally { if (path.basename(dir).startsWith("jeval-")) fs.rmSync(dir, { recursive: true, force: true }); }
  }
  console.log(`\n${pasan}/${tareas.length} pass. History: ${HIST}`);
}

function reporte() {
  if (!fs.existsSync(HIST)) return console.log("No history yet.");
  const filas = fs.readFileSync(HIST, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  const grupos = {};
  for (const r of filas) (grupos[r.modelo + "|" + r.tarea] ||= []).push(r);
  console.log("model · task".padEnd(52) + "latest   previous  verdict");
  for (const [k, v] of Object.entries(grupos)) {
    const [u, a] = [v.at(-1), v.at(-2)];
    const est = !a ? "first measurement" : u.pass === a.pass ? "stable" : u.pass ? "IMPROVED" : "REGRESSION";
    console.log(k.replace("|", " · ").padEnd(52) + (u.pass ? "pass    " : "fail    ") + (a ? (a.pass ? "pass      " : "fail      ") : "—         ") + est);
  }
}

if (flag("selftest")) selftest();
else if (flag("list")) TAREAS.forEach((t) => console.log(t.id.padEnd(30), t.regla));
else if (flag("report")) reporte();
else ejecutar();
