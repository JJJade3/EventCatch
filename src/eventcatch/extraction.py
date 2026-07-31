import logging
import time
from typing import Any

from .client import get_client
from .config import settings
from .prompts import CATCH_EVENT_TOOL, build_extraction_prompt
from .schemas import EventRecord

logger = logging.getLogger(__name__)


async def extract_and_clean(text: str) -> EventRecord:
    if not text or not text.strip():
        raise ValueError("Event information is empty or invalid.")

    start = time.monotonic()
    raw = await _call_claude(text)
    elapsed = time.monotonic() - start
    logger.info("Extraction took %.2fs", elapsed)

    return EventRecord.model_validate(raw)


async def _call_claude(text: str) -> dict[str, Any]:
    client = get_client()
    response = await client.messages.create(
        model=settings.anthropic_model,
        max_tokens=settings.anthropic_max_tokens,
        tools=[CATCH_EVENT_TOOL],
        tool_choice={"type": "tool", "name": CATCH_EVENT_TOOL["name"]},
        messages=[{"role": "user", "content": build_extraction_prompt(text)}],
    )
    logger.info(
        "Tokens - input: %d, output: %d",
        response.usage.input_tokens,
        response.usage.output_tokens,
    )
    return response.content[0].input
