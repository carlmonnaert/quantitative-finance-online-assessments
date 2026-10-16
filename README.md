# Quant Trading / Quant Research OA Mock

This repo contains a lightweight HackerRank-style assessment mimic for quant online assessments.

- Session length: **15 minutes**
- Questions served per run: **30**
- Question source: JSON files listed in `question-bank/manifest.json`

The project currently includes generated question sets across:

- Linear Algebra & Calculus
- Probability & Statistics
- Coding & Algorithms
- Machine Learning

Each run serves a 30-question paper with a fixed layout:

- Complete-answer slots (numeric/text): Q4, Q11, Q12, Q16, Q21, Q22, Q25
- All other slots: MCQ

## Quick start

From the repo root:

```bash
./start_test.sh
```

What this does:

1. Regenerates question files and updates `question-bank/manifest.json`
2. Starts a local server

Then open:

- `http://localhost:8000`

Optional custom port:

```bash
./start_test.sh 9000
```

Then open `http://localhost:9000`.

If you want to serve the current question files without regenerating:

```bash
python3 -m http.server 8000
```

> Do not open `index.html` as `file://...`; JSON loading requires HTTP.

## Question bank layout

```text
question-bank/
  manifest.json
  questions/
    coding_algorithms.json
    linear_algebra_calculus.json
    machine_learning.json
    probability_statistics.json
  templates/
    question-set.template.json
```

## Question JSON format

Each question file uses this top-level shape:

```json
{
  "questions": [
    {
      "id": "unique-id",
      "type": "mcq",
      "title": "Short title",
      "prompt": "Question prompt",
      "options": [
        { "value": "A", "label": "Option A" },
        { "value": "B", "label": "Option B" },
        { "value": "C", "label": "Option C" },
        { "value": "D", "label": "Option D" }
      ],
      "answer": "B",
      "explanation": "Optional explanation"
    },
    {
      "id": "unique-id-2",
      "type": "numeric",
      "title": "Numeric question title",
      "prompt": "Question prompt",
      "answer": "0.73"
    },
    {
      "id": "unique-id-3",
      "type": "text",
      "title": "Text question title",
      "prompt": "Question prompt",
      "answer": "arbitrage"
    }
  ]
}
```

Supported `type` values:

- `mcq` (requires `options`)
- `numeric`
- `text`

Scoring notes:

- `mcq` and `text` are case-insensitive exact string matches.
- `numeric` accepts small tolerance (`±1e-4`).

## How to add or maintain questions

### Option A: Regenerate dynamic banks (recommended)

```bash
python3 scripts/generate_questions.py
```

This rewrites all topic files in `question-bank/questions/` and refreshes `question-bank/manifest.json`.

### Option B: Add your own files manually

1. Create one or more `.json` files in `question-bank/questions/`
2. Keep the format shown above
3. Update the manifest file list:

```bash
python3 scripts/build_manifest.py
```

`build_manifest.py` scans `question-bank/questions/*.json` and updates `manifest.json` with discovered filenames.

## Runtime behavior

- Loads all files listed in `manifest.json`
- Deduplicates by `id` before selection
- Splits pool into `mcq` and complete-answer (`numeric`/`text`) buckets
- Fills a fixed 30-slot structure (7 complete-answer slots, 23 MCQ slots)
- Falls back across buckets if one bucket is exhausted
- Shows navigation grid with answered/current states
- Supports previous/next and direct question jump
- Auto-submits when timer expires
- Displays submission summary including score
- Shows per-question report with result, points, your answer, correct answer, and explanation

## Main files

- `index.html`: assessment UI structure
- `styles.css`: interface styling
- `app.js`: loader, timer, rendering, scoring
- `start_test.sh`: generate + serve launcher
- `scripts/generate_questions.py`: topic-bank generator + manifest updater
- `scripts/build_manifest.py`: manifest-only updater for manual files
