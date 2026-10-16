#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8000}"

echo "Generating fresh randomized question bank and updating manifest..."
python3 scripts/generate_questions.py

echo "Starting Quant OA mock test on http://localhost:${PORT}"
echo "Press Ctrl+C to stop."

python3 -m http.server "${PORT}"