---
name: autoresearch
description: "Auto-optimizacion autonoma de skills usando el patron de Karpathy + Curator de Hermes Agent. DOS MODOS: (A) optimizar un skill especifico con evals binarias, (B) curar el ecosistema completo de skills (fusion, archivado, transiciones de estado). Activar con: optimiza este skill, mejora el skill, autoresearch, self-improve, corre evals, evalua el skill, benchmark skill — O — curar skills, revisar skills obsoletos, fusionar skills, limpiar skills. NO USAR para: crear skills nuevos (usar skill-creator), correr skills normalmente."
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent
---

# Autoresearch: Self-Improving Skills + Curator

> Dos fuentes: patron Karpathy (optimizacion individual) + Curator de Hermes Agent/NousResearch (curación ecosistema).
> El principio: un loop autonomo que mejora skills indefinidamente, y un curador que mantiene el ecosistema sano.

---

## MODO B — Curator (ecosistema completo)

> Trigger: "curar skills", "revisar skills obsoletos", "fusionar skills", "limpiar skills"
> Corre autónomamente sin aprobación por skill individual.

### Filosofía

Inspirado en `curator.py` de Hermes Agent (NousResearch, 134k⭐):
- Skills acumulan entropía: duplicados, micro-skills que deberían ser subsecciones, skills obsoletos
- El curador fusiona, archiva y mantiene — **nunca borra**
- Skills con `pinned: true` en frontmatter son **inmunes** a toda transición

### Estados de un skill

```
activo ──(60d sin uso)──► stale ──(120d sin uso)──► archivado
  ▲                                                      │
  └──────────── restaurar manualmente si necesario ──────┘

pinned: true → inmune a todas las transiciones automáticas
```

### Protocolo Curator (5 pasos)

```
PASO 1: INVENTARIO
  Glob ~/.claude/skills/**/SKILL.md
  Extraer: name, description, última modificación
  Agrupar por prefijo/dominio (azure-*, seo-*, react-*, etc.)

PASO 2: TRANSICIONES AUTOMÁTICAS (sin LLM, basadas en git log)
  activo → stale:    sin commit/uso en >60 días
  stale → archivado: sin uso en >120 días AND NOT pinned

PASO 3: ANÁLISIS LLM (clusters de skills)
  Por cada cluster de prefijo compartido, preguntar:
    ¿Hacen lo mismo con distintos nombres? → candidatos a fusión
    ¿Un micro-skill debería ser subsección de un skill mayor? → umbrella
    ¿Hay redundancia con skills bundled del sistema? → candidato a archivar

PASO 4: CONSOLIDACIÓN
  Fusionar A + B → C (umbrella skill con lo mejor de ambos)
  Archivar A y B en ~/.claude/skills/_archived/YYYY-MM-DD-nombre/
  Añadir nota en A y B: "archived: absorbed into C — YYYY-MM-DD"
  NUNCA usar contadores de uso como único criterio de fusión

PASO 5: REPORTE al señor Ignacio
  Skills revisados: N | Fusiones: X | Archivados: Y | Pinned (intocados): Z
  Candidatos para revisión manual: [lista con razón]
  Append a cerebro/log.md: "[YYYY-MM-DD] curator run: X fusiones, Y archivados"
```

### Invariantes de seguridad (del Hermes curator)
- Solo actúa sobre `~/.claude/skills/` — NUNCA skills del sistema o plugins externos
- Archiva en `~/.claude/skills/_archived/YYYY-MM-DD-nombre/` (siempre recuperable)
- Ante cualquier duda → proponer al señor Ignacio, no ejecutar
- Registrar cada acción en `cerebro/log.md`

---

## MODO A — Karpathy Loop (skill individual)

## Filosofia

"Un skill ordinario optimizado durante un tiempo extraordinario produce resultados extraordinarios."
El interes compuesto aplicado a prompts. Cada iteracion es un micro-experimento.
Lo que importa no es la mejora individual (0.5%) sino la acumulacion (50 iteraciones = transformacion).

---

## Fase 1: Setup (con el usuario)

Antes de correr autonomamente, alinear con el usuario:

### 1.1 Identificar el skill target

Leer el SKILL.md completo del skill target. Entender que hace, que outputs produce, que herramientas usa.

### 1.2 Definir las Evals

Las evals son la UNICA forma de medir si el skill mejoro. Sin buenas evals, autoresearch es ruido.

