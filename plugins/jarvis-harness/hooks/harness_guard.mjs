#!/usr/bin/env node
// HARNESS GUARD — hace cumplir las reglas de .harness/feature_list.json (skill long-run-harness).
// "La skill enseña, el hook impone": sin esto, la lista de funcionalidades se puede editar para que parezca terminada.
//
// Reglas (violación = exit 1):
//   1. Esquema: cada funcionalidad tiene id único, descripcion, pasos[] (≥1) y pasa (boolean).
//   2. pasa:true exige `evidencia` (≥ 10 caracteres: el comando o chequeo y su resultado). Sin evidencia no hay "pasa".
//   3. Contra la versión de git (--base, por defecto HEAD): no se borran funcionalidades, y `descripcion` y `pasos`
//      no cambian. Solo pueden cambiar `pasa`, `evidencia` y `nota`.
// Avisos (no fallan): funcionalidades nuevas; una que estaba en pasa:true y vuelve a false (regresión: exige `nota`).
//
// Uso:  node harness_guard.mjs [--dir <repo>] [--base HEAD]
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const lista = (j) => (Array.isArray(j) ? j : j?.features ?? j?.funcionalidades ?? null);
const igual = (a, b) => JSON.stringify(a) === JSON.stringify(b);

/** @returns {{violaciones:string[], avisos:string[]}} */
export function validar(actualJson, baseJson = null) {
  const violaciones = [], avisos = [];
  const act = lista(actualJson);
  if (!act) return { violaciones: ["feature_list.json debe ser un arreglo (o {features:[…]})"], avisos };
  const ids = new Set();
  for (const [i, f] of act.entries()) {
    const etiqueta = f?.id ?? `#${i}`;
    if (!f || typeof f.id !== "string" || !f.id) { violaciones.push(`funcionalidad #${i}: falta id`); continue; }
    if (ids.has(f.id)) violaciones.push(`${f.id}: id repetido`);
    ids.add(f.id);
    if (typeof f.descripcion !== "string" || !f.descripcion.trim()) violaciones.push(`${etiqueta}: falta descripcion`);
    if (!Array.isArray(f.pasos) || f.pasos.length < 1) violaciones.push(`${etiqueta}: pasos debe tener al menos 1 paso`);
    if (typeof f.pasa !== "boolean") violaciones.push(`${etiqueta}: pasa debe ser true/false`);
    if (f.pasa === true && !(typeof f.evidencia === "string" && f.evidencia.trim().length >= 10)) violaciones.push(`${etiqueta}: pasa:true SIN evidencia (comando + resultado) — no se puede marcar aprobada`);
  }
  const base = baseJson ? lista(baseJson) : null;
  if (base) {
    const porId = new Map(act.map((f) => [f?.id, f]));
    for (const b of base) {
      const a = porId.get(b.id);
      if (!a) { violaciones.push(`${b.id}: se BORRÓ una funcionalidad (no se permite; si ya no aplica, márcala con nota)`); continue; }
      if (a.descripcion !== b.descripcion) violaciones.push(`${b.id}: se modificó la descripcion (solo pueden cambiar pasa, evidencia y nota)`);
      if (!igual(a.pasos, b.pasos)) violaciones.push(`${b.id}: se modificaron los pasos (solo pueden cambiar pasa, evidencia y nota)`);
      if (b.pasa === true && a.pasa === false) avisos.push(`${b.id}: regresión (estaba aprobada y ahora no)${a.nota ? "" : " — falta `nota` que lo explique"}`);
    }
    const nuevas = act.filter((f) => !base.some((b) => b.id === f?.id));
    if (nuevas.length) avisos.push(`${nuevas.length} funcionalidad(es) nueva(s): ${nuevas.map((f) => f.id).join(", ")}`);
  }
  return { violaciones, avisos };
}

function main() {
  const args = process.argv.slice(2);
  const opt = (n, d) => { const i = args.indexOf("--" + n); return i >= 0 ? args[i + 1] : d; };
  const dir = path.resolve(opt("dir", "."));
  const baseRef = opt("base", "HEAD");
  const archivo = path.join(dir, ".harness", "feature_list.json");
  if (!fs.existsSync(archivo)) { console.log(`[harness_guard] no hay ${archivo}: nada que validar`); process.exit(0); }
  let actual; try { actual = JSON.parse(fs.readFileSync(archivo, "utf8")); } catch (e) { console.error("feature_list.json no es JSON válido: " + e.message); process.exit(1); }
  let base = null;
  try { base = JSON.parse(execFileSync("git", ["show", `${baseRef}:.harness/feature_list.json`], { cwd: dir, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] })); } catch { /* aún no está en git: solo esquema */ }
  const { violaciones, avisos } = validar(actual, base);
  for (const a of avisos) console.log("aviso:", a);
  if (violaciones.length) { for (const v of violaciones) console.error("VIOLACIÓN:", v); console.error(`\n${violaciones.length} violación(es). La lista de funcionalidades no se edita para parecer terminada: se aprueba con evidencia.`); process.exit(1); }
  const total = lista(actual).length, ok = lista(actual).filter((f) => f.pasa).length;
  console.log(`[harness_guard] OK — ${ok}/${total} funcionalidades aprobadas${base ? " (contrastado con " + baseRef + ")" : " (sin versión previa en git: solo esquema)"}`);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) main();
