# EventCatch

## What this is

EventCatch is a small service that turns a single, informal social-media event
post (Instagram/Twitter-style caption, emojis and all) into structured event
data — name, date, location, host, start/end time, ticket tiers, registration
link — using Claude's tool-use (function calling) to force the model's output
into a fixed schema.

It is a single-endpoint extraction service, not a scraper: it does not fetch
posts itself, has no persistence layer, and takes one post's text in and
returns one JSON object out.

## Layout

```
src/eventcatch/
  config.py           Settings loaded from env / .env (pydantic-settings)
  schemas.py           Pydantic models: ExtractRequest, EventRecord, TicketTier
  prompts.py            Tool schema + prompt handed to Claude
  client.py               Anthropic client factory
  extraction.py       Core extraction logic: extract_and_clean()
  api.py                     FastAPI app, single POST /extract route
  logging_config.py    Shared logging setup

tests/                pytest suite (unit + API), Anthropic client mocked
eval/                  Golden-dataset accuracy check against the live API
scripts/               Manual smoke test against the live API
```

Dependency direction is one-way: `api.py` and `eval/run_eval.py` and
`scripts/smoke_test.py` all depend on `extraction.py`; `extraction.py` depends
on `config.py`, `client.py`, `prompts.py`, and `schemas.py`, and on nothing
above it.

- **`extraction.py` — business layer.** `extract_and_clean()` is the public
  entrypoint: it validates that input text isn't empty, calls Claude with
  `tool_choice` forced to `catch_event`, and validates the tool's output
  against `EventRecord`. Ticket price parsing (stripping `$`/`,`, casting to
  `float`) lives on `TicketTier` as a Pydantic field validator, so any code
  that constructs a `TicketTier` gets it for free.
- **`api.py` — service layer.** A thin FastAPI wrapper: one route,
  `POST /extract`, taking `{"text": ...}` and returning an `EventRecord`
  (fields the model omitted are dropped from the response, not returned as
  `null`). It registers an exception handler that turns `ValueError` (empty
  input) into an HTTP 400. Anything else — including `anthropic.APIError` or
  a schema-validation failure — is not caught here and falls through to
  FastAPI's default 500 response. There's no auth, retry, or rate limiting.
- **`eval/run_eval.py` — eval layer.** A standalone script, run separately
  from the service. It loads a small hand-labeled golden dataset from
  `eval/golden_dataset.json`, runs `extract_and_clean()` against each
  example, and does field-by-field comparison against the expected output.
- **`scripts/smoke_test.py`** runs a few hardcoded sample posts through the
  extractor concurrently and prints the results — a manual check against the
  live API, not part of the test suite.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY` (loaded via
`python-dotenv`/`pydantic-settings` from `config.py`).

## Running locally (uvicorn)

```bash
uvicorn eventcatch.api:app --reload --port 8000
```

```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Sunset Rooftop Yoga Sat Aug 2, 6pm @ The Nest rooftop. $25 early bird"}'
```

## Running with Docker

The `Dockerfile` builds from `python:3.11-slim`, installs the package from
`pyproject.toml`, and runs `uvicorn eventcatch.api:app --host 0.0.0.0 --port
8000` on port 8000.

```bash
docker build -t eventcatch .
docker run --rm -p 8000:8000 --env-file .env eventcatch
```

`ANTHROPIC_API_KEY` is not baked into the image — it must be supplied at
`docker run` time via `--env-file` or `-e`.

## Tests

```bash
pytest
```

Unit and API tests mock the Anthropic client (see `tests/conftest.py`), so
they run offline and don't consume API credits or require an API key.

## Eval

**Method:** `eval/golden_dataset.json` holds a 3-example golden dataset of
hand-labeled posts covering a few different formats (with ticket tiers,
without, free entry). For each example, `extract_and_clean()`'s output is
compared field-by-field against the expected dict: a field counts as correct
if it's present in the output and, after lowercasing/stripping, matches the
expected string exactly. Overall accuracy is total correct fields divided by
total expected fields across the whole dataset. This makes a live call to the
Anthropic API for each example, so it needs `ANTHROPIC_API_KEY` set.

```bash
python eval/run_eval.py
```

**Result:** Constraining the `date` field's output format in the prompt —
telling the model to emit only "month day" (e.g. `Aug 2`), with no weekday or
year — raised field-level accuracy from 75% to 94% on this golden set. That's
the one prompt change reflected in `prompts.py`'s current extraction prompt.

This is a 3-post, hand-picked golden set, so treat 75%→94% as a directional
result showing that change helped, not as a statistically robust accuracy
benchmark. It's useful for catching regressions in field naming/formatting as
the prompt or schema changes, not for making general accuracy claims about
the extractor.

## Known limitations

- **`ticket_tiers` doesn't model non-ticket pricing well.** The schema
  (`tier_name` + numeric `price`) is shaped for classic ticket tiers like
  "early bird" / "door". Per-unit pricing (e.g. "$18 a bowl"), free/donation
  entry, price ranges, and non-USD currency have no clean representation —
  they either get force-fit into `tier_name`/`price` or dropped.
  `TicketTier.price`'s validator only strips `$` and `,` before calling
  `float()`, so any other text in the price value will raise a validation
  error.
- **`date` is not parsed into a structured or ISO format.** The prompt asks
  for free text in "month day" form (e.g. `Aug 2`) — there's no year, no
  timezone, and no parsing into `datetime`/ISO-8601 anywhere in the pipeline.
  Callers get a string that looks like a date but isn't validated or typed as
  one; parsing it (and inferring the year) is left to the caller.
