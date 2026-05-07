"""Validate that all commands/*.md have a title heading."""
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
COMMANDS_DIR = REPO_ROOT / "commands"


def test_all_commands_have_heading():
    command_files = list(COMMANDS_DIR.glob("*.md"))
    assert len(command_files) > 0, "No command .md files found"
    missing_heading = []
    for cmd_file in command_files:
        text = cmd_file.read_text(encoding="utf-8", errors="ignore")
        if not any(line.startswith("#") for line in text.splitlines()):
            missing_heading.append(str(cmd_file.relative_to(REPO_ROOT)))
    assert not missing_heading, "Commands without heading:\n" + "\n".join(missing_heading)
