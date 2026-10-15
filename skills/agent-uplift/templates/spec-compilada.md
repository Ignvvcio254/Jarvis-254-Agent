# Plantilla SPEC-COMPILER — convertir cualquier pedido en one-shot perfecto

> Jarvis llena esta plantilla ANTES de despachar. Todo entre {{ }} se reemplaza; secciones vacías se eliminan.

---

{{PREFIJO_EJECUCION — incluir SIEMPRE si la tarea edita/crea archivos:}}
INSTRUCCIÓN DE EJECUCIÓN: esta tarea se completa ÚNICAMENTE escribiendo archivos con tus herramientas. No describas planes. Lee lo mínimo necesario y ejecuta de inmediato.

{{CONTRAMEDIDAS del modelo destino — copiar desde antipatterns/<modelo>.md las que apliquen}}

## Contexto (verificado, no supuesto)
- Proyecto: {{qué es, stack, restricción principal}}
- Ya existe (verificado por grep): {{funciones/contratos exactos con nombres reales}}
- NO tocar: {{archivos/sistemas fuera de alcance}}

## Tarea — puntos numerados (cada uno con criterio observable)
1. {{acción}} → se verifica con: {{evidencia esperada: archivo, función, test, patrón grep}}
2. ...
{{máx 6 puntos para tier barato; si excede → descomponer antes de despachar}}

## Contrato de salida
- Archivos exactos a crear/editar: {{lista}}
- Prohibido: archivos extra, dependencias nuevas, console.log, modificar tests.
- Al terminar responde SOLO: {{"LISTO" | resumen máx N líneas mapeando cada punto}}

---

## Checklist del compilador (Jarvis, antes de despachar)
- [ ] Cada nombre de función/archivo citado fue verificado por grep en el código real.
- [ ] Cada punto numerado tiene UNA evidencia verificable (assert/grep/test).
- [ ] Tamaño acorde al tier (barato: ≤6 puntos, ≤1 archivo grande, "no leas archivos completos").
- [ ] Contramedidas del modelo destino inyectadas.
- [ ] Runner con check `edited`/`Test-Path` de cada entregable.
