import test from "node:test";
import assert from "node:assert/strict";
import { pedidoAOpenAI, respuestaAAnthropic, crearTraductorStream, motivoParada, paradaFinal } from "./anthropic-openai.mjs";

test("system, texto y límite de max_tokens", () => {
  const o = pedidoAOpenAI({ model: "x", max_tokens: 128000, system: [{ type: "text", text: "A" }, { type: "text", text: "B" }], messages: [{ role: "user", content: "hola" }] }, { maxOut: 8192 });
  assert.equal(o.messages[0].content, "A\n\nB");
  assert.equal(o.messages[1].content, "hola");
  assert.equal(o.max_tokens, 8192);
});

test("tool_use del asistente y tool_result del usuario se mapean a tool_calls / role:tool", () => {
  const o = pedidoAOpenAI({
    model: "x", max_tokens: 100,
    messages: [
      { role: "user", content: "lee a.txt" },
      { role: "assistant", content: [{ type: "thinking", thinking: "..." }, { type: "text", text: "ok" }, { type: "tool_use", id: "t1", name: "Read", input: { path: "a.txt" } }] },
      { role: "user", content: [{ type: "tool_result", tool_use_id: "t1", content: [{ type: "text", text: "contenido" }] }, { type: "text", text: "sigue" }] },
    ],
  });
  // sin `system`: [0]=user, [1]=assistant, [2]=tool, [3]=user
  const a = o.messages[1];
  assert.equal(a.role, "assistant");
  assert.equal(a.tool_calls[0].function.name, "Read");
  assert.deepEqual(JSON.parse(a.tool_calls[0].function.arguments), { path: "a.txt" });
  assert.equal(o.messages[2].role, "tool");
  assert.equal(o.messages[2].tool_call_id, "t1");
  assert.equal(o.messages[2].content, "contenido");
  assert.equal(o.messages[3].role, "user"); // el texto del usuario va DESPUÉS de los tool
  assert.ok(!JSON.stringify(o).includes("thinking"));
});

test("extraToolCall se agrega a cada tool_call del historial (firma de Gemini)", () => {
  const extra = { extra_content: { google: { thought_signature: "skip_thought_signature_validator" } } };
  const o = pedidoAOpenAI({ model: "x", max_tokens: 10, messages: [
    { role: "user", content: "." },
    { role: "assistant", content: [{ type: "tool_use", id: "t1", name: "Read", input: {} }, { type: "tool_use", id: "t2", name: "Read", input: {} }] },
  ] }, { extraToolCall: extra });
  assert.equal(o.messages[1].tool_calls.length, 2);
  for (const tc of o.messages[1].tool_calls) assert.equal(tc.extra_content.google.thought_signature, "skip_thought_signature_validator");
  // sin la opción, no se agrega nada
  const limpio = pedidoAOpenAI({ model: "x", max_tokens: 10, messages: [{ role: "assistant", content: [{ type: "tool_use", id: "t1", name: "R", input: {} }] }] });
  assert.ok(!("extra_content" in limpio.messages[0].tool_calls[0]));
});

test("herramientas: esquema limpio y tool_choice", () => {
  const o = pedidoAOpenAI({ model: "x", max_tokens: 10, messages: [{ role: "user", content: "." }], tools: [{ name: "T", description: "d", input_schema: { $schema: "http://json-schema.org/draft-07/schema#", type: "object", properties: { n: { type: "number", exclusiveMinimum: 0 } } } }], tool_choice: { type: "any" } });
  assert.equal(o.tools[0].function.name, "T");
  assert.ok(!("$schema" in o.tools[0].function.parameters));
  assert.ok(!("exclusiveMinimum" in o.tools[0].function.parameters.properties.n));
  assert.equal(o.tool_choice, "required");
});

test("respuesta normal con tool_calls → tool_use y stop_reason", () => {
  const r = respuestaAAnthropic({ id: "c1", choices: [{ message: { content: "ok", tool_calls: [{ id: "t9", function: { name: "Bash", arguments: "{\"cmd\":\"ls\"}" } }] }, finish_reason: "tool_calls" }], usage: { prompt_tokens: 5, completion_tokens: 7 } }, "m");
  assert.equal(r.stop_reason, "tool_use");
  assert.deepEqual(r.content[1], { type: "tool_use", id: "t9", name: "Bash", input: { cmd: "ls" } });
  assert.deepEqual(r.usage, { input_tokens: 5, output_tokens: 7 });
});

