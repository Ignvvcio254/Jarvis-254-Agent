"""Skill curator — adopts the NousResearch/hermes-agent curator.py pattern.

Manages lifecycle of skills in skills/ directory:
  active   → skill is current and usable
  stale    → skill has not been modified in > stale_days
  archived → skill moved to skills/_archived/ (never deleted)

Invariants (mirroring Hermes curator.py):
  - Only touches skills that declare `pinned: false` (or no pinned field).
  - Archives instead of deleting — always recoverable.
  - Respects `pinned: true` in frontmatter — never touched.
  - Does not use access-frequency as a criterion (avoids popularity bias).

Usage:
    from pathlib import Path
    from jarvis_core.skill_curator import SkillCurator

    curator = SkillCurator(repo_root=Path("."))
    report = curator.run(dry_run=True)
    print(report.summary())
    for entry in report.entries:
        print(entry.action, entry.skill, entry.reason)
"""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_FIELD_RE = re.compile(r"^(\w[\w\-]*):\s*(.*)$", re.MULTILINE)

# Skills always protected regardless of their frontmatter
_ALWAYS_PINNED = {"antigravity-bridge", "primer", "prp", "bucle-agentico", "autoresearch"}


@dataclass
class CurationEntry:
    skill: str
    action: str      # "keep" | "mark_stale" | "archive"
    reason: str
    dry_run: bool = True


@dataclass
class CurationReport:
    entries: list[CurationEntry] = field(default_factory=list)
    archived: int = 0
    marked_stale: int = 0
    kept: int = 0

    def add(self, entry: CurationEntry) -> None:
        self.entries.append(entry)
        if entry.action == "archive":
            self.archived += 1
        elif entry.action == "mark_stale":
            self.marked_stale += 1
        else:
            self.kept += 1

    def summary(self) -> str:
        suffix = " [DRY RUN]" if self.entries and self.entries[0].dry_run else ""
        return (
            f"Curation complete — "
            f"kept: {self.kept}, stale: {self.marked_stale}, archived: {self.archived}{suffix}"
        )


class SkillCurator:
    """Lifecycle manager for skills/*/SKILL.md files."""

    def __init__(
        self,
        repo_root: Path,
        stale_days: int = 60,
        archive_days: int = 120,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.skills_dir = self.repo_root / "skills"
        self.archive_dir = self.skills_dir / "_archived"
        self.stale_days = stale_days
        self.archive_days = archive_days

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, dry_run: bool = True) -> CurationReport:
        """Evaluate all skills and apply transitions. Returns a CurationReport."""
        report = CurationReport()
        for skill_file in sorted(self.skills_dir.rglob("SKILL.md")):
            if "_archived" in skill_file.parts:
                continue
            skill_name = skill_file.parent.name
            meta = self._parse_frontmatter(skill_file)
            entry = self._evaluate(skill_name, skill_file, meta, dry_run)
            report.add(entry)
            if not dry_run:
                if entry.action == "archive":
                    self._archive(skill_file, skill_name)
                elif entry.action == "mark_stale":
                    self._set_state(skill_file, "stale")
        return report

    def status(self) -> dict[str, list[str]]:
        """Return {state: [skill_names]} for all skills."""
        result: dict[str, list[str]] = {
            "active": [], "stale": [], "archived": [], "unknown": []
        }
        for skill_file in self.skills_dir.rglob("SKILL.md"):
            name = skill_file.parent.name
            if "_archived" in skill_file.parts:
                result["archived"].append(name)
                continue
            meta = self._parse_frontmatter(skill_file)
            state = meta.get("state", "active")
            bucket = state if state in result else "unknown"
            result[bucket].append(name)
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_frontmatter(self, path: Path) -> dict[str, str]:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return {}
        match = _FRONTMATTER_RE.match(text)
        if not match:
            return {}
        return {m.group(1): m.group(2).strip() for m in _FIELD_RE.finditer(match.group(1))}

    def _is_pinned(self, skill_name: str, meta: dict) -> bool:
        if skill_name in _ALWAYS_PINNED:
            return True
        return meta.get("pinned", "false").lower() == "true"

    def _days_since_modified(self, path: Path) -> float:
        mtime = path.stat().st_mtime
        return (datetime.now(timezone.utc).timestamp() - mtime) / 86400

    def _evaluate(
        self,
        skill_name: str,
        skill_file: Path,
        meta: dict,
        dry_run: bool,
    ) -> CurationEntry:
        if self._is_pinned(skill_name, meta):
            return CurationEntry(skill_name, "keep", "pinned", dry_run)

        days_old = self._days_since_modified(skill_file)
        current_state = meta.get("state", "active")

        if days_old >= self.archive_days and current_state == "stale":
            return CurationEntry(
                skill_name, "archive", f"{days_old:.0f}d stale → archive", dry_run
            )
        if days_old >= self.stale_days and current_state == "active":
            return CurationEntry(
                skill_name, "mark_stale", f"{days_old:.0f}d since last modified", dry_run
            )
        return CurationEntry(
            skill_name, "keep", f"{days_old:.0f}d old, state={current_state}", dry_run
        )

    def _archive(self, skill_file: Path, skill_name: str) -> None:
        dest_dir = self.archive_dir / skill_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(skill_file.parent), str(dest_dir))

    def _set_state(self, skill_file: Path, state: str) -> None:
        try:
            text = skill_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return
        if _FRONTMATTER_RE.match(text):
            if re.search(r"^state:", text, re.MULTILINE):
                text = re.sub(r"^state:.*$", f"state: {state}", text, flags=re.MULTILINE)
            else:
                text = re.sub(
                    r"(^---\s*\n.*?\n)(---)",
                    lambda m: m.group(1) + f"state: {state}\n" + m.group(2),
                    text,
                    count=1,
                    flags=re.DOTALL,
                )
        else:
            text = f"---\nstate: {state}\n---\n\n" + text
        skill_file.write_text(text, encoding="utf-8")
