---
description: Lanza 7 workers especializados de marketing en paralelo vía Claude Flow. Cada worker cubre un dominio del marketingskills repo (SEO, CRO, Copy, Paid, Growth, Sales, Strategy) con la capa estratégica de Hormozi como base. Uso general — aplica a cualquier producto o cliente. Trigger: /marketing-swarm
argument-hint: "[contexto-del-producto] [objetivo-del-swarm]"
---

# Marketing Swarm — 7 Especialistas en Paralelo

## Comportamiento operativo

- Lanza un swarm jerárquico de 7 workers con dominios especializados.
- Usa contexto compartido de producto + objetivo único de campaña/análisis.
- Ejecuta análisis paralelo y consolida resultados en una síntesis accionable.
- Mantiene trazabilidad de asignación por dominio y output por worker.

## Qué hace este comando

Orquesta un análisis o tarea de marketing completa distribuyéndola entre 7 workers de Claude Flow, cada uno especializado en un dominio. Los workers corren en paralelo y entregan sus outputs a Jarvis para síntesis final.

## Cuándo usar

- Análisis de marketing completo de un producto (audit 360°)
- Lanzamiento de producto/servicio (todos los frentes en paralelo)
- Sprint de marketing intensivo (ejecutar múltiples dominios a la vez)
- Cuando el señor Ignacio necesite cobertura total sin trabajar secuencialmente

## Cómo invocar

```
/marketing-swarm
```

Jarvis pedirá dos inputs:
1. **Contexto del producto** — ruta a un archivo `.md` con ICP, oferta, diferenciadores, precios; o descripción inline
2. **Objetivo del swarm** — qué querés lograr (ej: "audit completo", "lanzamiento en 2 semanas", "optimizar conversión del funnel")

---

## Protocolo de ejecución

### Paso 1 — Recibir inputs

Antes de lanzar el swarm, Jarvis recopila:

```
PRODUCT_CONTEXT = [ruta al archivo .md o descripción inline]
SWARM_OBJECTIVE = [objetivo específico del análisis/tarea]
HORMOZI_FILE = C:/Users/w10/Downloads/HORMOZI-MAESTRO-MARKETING.md
```

Si el señor Ignacio tiene un `.agents/product-marketing-context.md` en el proyecto activo, leerlo automáticamente como PRODUCT_CONTEXT.

---

### Paso 2 — Inicializar hive-mind

```bash
claude-flow hive-mind spawn --agents 7 --topology hierarchical --name "marketing-swarm"
```

Jarvis = orquestador principal. Los 7 workers reciben sus asignaciones por broadcast.

---

### Paso 3 — Asignar dominios a workers

Cada worker recibe este contexto inicial obligatorio:
- `PRODUCT_CONTEXT` (el mismo para todos)
- `SWARM_OBJECTIVE` (el mismo para todos)
- Sus skills Haines específicos (listados abajo)
- El capítulo Hormozi correspondiente a su dominio

| Worker | Dominio | Skills Haines | Hormozi |
|--------|---------|---------------|---------|
| W1 | **SEO & Descubrimiento** | seo-audit, ai-seo, site-architecture, programmatic-seo, schema-markup, content-strategy, aso-audit | Cap. 13 (Content 80/20) |
| W2 | **CRO** | page-cro, signup-flow-cro, onboarding-cro, form-cro, popup-cro, paywall-upgrade-cro | Cap. 2 (Value Stack visible) + Cap. 7 (Fricción estratégica) |
| W3 | **Contenido & Copy** | copywriting, copy-editing, cold-email, email-sequence, social-content, video, image | Cap. 6 (Hooks + narrativa ganadora) + Cap. 8 (Lead Nurture 4 pilares) |
| W4 | **Paid & Medición** | paid-ads, ad-creative, ab-test-setup, analytics-tracking | Cap. 6 (Goated Ads estructura) + Cap. 15 (Framework Post-Cita) |
| W5 | **Growth & Retención** | referral-program, free-tool-strategy, churn-prevention, community-marketing, lead-magnets | Cap. 11 (Dependencia técnica activa) + Cap. 12 (Modelos monetización) + Cap. 14 (Fast Cash) |
| W6 | **Sales & GTM** | revops, sales-enablement, launch-strategy, pricing-strategy, competitor-alternatives, competitor-profiling, directory-submissions | Cap. 3-4 (Precio) + Cap. 9 (Tripwire/Cierre) + Cap. 10 (Objeciones) |
| W7 | **Estrategia** | marketing-ideas, marketing-psychology, customer-research, product-marketing-context | Cap. 1 (Ecuación de Valor) + Cap. 5 (Proof Social) + Cap. 16 (Principios maestros) |

---

### Paso 4 — Prompt base para cada worker

Cada worker recibe este prompt adaptado a su dominio:

```
Eres el especialista en [DOMINIO] de un equipo de marketing.

PRODUCTO/CONTEXTO:
[PRODUCT_CONTEXT]

OBJETIVO DEL SWARM:
[SWARM_OBJECTIVE]

TU TAREA:
Analiza el contexto desde la perspectiva de tu dominio ([DOMINIO]).
Aplica los frameworks de Hormozi ([CAPÍTULOS]) como capa estratégica.
Ejecuta con las metodologías de los skills: [SKILLS].

ENTREGA:
1. Diagnóstico actual del dominio (qué está bien / qué falta)
2. Top 3 acciones prioritarias con impacto estimado
3. Dependencias con otros dominios (qué necesitás de otros workers)
4. Quick wins ejecutables en menos de 48 horas

Sé específico, accionable y directo. Sin relleno.
```

---

### Paso 5 — Recopilar y sintetizar

Una vez que los 7 workers entregan sus outputs, Jarvis:

1. Consolida los 7 diagnósticos en una vista unificada
2. Identifica dependencias cruzadas (ej: W3 necesita datos de W7)
3. Prioriza las acciones por impacto × esfuerzo
4. Genera el **Plan de Acción Maestro** con:
   - Semana 1: Quick wins de todos los dominios
   - Semana 2-4: Acciones de mediano plazo
   - Backlog: iniciativas de largo plazo

---

## Output final esperado

```markdown
# Marketing Swarm — [Nombre del producto] — [Fecha]

## Diagnóstico por dominio
### W1 — SEO & Descubrimiento
### W2 — CRO
### W3 — Contenido & Copy
### W4 — Paid & Medición
### W5 — Growth & Retención
### W6 — Sales & GTM
### W7 — Estrategia

## Dependencias cruzadas detectadas
## Plan de Acción Maestro (priorizado)
## Quick Wins (< 48 horas)
```

---

## Variantes de uso

**Audit completo:**
```
/marketing-swarm → objetivo: "audit 360° del estado de marketing actual"
```

**Pre-lanzamiento:**
```
/marketing-swarm → objetivo: "preparar lanzamiento del producto en 3 semanas"
```

**Diagnóstico de funnel:**
```
/marketing-swarm → objetivo: "identificar dónde se cae la conversión del funnel"
```

**Sprint de contenido:**
```
/marketing-swarm → objetivo: "plan de contenido y distribución para Q2"
```

---

## Notas operativas

- Si Claude Flow no está disponible: ejecutar los 7 dominios secuencialmente activando los skills correspondientes de a uno.
- Cada worker debe recibir el archivo Hormozi completo si el análisis lo requiere (es denso — usarlo selectivamente por capítulo).
- El comando `/memoria ingest` después del swarm crea un nodo de sesión con el output consolidado.
- Para productos con `product-marketing-context.md` ya completo: ese archivo es el PRODUCT_CONTEXT ideal.
