import test from "node:test";
import assert from "node:assert/strict";
import { validar } from "./harness_guard.mjs";

const f = (id, extra = {}) => ({ id, descripcion: `desc ${id}`, pasos: ["a", "b"], pasa: false, ...extra });
const BASE = [f("login"), f("leads", { pasa: true, evidencia: "npm test leads → 12 pasan" })];

test("lista válida y sin cambios → sin violaciones", () => {
  const r = validar(BASE, BASE);
  assert.deepEqual(r.violaciones, []);
});

test("aprobar con evidencia es válido y NO toca descripcion/pasos", () => {
  const act = [f("login", { pasa: true, evidencia: "curl /login → 200 y cookie de sesión" }), BASE[1]];
  assert.deepEqual(validar(act, BASE).violaciones, []);
});

test("pasa:true sin evidencia → violación (no se puede declarar terminado por decreto)", () => {
  const r = validar([f("login", { pasa: true }), BASE[1]], BASE);
  assert.ok(r.violaciones.some((v) => v.includes("login") && v.includes("SIN evidencia")));
  assert.ok(validar([f("x", { pasa: true, evidencia: "ok" })]).violaciones.length === 1, "evidencia de <10 caracteres tampoco vale");
});

test("borrar una funcionalidad → violación", () => {
  const r = validar([BASE[0]], BASE);
  assert.ok(r.violaciones.some((v) => v.includes("leads") && v.includes("BORRÓ")));
});

test("editar descripcion o pasos para que sea más fácil → violación", () => {
  const act = [{ ...BASE[0], descripcion: "algo más fácil" }, { ...BASE[1], pasos: ["solo uno"] }];
  const r = validar(act, BASE);
  assert.ok(r.violaciones.some((v) => v.includes("login") && v.includes("descripcion")));
  assert.ok(r.violaciones.some((v) => v.includes("leads") && v.includes("pasos")));
});

test("regresión (true → false) es aviso, no violación; funcionalidades nuevas son aviso", () => {
  const act = [BASE[0], { ...BASE[1], pasa: false }, f("nueva")];
  const r = validar(act, BASE);
  assert.deepEqual(r.violaciones, []);
  assert.ok(r.avisos.some((a) => a.includes("regresión")) && r.avisos.some((a) => a.includes("nueva")));
});

test("esquema: ids repetidos, falta de pasos y forma inválida", () => {
  assert.ok(validar([f("a"), f("a")]).violaciones.some((v) => v.includes("repetido")));
  assert.ok(validar([{ id: "b", descripcion: "d", pasos: [], pasa: false }]).violaciones.some((v) => v.includes("pasos")));
  assert.ok(validar({ no: "es lista" }).violaciones.length === 1);
});
