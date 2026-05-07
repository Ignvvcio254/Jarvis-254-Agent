# Compresión de contexto — Contrato protect_n

Contrato de compresión de contexto adoptado desde el patrón `context_engine.py` de NousResearch/hermes-agent.

## Implementación

`jarvis_core/cerebro_index.py` — clase `ContextCompressor`.

## Parámetros

| Parámetro | Default | Significado |
|---|---|---|
| `protect_first_n` | 3 | Nunca comprimir los primeros N mensajes (instrucciones de sistema, contexto inicial) |
| `protect_last_n` | 6 | Nunca comprimir los últimos N mensajes (coherencia de sesión activa) |
| `threshold` | 0.75 | Activar compresión cuando el uso llega al 75% del context window |

## Por qué estos valores

- `protect_first_n = 3`: los primeros mensajes contienen `CLAUDE.md`, contexto del proyecto y sesión — comprimirlos destruye la identidad del agente.
- `protect_last_n = 6`: los últimos 6 mensajes son la conversación activa — comprimirlos produce respuestas incoherentes.
- `threshold = 0.75`: compresión preventiva antes de saturar el window, no reactiva cuando ya hay problemas.

## Uso programático

```python
from jarvis_core.cerebro_index import ContextCompressor

compressor = ContextCompressor(
    protect_first_n=3,
    protect_last_n=6,
    threshold=0.75,
)

# Verificar si comprimir
if compressor.should_compress(used_tokens=150_000, max_tokens=200_000):
    messages = compressor.compress(messages, summarizer=my_llm_summarizer)

# Ver configuración activa
print(compressor.describe())
```

## Búsqueda FTS5 en cerebro/

`jarvis_core/cerebro_index.py` — clase `CerebroIndex`.

Reemplaza búsqueda lineal del wiki con SQLite FTS5 (ranking BM25, sin dependencias externas).

```bash
# Indexar nodos de cerebro/ (necesario una vez tras clonar)
python -c "from pathlib import Path; from jarvis_core.cerebro_index import CerebroIndex; CerebroIndex(Path('.')).build(force=True)"

# Buscar desde el CLI
python jarvis_runtime.py memory search "token budget"
python jarvis_runtime.py memory search "hermes" --limit 5
```

El índice se persiste en `cerebro/cerebro_fts.db` (ignorado por git). Se reconstruye automáticamente si no existe.

## Impacto en consumo de tokens

| Comportamiento | Sin protect_n | Con protect_n |
|---|---|---|
| Compresión de instrucciones del sistema | Posible (destruye identidad) | Bloqueado |
| Compresión de contexto activo | Posible (genera incoherencia) | Bloqueado |
| Zona comprimible | Todo el historial | Solo mensajes intermedios |
| Búsqueda en cerebro/ | Lineal O(n archivos) | FTS5 O(log n) con BM25 |
