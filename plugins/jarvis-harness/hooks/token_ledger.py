#!/usr/bin/env python3
"""
JARVIS TOKEN LEDGER — mide la economía real del harness UPLIFT.

Registra por tarea: modelo usado, dificultad, si el verify-gate pasó a la 1ª,
intentos de repair, y un costo relativo estimado. Sin esto, el "ahorro" del
token-router es teórico. Con esto, jarvis-evolve tiene números para decidir.

Uso:
  # registrar una tarea completada
  python token_ledger.py log --model sonnet --difficulty estandar \
      --gate pass --repairs 0 --task "fix bug en auth"

  # ver el resumen (totales por modelo + ahorro estimado vs todo-Opus)
  python token_ledger.py report

El ledger es un JSONL append-only en ~/.claude/metrics/token_ledger.jsonl
(fuente de verdad local, nunca se reescribe).
"""
import argparse
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Consola Windows: forzar UTF-8 para · → y acentos.
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

LEDGER = Path.home() / ".claude" / "metrics" / "token_ledger.jsonl"

# Costo relativo de salida por 1M tokens (Claude API, referencia 2026).
# El router elige el mínimo suficiente; el ledger cuantifica el ahorro.
COST = {"haiku": 1.25, "gemma": 0.0, "sonnet": 15.0, "opus": 75.0}
DIFFICULTY = {"trivial", "estandar", "complejo"}


def _ensure():
    LEDGER.parent.mkdir(parents=True, exist_ok=True)


def cmd_log(a):
    _ensure()
    model = a.model.lower()
    if model not in COST:
        print(f"[ledger] modelo desconocido: {model} (válidos: {', '.join(COST)})", file=sys.stderr)
        return 1
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "difficulty": a.difficulty,
        "gate": a.gate,                 # pass | fail | none
        "gate_first_try": a.gate == "pass" and a.repairs == 0,
        "repairs": a.repairs,
        "cost_unit": COST[model],       # costo relativo del modelo elegido
        "cost_opus": COST["opus"],      # costo si se hubiera usado Opus a pelo
        "task": a.task or "",
    }
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    saved = COST["opus"] - COST[model]
    print(f"[ledger] +{model} ({a.difficulty}) gate={a.gate} repairs={a.repairs} "
          f"· ahorro vs Opus: {saved:.1f}/1M")
    return 0


def cmd_report(_a):
    if not LEDGER.exists():
        print("[ledger] sin datos todavía. Registra tareas con: token_ledger.py log ...")
        return 0
    rows = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not rows:
        print("[ledger] vacío.")
        return 0
    n = len(rows)
    by_model, gate_ok, first_try, repairs = {}, 0, 0, 0
    cost_real = cost_allopus = 0.0
    for r in rows:
        by_model[r["model"]] = by_model.get(r["model"], 0) + 1
        if r.get("gate") == "pass":
            gate_ok += 1
        if r.get("gate_first_try"):
            first_try += 1
        repairs += r.get("repairs", 0)
        cost_real += r.get("cost_unit", 0)
        cost_allopus += r.get("cost_opus", 0)
    saved_pct = (1 - cost_real / cost_allopus) * 100 if cost_allopus else 0
    print("=== JARVIS TOKEN LEDGER ===")
    print(f"Tareas registradas : {n}")
    print(f"Distribución modelo: " + " · ".join(f"{m}={c}" for m, c in sorted(by_model.items())))
    print(f"Gate pass          : {gate_ok}/{n} ({gate_ok/n*100:.0f}%)")
    print(f"Pass a la 1ª        : {first_try}/{n} ({first_try/n*100:.0f}%)")
    print(f"Reparaciones totales: {repairs}")
    print(f"Costo relativo real : {cost_real:.1f}  (si todo-Opus: {cost_allopus:.1f})")
    print(f"AHORRO ESTIMADO     : {saved_pct:.0f}% vs hacer todo con Opus")
    return 0


def main():
    p = argparse.ArgumentParser(description="Jarvis token ledger — mide la economía del harness")
    sub = p.add_subparsers(dest="cmd", required=True)
    lg = sub.add_parser("log", help="registrar una tarea")
    lg.add_argument("--model", required=True, help="haiku|gemma|sonnet|opus")
    lg.add_argument("--difficulty", default="estandar", choices=sorted(DIFFICULTY))
    lg.add_argument("--gate", default="none", choices=["pass", "fail", "none"])
    lg.add_argument("--repairs", type=int, default=0)
    lg.add_argument("--task", default="")
    lg.set_defaults(func=cmd_log)
    rp = sub.add_parser("report", help="ver resumen y ahorro estimado")
    rp.set_defaults(func=cmd_report)
    args = p.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()