#!/usr/bin/env python3
"""Build question-bank/manifest.json from files in question-bank/questions."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "question-bank" / "manifest.json"
QUESTIONS_DIR = ROOT / "question-bank" / "questions"


def main() -> None:
    if not QUESTIONS_DIR.exists():
        raise SystemExit(f"Questions directory not found: {QUESTIONS_DIR}")

    question_files = sorted(path.name for path in QUESTIONS_DIR.glob("*.json"))

    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    else:
        manifest = {
            "assessmentConfig": {
                "durationMinutes": 15,
                "targetQuestionCount": 30,
            },
            "files": [],
        }

    manifest["files"] = question_files
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {MANIFEST_PATH} with {len(question_files)} file(s).")


if __name__ == "__main__":
    main()
