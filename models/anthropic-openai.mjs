// Traductor Anthropic Messages <-> OpenAI Chat Completions (puro, sin red, probado en anthropic-openai.test.mjs).
// Lo usa modelo-proxy.mjs para que Claude Code (que habla Anthropic) converse con proveedores que solo
// hablan el formato OpenAI (NVIDIA NIM, Gemini, Ollama…).
//
// Qué traduce: system, mensajes de texto, imágenes base64, tool_use/tool_result, tool_choice,
// max_tokens/temperature/top_p/stop, y la respuesta (normal y en streaming SSE).
// Qué descarta A PROPÓSITO: bloques `thinking` previos y `cache_control` (no existen al otro lado).

const textoDe = (c) =>
  typeof c === "string" ? c : Array.isArray(c) ? c.map((b) => (b?.type === "text" ? b.text : b?.type === "image" ? "[imagen]" : "")).join("") : "";

function limpiarEsquema(s) {
  // Gemini/OpenAI estrictos rechazan algunas palabras del JSON-Schema que Claude Code sí emite.
  if (Array.isArray(s)) return s.map(limpiarEsquema);
  if (s && typeof s === "object") {
    const o = {};
    for (const [k, v] of Object.entries(s)) {
      if (k === "$schema" || k === "$id" || k === "exclusiveMinimum" || k === "exclusiveMaximum") continue;
      o[k] = limpiarEsquema(v);
    }
    return o;
  }
  return s;
}

// `extraToolCall`: campos extra que ciertos proveedores exigen en CADA tool_call que se les reenvía.
// Gemini 3 (modo OpenAI) responde 400 "Function call is missing a thought_signature" si el historial trae
// llamadas a herramienta sin firma. Claude Code no conserva la firma real, así que se usa el valor
// de omisión que Google documenta para historiales inyectados: "skip_thought_signature_validator".
export function pedidoAOpenAI(body, { maxOut = 16384, modelo, extraToolCall = null } = {}) {
  const msgs = [];
  const sys = Array.isArray(body.system) ? body.system.map((b) => b.text || "").join("\n\n") : body.system;
  if (sys) msgs.push({ role: "system", content: sys });

  for (const m of body.messages || []) {
    const bloques = typeof m.content === "string" ? [{ type: "text", text: m.content }] : m.content || [];
    if (m.role === "assistant") {
      const texto = bloques.filter((b) => b.type === "text").map((b) => b.text).join("");
      const llamadas = bloques
        .filter((b) => b.type === "tool_use")
        .map((b) => ({ id: b.id, type: "function", function: { name: b.name, arguments: JSON.stringify(b.input ?? {}) }, ...(extraToolCall || {}) }));
      const out = { role: "assistant", content: texto || (llamadas.length ? null : "") };
      if (llamadas.length) out.tool_calls = llamadas;
      msgs.push(out);
    } else {
      // user: los tool_result van como mensajes `tool` ANTES del texto del usuario de este turno.
      const partes = [];
      for (const b of bloques) {
        if (b.type === "tool_result") {
          const t = textoDe(b.content);
          msgs.push({ role: "tool", tool_call_id: b.tool_use_id, content: b.is_error ? `ERROR: ${t}` : t || "(sin salida)" });
        } else if (b.type === "text") {
          partes.push({ type: "text", text: b.text });
        } else if (b.type === "image" && b.source?.type === "base64") {
          partes.push({ type: "image_url", image_url: { url: `data:${b.source.media_type};base64,${b.source.data}` } });
        } else if (b.type === "image" && b.source?.type === "url") {
          partes.push({ type: "image_url", image_url: { url: b.source.url } });
        }
      }
      if (partes.length) {
        const soloTexto = partes.every((p) => p.type === "text");
        msgs.push({ role: "user", content: soloTexto ? partes.map((p) => p.text).join("\n") : partes });
      }
    }
  }

  const o = { model: modelo ?? body.model, messages: msgs, max_tokens: Math.min(body.max_tokens ?? maxOut, maxOut), stream: !!body.stream };
  if (body.stream) o.stream_options = { include_usage: true };
  if (body.temperature != null) o.temperature = body.temperature;
  if (body.top_p != null) o.top_p = body.top_p;
  if (body.stop_sequences?.length) o.stop = body.stop_sequences;
  if (body.tools?.length) {
    o.tools = body.tools.map((t) => ({
      type: "function",
      function: { name: t.name, description: t.description || "", parameters: limpiarEsquema(t.input_schema || { type: "object", properties: {} }) },
    }));
    const tc = body.tool_choice;
    if (tc) {
      if (tc.type === "auto") o.tool_choice = "auto";
      else if (tc.type === "any") o.tool_choice = "required";
      else if (tc.type === "none") o.tool_choice = "none";
      else if (tc.type === "tool") o.tool_choice = { type: "function", function: { name: tc.name } };
    }
  }
  return o;
}

const PARADA = { stop: "end_turn", length: "max_tokens", tool_calls: "tool_use", function_call: "tool_use", content_filter: "end_turn" };
export const motivoParada = (r) => PARADA[r] || "end_turn";
// Una respuesta cortada por límite de tokens NO es una llamada a herramienta válida aunque haya bloques tool_use
// (sus argumentos JSON quedaron a medias): se declara max_tokens para que Claude Code no ejecute basura.
export const paradaFinal = (finish, huboHerramienta) => (finish === "length" ? "max_tokens" : huboHerramienta ? "tool_use" : motivoParada(finish));