**Reglas de evals:**
1. **SIEMPRE binarias** (si/no, pass/fail). NUNCA escalas Likert.
2. **3-6 criterios** por skill.
3. **Nunca demasiado estrechos.** No optimizar para un solo atributo superficial.
4. **Cubrir dimensiones ortogonales.** Cada criterio mide algo DIFERENTE.

### 1.3 Definir parametros

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| `N` | 5 | Outputs generados por ciclo |
| `max_score` | N * num_criterios | Score maximo posible |
| `interval` | 3 min | Tiempo entre ciclos |
| `target_score` | 90% del max | Score para considerar "excelente" |
| `max_iterations` | 30 | Limite de iteraciones |
| `budget` | $5 USD | Limite de gasto estimado |

### 1.4 Crear branch y baseline

```bash
git checkout -b autoresearch/<skill-name>
```

- Copiar el SKILL.md a `<skill>/SKILL.md.backup`
- Inicializar `<skill>/autoresearch-results.tsv`:
  ```
  iteration	score	max_score	pct	status	changes_summary
  ```
- Correr la primera evaluacion como **baseline** (iteration 0, status: baseline)
- Confirmar con el usuario: "Baseline: X/Y (Z%). Arranco?"

**Una vez el usuario confirma, NO PARAR.**

---

## Fase 2: El Loop (autonomo)

> "El humano puede estar dormido. NUNCA pausar para preguntar."

### El ciclo exacto:

```
LOOP (hasta max_iterations o target_score):

  1. ANALIZAR — Leer resultados previos. Que fallo? Que patron emerge?

  2. HIPOTESIS — Formular UNA hipotesis clara:
     "Si cambio X en el prompt, deberia mejorar Y porque Z"

  3. MUTAR — Editar el SKILL.md del skill target
     - UN cambio por iteracion
     - NUNCA tocar el frontmatter
     - NUNCA copiar los criterios de eval al prompt (gaming)

  4. COMMIT — git add + git commit ANTES de correr
     Mensaje: "autoresearch(<skill>): iter N — <hipotesis corta>"

  5. GENERAR — Correr el skill N veces con inputs variados

  6. EVALUAR — Para cada output, aplicar cada criterio (si/no)
     Score = total "si" / max_score

  7. DECIDIR:
     - Score > best_score -> STATUS: keep (commit se queda)
     - Score <= best_score -> STATUS: discard (git reset --hard HEAD~1)
     - Crash -> STATUS: crash (fix trivial o revertir)

  8. REGISTRAR — Append a autoresearch-results.tsv

  9. REPETIR
```

### Reglas del loop

- **UN cambio por iteracion.** Aislamiento de variables.
- **Inputs variados.** Al menos 3 inputs diferentes por ciclo.
- **Simplicidad > complejidad.** Eliminar lineas que no aportan = mejor que agregar.
- **Crash tolerance.** Log it, revert, try different approach.

### Criterio de simplicidad (Karpathy)

> Mejora pequena por ELIMINAR complejidad = SIEMPRE vale la pena.
> Agregar 10 instrucciones para subir 5% = cuestionable.

---

## Fase 3: Reporte

Cuando se alcanza `target_score` o `max_iterations`:

```
## Autoresearch Report: <skill-name>

**Baseline:** X/Y (Z%)
**Final:** X/Y (Z%)
**Mejora:** +N% en M iteraciones
**Costo estimado:** ~$X USD

### Cambios que mejoraron:
1. Iter N: <cambio> -> +X%

### Cambios que NO mejoraron:
1. Iter N: <cambio> -> descartado
```

Mostrar al usuario. Si aprueba: `git checkout main && git merge autoresearch/<skill>`.

---

## Tipos de Evaluacion

### Codigo
- El codigo compila/funciona sin errores? (si/no)
- Sigue los patrones del proyecto? (si/no)
- No introduce vulnerabilidades? (si/no)
- Es mantenible y legible? (si/no)

### Texto
- Contiene la informacion clave solicitada? (si/no)
- El tono es apropiado? (si/no)
- La estructura es clara? (si/no)
- No hay informacion inventada? (si/no)

### Visual
- Todo el texto es legible? (si/no)
- El layout es claro? (si/no)
- Comunica la idea sin ambiguedad? (si/no)

---

## Limites de Seguridad

| Limite | Valor |
|--------|-------|
| Max iteraciones | 30 |
| Budget | $5 USD |
| Max prompt growth | 2x original |
| Backup | Siempre obligatorio |
| Branch dedicado | Siempre |
| Solo body del SKILL.md | Frontmatter es sacrosanto |