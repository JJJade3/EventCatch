"""Manual smoke test: runs a few hardcoded sample posts through the extractor concurrently."""

import asyncio

from eventcatch.extraction import extract_and_clean
from eventcatch.logging_config import configure_logging

SAMPLE_POSTS = [
    "Sunset Rooftop Yoga + Chill \U0001f9d8‍♀️ Sat Aug 2, 6pm @ The Nest rooftop, 445 Grand Ave. $25 early bird / $35 door. linktr.ee/nestyoga",
    "\U0001f4da Indie Book Swap! Sunday Aug 3, 2-5pm at Grounded Cafe (12 Oak St). Free entry, bring a book take a book ☕",
    "LATE NIGHT RAMEN POP-UP \U0001f35c Fri Aug 1 from 9pm till we sell out. Miso Bar, 88 Kent Ave. $18 a bowl, cash only",
    "",
]


async def main() -> None:
    configure_logging()
    results = await asyncio.gather(
        *(extract_and_clean(post) for post in SAMPLE_POSTS), return_exceptions=True
    )
    for result in results:
        if isinstance(result, Exception):
            print(f"Error occurred while processing event: {result}")
            continue
        for field_name, value in result.model_dump(exclude_none=True).items():
            if isinstance(value, list):
                print(f"{field_name}:")
                for item in value:
                    print(f"  - {item}")
            else:
                print(field_name, ":", value)
        print()


if __name__ == "__main__":
    asyncio.run(main())