const parseJSON = (s) => { try { return JSON.parse(s || "{}"); } catch { return {}; } };

export function respuestaAAnthropic(j, modelo) {
  const ch = j.choices?.[0] || {};
  const m = ch.message || {};
  const content = [];
  if (m.content) content.push({ type: "text", text: m.content });
  for (const tc of m.tool_calls || []) content.push({ type: "tool_use", id: tc.id, name: tc.function?.name, input: parseJSON(tc.function?.arguments) });
  if (!content.length) content.push({ type: "text", text: "" });
  return {
    id: j.id || "msg_proxy", type: "message", role: "assistant", model: modelo, content,
    stop_reason: paradaFinal(ch.finish_reason, content.some((b) => b.type === "tool_use")),
    stop_sequence: null,
    usage: { input_tokens: j.usage?.prompt_tokens ?? 0, output_tokens: j.usage?.completion_tokens ?? 0 },
  };
}

const sse = (evento, datos) => `event: ${evento}\ndata: ${JSON.stringify(datos)}\n\n`;

/** Máquina de estados: recibe chunks OpenAI ya parseados (objetos), devuelve strings SSE de Anthropic. */
export function crearTraductorStream(modelo) {
  let iniciado = false, indice = -1, tipoAbierto = null, terminado = false;
  const herramientas = new Map(); // índice OpenAI -> { bloque (índice Anthropic), id }
  let paradaOpenAI = null, tokensIn = 0, tokensOut = 0, huboHerramienta = false;

  const cerrar = () => { if (tipoAbierto === null) return ""; const s = sse("content_block_stop", { type: "content_block_stop", index: indice }); tipoAbierto = null; return s; };
  const iniciar = () => iniciado ? "" : ((iniciado = true), sse("message_start", { type: "message_start", message: { id: "msg_proxy", type: "message", role: "assistant", model: modelo, content: [], stop_reason: null, stop_sequence: null, usage: { input_tokens: tokensIn, output_tokens: 0 } } }));

  return {
    chunk(c) {
      if (terminado) return "";
      // Un 200 con {"error":…} dentro del SSE (medido en otros gateways) no trae `choices`: antes se ignoraba y la
      // respuesta terminaba "vacía y exitosa". Ahora se propaga como evento de error.
      if (c.error) return this.error(typeof c.error === "string" ? c.error : c.error.message || JSON.stringify(c.error));
      let out = iniciar();
      if (c.usage) { tokensIn = c.usage.prompt_tokens ?? tokensIn; tokensOut = c.usage.completion_tokens ?? tokensOut; }
      const ch = c.choices?.[0];
      if (!ch) return out;
      const d = ch.delta || {};
      if (d.content) {
        if (tipoAbierto !== "text") { out += cerrar(); indice++; tipoAbierto = "text"; out += sse("content_block_start", { type: "content_block_start", index: indice, content_block: { type: "text", text: "" } }); }
        out += sse("content_block_delta", { type: "content_block_delta", index: indice, delta: { type: "text_delta", text: d.content } });
      }
      for (const tc of d.tool_calls || []) {
        const k = tc.index ?? 0;
        const reg = herramientas.get(k);
        // Llamadas paralelas: si el proveedor repite index (o lo omite) pero manda un id DISTINTO, es otra llamada.
        if (!reg || (tc.id && reg.id && tc.id !== reg.id)) {
          out += cerrar(); indice++; tipoAbierto = "tool"; huboHerramienta = true;
          herramientas.set(k, { bloque: indice, id: tc.id });
          out += sse("content_block_start", { type: "content_block_start", index: indice, content_block: { type: "tool_use", id: tc.id || `toolu_${k}_${Date.now()}`, name: tc.function?.name || "", input: {} } });
        }
        const args = tc.function?.arguments;
        if (args) out += sse("content_block_delta", { type: "content_block_delta", index: herramientas.get(k).bloque, delta: { type: "input_json_delta", partial_json: args } });
      }
      if (ch.finish_reason) paradaOpenAI = ch.finish_reason;
      return out;
    },
    fin() {
      if (terminado) return "";
      terminado = true;
      let out = iniciar() + cerrar();
      if (indice === -1) { // respuesta vacía: Anthropic exige al menos un bloque
        indice = 0; out += sse("content_block_start", { type: "content_block_start", index: 0, content_block: { type: "text", text: "" } }) + sse("content_block_stop", { type: "content_block_stop", index: 0 });
      }
      const parada = paradaFinal(paradaOpenAI, huboHerramienta);
      return out + sse("message_delta", { type: "message_delta", delta: { stop_reason: parada, stop_sequence: null }, usage: { input_tokens: tokensIn, output_tokens: tokensOut } }) + sse("message_stop", { type: "message_stop" });
    },
    // Corte o error a mitad de respuesta: se avisa como error (Claude Code reintenta) en vez de simular un final exitoso.
    error(mensaje) {
      if (terminado) return "";
      terminado = true;
      return iniciar() + sse("error", { type: "error", error: { type: "overloaded_error", message: mensaje } });
    },
    ping: () => sse("ping", { type: "ping" }),
  };
}

export const errorAnthropic = (status, mensaje) => ({
  type: "error",
  error: { type: status === 401 || status === 403 ? "authentication_error" : status === 429 ? "rate_limit_error" : status === 400 ? "invalid_request_error" : "api_error", message: mensaje },
});
