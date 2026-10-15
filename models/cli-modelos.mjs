// Participantes que NO se llaman por API sino ejecutando su CLI OFICIAL con la sesión del propio usuario.
// Hoy: Codex (`cli/codex` o `cli/codex:<modelo>`), que usa la suscripción de ChatGPT del usuario.
//
// Por qué así y no a través del gateway: enrutar el token OAuth de una suscripción por un intermediario propio NO está
// cubierto por los términos de los proveedores (Anthropic lo prohíbe; OpenAI solo autoriza 'Sign in with ChatGPT' para
// terceros nombrados). Ejecutar el CLI OFICIAL, con su propia sesión, es exactamente el uso previsto: aquí no se lee,
// copia ni reenvía ninguna credencial.
//
// Contención: carpeta temporal VACÍA como directorio de trabajo, sandbox de solo lectura, sin sesión persistida (--ephemeral),
// tiempo máximo, árbol de procesos eliminado al vencer, y variable de entorno mínima.
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const CODEX_JS = () => process.env.CODEX_JS || path.join(process.env.APPDATA || "", "npm", "node_modules", "@openai", "codex", "bin", "codex.js");
const ENV = () => Object.fromEntries(["PATH", "SystemRoot", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "HOMEDRIVE", "HOMEPATH", "COMSPEC", "PATHEXT"].filter((k) => process.env[k]).map((k) => [k, process.env[k]]));

export const esCli = (modelo) => typeof modelo === "string" && modelo.startsWith("cli/");

function matarArbol(p) { try { if (process.platform === "win32") spawnSync("taskkill", ["/pid", String(p.pid), "/T", "/F"], { stdio: "ignore" }); else p.kill("SIGKILL"); } catch { /* ya terminó */ } }

/** Devuelve { modelo, ms, texto } o { modelo, ms, error } — mismo contrato que las llamadas por gateway. */
export async function llamarCli(modelo, system, user, { timeoutMs = 180_000 } = {}) {
  const t0 = Date.now();
  const [proveedor, variante] = modelo.slice(4).split(":");
  if (proveedor !== "codex") return { modelo, ms: 0, error: `CLI desconocido: ${proveedor}` };
  const js = CODEX_JS();
  if (!fs.existsSync(js)) return { modelo, ms: 0, error: "Codex no está instalado (npm i -g @openai/codex)" };
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "cli-codex-"));
  const salida = path.join(dir, "respuesta.txt");
  const prompt = `${system}\n\nResponde DIRECTAMENTE con tu respuesta final; no ejecutes comandos ni leas archivos.\n\n${user}`;
  const args = [js, "exec", "--skip-git-repo-check", "--ephemeral", "-s", "read-only", "--color", "never", "-C", dir, "-o", salida, ...(variante ? ["-m", variante] : []), "-"];
  try {
    return await new Promise((resolve) => {
      const p = spawn(process.execPath, args, { cwd: dir, env: ENV(), stdio: ["pipe", "ignore", "pipe"] });
      let err = "", vencido = false;
      p.stderr.on("data", (c) => { if (err.length < 2000) err += c; });
      p.stdin.on("error", () => {}); p.stdin.end(prompt, "utf8");                 // el prompt va por stdin: sin límites ni escapes de línea de comandos
      const reloj = setTimeout(() => { vencido = true; matarArbol(p); }, timeoutMs);
      p.on("close", (code) => {
        clearTimeout(reloj);
        let texto = ""; try { texto = fs.readFileSync(salida, "utf8").trim(); } catch { /* sin archivo de salida */ }
        if (vencido) return resolve({ modelo, ms: Date.now() - t0, error: `Codex sin respuesta en ${Math.round(timeoutMs / 1000)} s` });
        if (!texto) return resolve({ modelo, ms: Date.now() - t0, error: `Codex terminó sin respuesta (código ${code}): ${err.replace(/\s+/g, " ").slice(0, 160)}` });
        resolve({ modelo, ms: Date.now() - t0, texto });
      });
      p.on("error", (e) => { clearTimeout(reloj); resolve({ modelo, ms: Date.now() - t0, error: "no pude ejecutar Codex: " + e.message }); });
    });
  } finally {
    if (path.basename(dir).startsWith("cli-codex-")) { try { fs.rmSync(dir, { recursive: true, force: true, maxRetries: 8, retryDelay: 250 }); } catch { /* mejor esfuerzo */ } }
  }
}
