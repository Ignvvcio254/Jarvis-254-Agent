"""Ensure no real secrets or tokens are committed to the repo.

Uses high-specificity patterns that match real credential formats, not
documentation placeholders like 'your_api_key' or 'example_password'.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# High-specificity patterns — match real credential formats only
SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{36}"),                # GitHub PAT (40 chars total)
    re.compile(r"sk-ant-api03-[A-Za-z0-9\-_]{90,}"),   # Anthropic key (real format)
    re.compile(r"sk-[A-Za-z0-9]{48,}"),                # OpenAI key (real length >=48)
    re.compile(r"AKIA[A-Z0-9]{16}"),                   # AWS access key (fixed format)
    re.compile(r"xoxb-[A-Za-z0-9\-]{50,}"),            # Slack bot token
    re.compile(r"AIza[A-Za-z0-9\-_]{35}"),             # Google API key (fixed length)
]

SKIP_DIRS = {".git", "__pycache__", "quarantine", "upstream", ".venv", "node_modules"}
SKIP_EXTENSIONS = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".db", ".sqlite"}


def iter_text_files():
    for path in REPO_ROOT.rglob("*"):
        if path.is_dir():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix in SKIP_EXTENSIONS:
            continue
        yield path


def test_no_secrets_in_repo():
    hits = []
    for path in iter_text_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, PermissionError):
            continue
        for pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                rel = path.relative_to(REPO_ROOT)
                hits.append(f"{rel}: {match.group()[:16]}…")
    assert not hits, "Real secrets found in repo:\n" + "\n".join(hits[:10])
