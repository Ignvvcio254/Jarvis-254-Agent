"""Validate that all skills/*/SKILL.md have minimum required frontmatter."""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
REQUIRED_FIELDS = {"name", "description"}


def get_frontmatter_fields(text: str) -> set[str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return set()
    fields = set()
    for line in match.group(1).splitlines():
        if ":" in line:
            fields.add(line.split(":")[0].strip())
    return fields


def test_all_skills_have_frontmatter():
    skill_files = list(SKILLS_DIR.rglob("SKILL.md"))
    assert len(skill_files) > 0, "No SKILL.md files found"
    missing = []
    for skill_file in skill_files:
        text = skill_file.read_text(encoding="utf-8", errors="ignore")
        fields = get_frontmatter_fields(text)
        absent = REQUIRED_FIELDS - fields
        if absent:
            missing.append(f"{skill_file.relative_to(REPO_ROOT)}: missing {absent}")
    assert not missing, "Skills missing frontmatter:\n" + "\n".join(missing[:20])
