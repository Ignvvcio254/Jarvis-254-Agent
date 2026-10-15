---
name: long-run-harness
description: Método para trabajos LARGOS que cruzan varias sesiones (un módulo del CRM, una migración, una feature grande): sesión inicializadora que crea una lista de funcionalidades con banderas de aprobado, archivo de progreso y script de arranque; luego cada sesión retoma, hace UNA funcionalidad, la verifica con evidencia y deja commit. Úsalo cuando el trabajo no cabe en una sesión o cuando ya se declaró "terminado" algo que no lo estaba. Complementa a prp y bucle-agentico; no los reemplaza.
---

# Long-run harness — continuidad sin autoengaño

Basado en el patrón publicado por Anthropic para agentes de larga duración (agente inicializador + agente de código con
lista de funcionalidades, archivo de progreso y commits por funcionalidad), implementado con mis propias piezas:
`verify-repair` (veredicto), `scratchpad` (memoria de trabajo), `token-router` (modelo por dificultad) y un validador que
**impone** las reglas (`harness_guard.mjs`): la skill enseña, el hook impone.

## Cuándo usarlo y cuándo NO
- **Sí:** el trabajo abarca varias sesiones, tiene muchas piezas verificables, o el historial muestra "terminé" prematuros.
- **No:** un fix o una feature de una sesión (usa `bucle-agentico`), ni la planificación inicial de una feature (usa `prp`: el PRP
  puede ALIMENTAR la lista de funcionalidades de este harness).

## Archivos (en el repo del proyecto, carpeta `.harness/`)
| Archivo | Qué es | Quién lo cambia |
|---|---|---|
| `feature_list.json` | Lista de funcionalidades. Cada una: `id`, `descripcion`, `pasos[]`, `pasa` (false al inicio), `evidencia`, `nota` | Solo `pasa`, `evidencia` y `nota` cambian. Jamás se borra, reordena ni se editan `descripcion`/`pasos` |
| `progress.md` | Bitácora: qué se hizo, por qué, qué sigue, bloqueos | Se agrega al final en cada sesión |
| `init.ps1` (o `.sh`) | Levanta el entorno y corre un humo mínimo (build, servidor, un test de ida y vuelta) | Se crea una vez y se mantiene |

Ejemplo de funcionalidad:
```json
{ "id": "leads-filtro-estado", "descripcion": "Filtrar leads por estado y recordar el filtro en la URL",
  "pasos": ["abrir /leads", "elegir estado 'contactado'", "la tabla muestra solo contactados", "recargar: el filtro persiste"],
  "pasa": false }
```

## Sesión 1 — inicializadora (no se escribe código de producto)
1. Entender el objetivo y las restricciones del proyecto (CLAUDE.md, reglas, patrones obligatorios).
2. Redactar `feature_list.json` **exhaustiva y granular**: cada funcionalidad verificable de punta a punta por una persona usando la app.
   Mejor 60 funcionalidades pequeñas que 8 vagas. Todas `pasa:false`.
3. Crear `init.ps1` y comprobar que corre limpio desde cero.
4. Crear `progress.md` con el contexto y el orden de ataque recomendado (por dependencias).
5. Commit en una **rama de trabajo** (nunca `main`): `chore(harness): lista de funcionalidades inicial`.
6. Validar: `node ~/.claude/scripts/harness_guard.mjs` → debe decir OK.

## Sesiones siguientes — una funcionalidad por turno de trabajo
1. **Orientarse:** leer `progress.md`, `git log --oneline -15` y `feature_list.json`.
2. **Humo:** correr `init.ps1`. Si el estado base está roto, **arreglar eso primero** y registrarlo; no apilar trabajo sobre un cimiento roto.
3. **Elegir UNA** funcionalidad `pasa:false` (respetando dependencias). Una. No dos "ya que estamos".
4. Implementar. Modelo por dificultad con `token-router`; delegar lo mecánico a `worker-low`.
5. **Verificar de punta a punta como lo haría una persona** (navegador/curl/test real, no solo "compila"). Usar `verify-repair`.
6. Solo con la verificación pasando, marcar `pasa:true` y escribir `evidencia`: el comando o chequeo **y su resultado**
   (ej. `playwright leads-filtro.spec → 4/4 pasos OK`). Sin evidencia el validador la rechaza.
7. Agregar a `progress.md`: qué hice, qué decidí y por qué, qué sigue, qué quedó bloqueado.
8. `node ~/.claude/scripts/harness_guard.mjs` → OK, y **commit** (`feat(<id>): …`). Parar o seguir con la siguiente.

## Reglas que no se negocian
- **No se declara terminado por decreto.** El estado del proyecto es el de `feature_list.json`, no mi impresión.
- **No se baja la vara:** prohibido editar `descripcion` o `pasos` para que algo "pase"; prohibido borrar funcionalidades difíciles.
  Si una ya no aplica, se deja con `nota` explicando por qué.
- **No se toca el test para que pase.** Se corrige el código.
- **Una funcionalidad por vez**, y siempre se deja el repositorio en un estado que arranca (`init.ps1` verde) al terminar la sesión.
- **Regresión:** si algo aprobado deja de funcionar, vuelve a `pasa:false` con `nota` y se arregla antes de seguir.
- Nunca `push` a `main`; todo en rama y PR (un PR por cambio).
- Aviso al usuario al cerrar: cuántas funcionalidades pasan (`n/total`), cuál sigue y qué bloquea.

## Anti-patrones (los que este harness existe para evitar)
- Marcar `pasa:true` tras "se ve bien" sin ejecutar el flujo real.
- Hacer varias funcionalidades de golpe y no poder decir cuál rompió qué.
- Dejar la sesión con el entorno roto "para arreglarlo después".
- Reescribir `progress.md` en lugar de agregar: se pierde el hilo.

## Integración con el resto
- **prp:** el PRP define fases y contexto; sus criterios de aceptación se vuelven funcionalidades de la lista.
- **bucle-agentico:** sigue siendo el motor de una sesión; este harness aporta la memoria entre sesiones.
- **scratchpad / precompact:** el estado vivo de la sesión va al scratchpad; el hook PreCompact conserva el hilo si se compacta.
- **subagent-orchestration:** una funcionalidad grande puede repartirse, pero **la bandera `pasa` solo la cambia quien verificó**.
- **jarvis-eval:** si una regla de este método se rompe repetidamente, se agrega una tarea al banco para medirla.

## Comandos útiles
```
node ~/.claude/scripts/harness_guard.mjs            # valida la lista contra git (HEAD)
node ~/.claude/scripts/harness_guard.mjs --base main  # contra otra rama
```
