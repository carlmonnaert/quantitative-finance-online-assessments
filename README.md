# Quant Trading / Quant Research OA Mock

This repo contains a lightweight HackerRank-style assessment mimic for quant online assessments.

- Session length: **15 minutes**
- Question target: **30 questions**
- Question source: JSON files from `question-bank/questions/`

No real questions are included yet.

## Quick start

From the repo root:

```bash
python3 -m http.server 8000
```

or:

```bash
./start_test.sh
```

Optional custom port:

```bash
./start_test.sh 9000
```

Open:

- `http://localhost:8000`

> Do not open `index.html` directly as a `file://` URL; `fetch` for JSON files requires a local server.

## Question bank structure

```text
question-bank/
  manifest.json
  questions/
    *.json
  templates/
    question-set.template.json
```

### 1) Add question files

Create one or more files in `question-bank/questions/`.

Each file must be JSON with this top-level shape:

```json
{
  "questions": [
    {
      "id": "unique-id",
      "type": "mcq",
      "title": "Short title",
      "prompt": "Full question prompt",
      "options": [
        { "value": "A", "label": "Option A" },
        { "value": "B", "label": "Option B" },
        { "value": "C", "label": "Option C" },
        { "value": "D", "label": "Option D" }
      ]
    },
    {
      "id": "unique-id-2",
      "type": "numeric",
      "title": "Numeric question title",
      "prompt": "Question prompt"
    },
    {
      "id": "unique-id-3",
      "type": "text",
      "title": "Free-text question title",
      "prompt": "Question prompt"
    }
  ]
}
```

Supported `type` values:

- `mcq` (requires `options`)
- `numeric`
- `text`

### 2) Build/update manifest

Run:

```bash
python3 scripts/build_manifest.py
```

This scans `question-bank/questions/*.json` and writes the file list into `question-bank/manifest.json`.

### 3) Configure assessment settings

In `question-bank/manifest.json`:

```json
{
  "assessmentConfig": {
    "durationMinutes": 15,
    "targetQuestionCount": 30
  },
  "files": ["file1.json", "file2.json"]
}
```

- `durationMinutes`: total timer duration.
- `targetQuestionCount`: number of questions sampled from all loaded questions.

If fewer than 30 questions are available, the app uses all loaded questions.

## Current behavior

- Randomizes the loaded question pool.
- Selects up to `targetQuestionCount` questions.
- Shows question index buttons (answered/current states).
- Supports previous/next navigation.
- Auto-submits when timer reaches zero.
- Manual submission button included.

## Files

- `index.html`: main assessment UI
- `styles.css`: styling
- `app.js`: loader, timer, state, rendering, submission
- `scripts/build_manifest.py`: manifest generation helper
- `question-bank/templates/question-set.template.json`: authoring template
