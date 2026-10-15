#!/usr/bin/env python3
"""
JARVIS CORRECTION DETECTOR — automates the correction-detection step of the
scratchpad skill (UserPromptSubmit hook).

If the user's message looks like a correction ("no, actually", "I already told
you", "ya te dije", "está mal"...), it injects a reminder to extract the
problem→solution pattern and save it to memory instead of letting it die in the
conversation. Knowledge that only lives in a conversation is dead knowledge.

Usage (settings.json UserPromptSubmit):
  { "type": "command", "command": "python ~/.claude/scripts/correction_detector.py" }
"""
import json
import re
import sys

PATTERNS = [
    # Spanish
    r"\bno,?\s+(mejor|en realidad|así no|eso no)\b",
    r"\b(está|esta)\s+mal\b",
    r"\bno\s+es\s+(así|asi|correcto|lo que)\b",
    r"\bte\s+equivocaste\b",
    r"\bya\s+te\s+(dije|hab[ií]a dicho)\b",
    r"\botra\s+vez\s+(lo mismo|el mismo)\b",
    r"\b(recuerda|acordate|acu[eé]rdate)\s+que\b",
    r"\bno\s+(hagas|vuelvas a|quiero que)\b",
    r"\b(siempre|nunca)\s+(haz|hagas|uses|pongas)\b",
    r"\bte\s+(dije|ped[ií])\s+que\b",
    r"\beso\s+(no era|no es lo que)\b",
    r"\bmal\s+ah[ií]\b",
    # English
    r"\bno,?\s+(actually|instead|that's not|not like that)\b",
    r"\b(that's|that is|this is)\s+(wrong|not what i)\b",
    r"\bi\s+(already\s+)?(told|asked)\s+you\b",
    r"\byou\s+(got it wrong|were wrong|made a mistake)\b",
    r"\b(again|once more)\s+the\s+same\b",
    r"\b(remember|don't forget)\s+that\b",
    r"\b(don't|do not|stop)\s+(do|doing|use|using|add|adding)\b",
    r"\b(always|never)\s+(do|use|add|put|write)\b",
]


def extract_text(prompt: str) -> str:
    m = re.search(r"<channel[^>]*>(.*?)</channel>", prompt, re.DOTALL)
    return (m.group(1) if m else prompt).strip()


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
    except Exception:
        sys.exit(0)
    prompt = extract_text(data.get("prompt", "")).lower()
    if not prompt:
        sys.exit(0)

    if not any(re.search(p, prompt) for p in PATTERNS):
        sys.exit(0)

    msg = (
        "[correction-detector] Possible CORRECTION from the user. "
        "Before continuing, apply the scratchpad skill: "
        "1) extract the problem->solution pattern (what went wrong, what should have been done); "
        "2) save it where it belongs (memory as feedback if it is about how to work, "
        "agent-uplift antipatterns/<model> if it is about a worker, cerebro if it is a session decision); "
        "3) confirm in one line, in the user's language: 'Noted: <rule>'. "
        "Never leave a correction only in the conversation."
    )
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": msg}
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
