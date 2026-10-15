import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))
from destructive_guard import evaluar, evaluar_herramienta  # noqa: E402

PREGUNTA = [
    "rm -rf datos",
    "rm -r ./clientes",
    "rm -fr ~/Documents/GitHub/MyProject/datos",
    "Remove-Item -Recurse -Force datos",
    "Remove-Item datos -Recurse",
    "rmdir /s /q datos",
    "del /s /q datos",
    "git clean -fd",
    "git reset --hard HEAD~3",
    "cd x && rm -rf datos && echo hecho",
    "rm -rf node_modules && git reset --hard",  # lo desechable NO exime a git destructivo
]
PASA = [
    "ls -la",
    "rm archivo.txt",                       # borrar UN archivo no es borrado masivo
    "rm -rf node_modules",
    "rm -rf .next dist",
    'D=$(mktemp -d); cd "$D"; rm -rf "$D"',
    "rm -rf /tmp/algo",
    "Remove-Item -Recurse -Force $env:TEMP\\prueba",
    "rm -rf __pycache__",
    "git status",
    "git diff --stat",
    "echo 'rm -rf nada' > /dev/null",  # texto, no comando... (heurística: se acepta el falso positivo si aparece)
]


class PruebasGuardia(unittest.TestCase):
    def test_pregunta(self):
        for c in PREGUNTA:
            self.assertIsNotNone(evaluar(c), f"debía preguntar: {c}")

    def test_pasa(self):
        for c in PASA[:-1]:
            self.assertIsNone(evaluar(c), f"no debía preguntar: {c}")

    def test_hook_de_extremo_a_extremo(self):
        ruta = str(Path(__file__).parent.parent / "hooks" / "destructive_guard.py")
        r = subprocess.run([sys.executable, ruta], input=json.dumps({"tool_input": {"command": "rm -rf datos"}}).encode(), capture_output=True)
        salida = json.loads(r.stdout.decode("utf-8"))
        self.assertEqual(salida["hookSpecificOutput"]["permissionDecision"], "ask")
        r2 = subprocess.run([sys.executable, ruta], input=json.dumps({"tool_input": {"command": "ls"}}).encode(), capture_output=True)
        self.assertEqual(r2.stdout, b"")

    def test_mcp_riesgo(self):
        for n in ["mcp__vercel__delete_project", "mcp__vercel__buy_domain", "mcp__github-git__merge_pull_request", "mcp__mem0__delete_all_memories", "mcp__supabase-tryvex__reset_branch"]:
            self.assertIsNotNone(evaluar_herramienta(n), n)
        for n in ["mcp__vercel__list_projects", "mcp__plugin_discord_discord__reply", "mcp__github-git__get_issue", "mcp__vercel__get_deployment", "Bash"]:
            self.assertIsNone(evaluar_herramienta(n), n)

    def test_modo_auto_deniega_y_default_pregunta(self):
        ruta = str(Path(__file__).parent.parent / "hooks" / "destructive_guard.py")
        def correr(modo):
            r = subprocess.run([sys.executable, ruta], input=json.dumps({"tool_name": "Bash", "permission_mode": modo, "tool_input": {"command": "rm -rf datos"}}).encode(), capture_output=True)
            return json.loads(r.stdout.decode("utf-8"))["hookSpecificOutput"]["permissionDecision"]
        self.assertEqual(correr("auto"), "deny")
        self.assertEqual(correr("bypassPermissions"), "deny")
        self.assertEqual(correr("default"), "ask")
        self.assertEqual(correr("acceptEdits"), "ask")

    def test_falla_abierto(self):
        ruta = str(Path(__file__).parent.parent / "hooks" / "destructive_guard.py")
        r = subprocess.run([sys.executable, ruta], input=b"esto no es json", capture_output=True)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, b"")


if __name__ == "__main__":
    unittest.main()