test("streaming: texto → herramienta → fin, con orden de eventos válido", () => {
  const t = crearTraductorStream("m");
  let s = "";
  s += t.chunk({ choices: [{ delta: { content: "ho" } }] });
  s += t.chunk({ choices: [{ delta: { content: "la" } }] });
  s += t.chunk({ choices: [{ delta: { tool_calls: [{ index: 0, id: "t1", function: { name: "Read", arguments: "{\"p\":" } }] } }] });
  s += t.chunk({ choices: [{ delta: { tool_calls: [{ index: 0, function: { arguments: "1}" } }] }, finish_reason: "tool_calls" }] });
  s += t.chunk({ choices: [], usage: { prompt_tokens: 3, completion_tokens: 4 } });
  s += t.fin();
  const eventos = [...s.matchAll(/^event: (\w+)/gm)].map((m) => m[1]);
  assert.deepEqual(eventos, ["message_start", "content_block_start", "content_block_delta", "content_block_delta", "content_block_stop", "content_block_start", "content_block_delta", "content_block_delta", "content_block_stop", "message_delta", "message_stop"]);
  assert.ok(s.includes('"stop_reason":"tool_use"'));
  assert.ok(s.includes('"output_tokens":4'));
  assert.ok(s.includes('"partial_json":"{\\"p\\":"'));
});

test("streaming: respuesta vacía aún produce un bloque válido", () => {
  const t = crearTraductorStream("m");
  const s = t.fin();
  assert.ok(s.includes("content_block_start") && s.includes("message_stop"));
});

test("motivos de parada", () => {
  assert.equal(motivoParada("length"), "max_tokens");
  assert.equal(motivoParada("stop"), "end_turn");
  assert.equal(motivoParada(undefined), "end_turn");
});

test("finish_reason length gana sobre tool_use (argumentos truncados no son una llamada válida)", () => {
  assert.equal(paradaFinal("length", true), "max_tokens");
  assert.equal(paradaFinal("tool_calls", true), "tool_use");
  assert.equal(paradaFinal("stop", false), "end_turn");
  const t = crearTraductorStream("m");
  let s = t.chunk({ choices: [{ delta: { tool_calls: [{ index: 0, id: "t1", function: { name: "Read", arguments: "{\"p\":" } }] }, finish_reason: "length" }] });
  s += t.fin();
  assert.ok(s.includes('"stop_reason":"max_tokens"'));
  const r = respuestaAAnthropic({ choices: [{ message: { tool_calls: [{ id: "a", function: { name: "R", arguments: "{" } }] }, finish_reason: "length" }] }, "m");
  assert.equal(r.stop_reason, "max_tokens");
});

test("llamadas paralelas con el MISMO index pero id distinto abren bloques separados", () => {
  const t = crearTraductorStream("m");
  let s = "";
  s += t.chunk({ choices: [{ delta: { tool_calls: [{ index: 0, id: "a", function: { name: "Read", arguments: "{\"x\":1}" } }] } }] });
  s += t.chunk({ choices: [{ delta: { tool_calls: [{ index: 0, id: "b", function: { name: "Grep", arguments: "{\"y\":2}" } }] }, finish_reason: "tool_calls" }] });
  s += t.fin();
  const inicios = [...s.matchAll(/"content_block":\{"type":"tool_use","id":"(\w+)","name":"(\w+)"/g)].map((m) => m[1] + ":" + m[2]);
  assert.deepEqual(inicios, ["a:Read", "b:Grep"]);
});

test("un error dentro del SSE termina como evento error, sin message_stop exitoso", () => {
  const t = crearTraductorStream("m");
  let s = t.chunk({ choices: [{ delta: { content: "hol" } }] });
  s += t.chunk({ error: { message: "boom" } });
  s += t.fin(); // no debe agregar un final exitoso después del error
  assert.ok(s.includes("event: error") && s.includes("boom"));
  assert.ok(!s.includes("message_stop"));
  assert.ok(crearTraductorStream("m").error("corte").includes("overloaded_error"));
});

test("el uso de entrada viaja en message_delta (Claude Code lo usa para compactar)", () => {
  const t = crearTraductorStream("m");
  let s = t.chunk({ choices: [{ delta: { content: "x" } }] });
  s += t.chunk({ choices: [], usage: { prompt_tokens: 123, completion_tokens: 4 } });
  s += t.fin();
  assert.ok(s.includes('"input_tokens":123') && s.includes('"output_tokens":4'));
});

test("imagen por URL se traduce a image_url", () => {
  const o = pedidoAOpenAI({ model: "x", max_tokens: 5, messages: [{ role: "user", content: [{ type: "text", text: "mira" }, { type: "image", source: { type: "url", url: "https://e.test/a.png" } }] }] });
  assert.equal(o.messages[0].content[1].image_url.url, "https://e.test/a.png");
});
