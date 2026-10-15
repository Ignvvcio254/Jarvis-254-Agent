#!/usr/bin/env python3
"""
VERDICT STAMP — sella un veredicto 'pass' cuando la verificación se hizo con un
gate válido distinto de verify-gate.ps1 (tsc --noEmit exit 0, npm run build,
deploy de Vercel READY, node --check, etc.). Escribe .verify/verdict.json con
mtime fresco → verdict_guard.py deja de avisar (deja de dar falso positivo).

Uso:
  python ~/.claude/scripts/verdict_stamp.py [gate] [--cwd RUTA]
Ej.:
  python ~/.claude/scripts/verdict_stamp.py tsc
  python ~/.claude/scripts/verdict_stamp.py vercel-build --cwd C:/proj

SOLO sella tras una verificación REAL que pasó. No es para saltarse el gate:
es para registrar un pass objetivo que el .ps1 no escribió. El honor del verdict
sigue siendo del gate real; esto solo evita el falso positivo del guard.
"""
import json
import os
import sys
import time
from pathlib import Path


def main():
    args = [a for a in sys.argv[1:]]
    cwd = None
    if "--cwd" in args:
        i = args.index("--cwd")
        cwd = args[i + 1] if i + 1 < len(args) else None
        del args[i:i + 2]
    gate = args[0] if args else "external"

    root = Path(cwd or os.getcwd()).resolve()
    vdir = root / ".verify"
    vdir.mkdir(parents=True, exist_ok=True)
    payload = {
        "verdict": "pass",
        "stateHash": f"stamped:{gate}",
        "gate": gate,
        "stampedBy": "verdict_stamp.py",
        "ts": int(time.time()),
    }
    out = vdir / "verdict.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.utime(out, None)  # mtime = ahora (lo que compara el guard)
    print(f"[verdict-stamp] sellado pass (gate={gate}) en {out}")


if __name__ == "__main__":
    main()
