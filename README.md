# EventCatch

## What this is

EventCatch is a small service that turns a single, informal social-media event
post (Instagram/Twitter-style caption, emojis and all) into structured event
data — name, date, location, host, start/end time, ticket tiers, registration
link — using Claude's tool-use (function calling) to force the model's output
into a fixed JSON schema.

It is a single-endpoint extraction service, not a scraper: it does not fetch
posts itself, has no persistence layer, and takes one post's text in and
returns one JSON object out.

## Architecture

The code is split into three files with a one-directional dependency: both
`app.py` and `eval.py` import from `extractor.py`; `extractor.py` depends on
neither.

- **`extractor.py` — business layer.** Owns the extraction logic: the
  `catch_tool` schema handed to Claude, `analyze()` (calls
  `client.messages.create` with `tool_choice` forced to `catch_event`), and
  `extract_and_clean()` — the public entrypoint, which validates that input
  text isn't empty and post-processes `ticket_tiers` prices via
  `clean_price()` (strips `$`/`,` and casts to `float`). It also has a
  `__main__` block that runs a few hardcoded sample posts concurrently via
  `asyncio.gather`; that's a manual smoke-test, not something either `app.py`
  or `eval.py` uses.
- **`app.py` — service layer.** A thin FastAPI wrapper: one route,
  `POST /extract`, taking `{"text": ...}` and returning
  `extractor.extract_and_clean()`'s output directly as JSON. It registers an
  exception handler that turns `extractor`'s `ValueError` (empty input) into
  an HTTP 400. Anything else the extractor call raises — including
  `anthropic.APIError` — is not caught here and falls through to FastAPI's
  default 500 response. There's no auth, retry, or rate limiting.
- **`eval.py` — eval layer.** A standalone script, run separately from the
  service. It defines a small hand-labeled golden dataset in-file, runs
  `extract_and_clean()` against each example, and does field-by-field
  comparison against the expected output.

## Running locally (uvicorn)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set `ANTHROPIC_API_KEY` in a `.env` file (loaded via `python-dotenv` at the
top of `extractor.py`), then:

```bash
uvicorn app:app --reload --port 8000
```

```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Sunset Rooftop Yoga Sat Aug 2, 6pm @ The Nest rooftop. $25 early bird"}'
```

## Running with Docker

The `Dockerfile` builds from `python:3.11-slim`, installs
`requirements.txt`, copies the repo in, and runs
`uvicorn app:app --host 0.0.0.0 --port 8000` on port 8000.

```bash
docker build -t eventcatch .
docker run --rm -p 8000:8000 --env-file .env eventcatch
```

`ANTHROPIC_API_KEY` is not baked into the image — it must be supplied at
`docker run` time via `--env-file` or `-e`.

## Eval

**Method:** `eval.py` holds a 3-example golden dataset of hand-labeled posts
covering a few different formats (with ticket tiers, without, free entry). For
each example, `extract_and_clean()`'s output is compared field-by-field
against the expected dict: a field counts as correct if it's present in the
output and, after lowercasing/stripping, matches the expected string exactly
(`normalize` + `fields_match` in `eval.py`). Overall accuracy is total correct
fields divided by total expected fields across the whole dataset.

```bash
python eval.py
```

**Result:** Constraining the `date` field's output format in the prompt —
telling the model to emit only "month day" (e.g. `Aug 2`), with no weekday or
year — raised field-level accuracy from 75% to 94% on this golden set. That's
the one prompt change reflected in `extractor.py`'s current `analyze()`
instructions.

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
  they either get force-fit into `tier_name`/`price` or dropped. `clean_price()`
  itself only strips `$` and `,` before calling `float()`, so any other text
  in the price value will raise.
- **`date` is not parsed into a structured or ISO format.** The prompt asks
  for free text in "month day" form (e.g. `Aug 2`) — there's no year, no
  timezone, and no parsing into `datetime`/ISO-8601 anywhere in the pipeline.
  Callers get a string that looks like a date but isn't validated or typed as
  one; parsing it (and inferring the year) is left to the caller.
