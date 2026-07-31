import time

from dotenv import load_dotenv
load_dotenv()

import asyncio
import anthropic
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


client = anthropic.AsyncAnthropic()

catch_tool = {
    "name": "catch_event",
    "description": "cath the event",
    "input_schema": {
        "type": "object",
        "properties": {
            "event_name": {"type": "string", "description": "Event name"},
            "date": {"type": "string", "description": "Event Date"},
            "location": {"type": "string", "description": "Event Location"},
            "host": {"type": "string", "description": "Event Host"},
            "start_time": {"type": "string", "description": "Event Start Time"},
            "end_time": {"type": "string", "description": "Event End Time"},
            "ticket_tiers": {"type": "array", "description": "All Event Ticket Price Tiers", "items": {"type": "object", "properties": {"tier_name": {"type": "string", "description": "Ticket Tier Name"}, "price": {"type": "number", "description": "Ticket Price"}}}},
            "registration_link": {"type": "string", "description": "Event Registration Link"},

        },
        "required": ["event_name", "date"]
    }
}
event_posts = [
    """Sunset Rooftop Yoga + Chill 🧘‍♀️ Sat Aug 2, 6pm @ The Nest rooftop, 445 Grand Ave. $25 early bird / $35 door. linktr.ee/nestyoga""",
    """📚 Indie Book Swap! Sunday Aug 3, 2-5pm at Grounded Cafe (12 Oak St). Free entry, bring a book take a book ☕""",
    """LATE NIGHT RAMEN POP-UP 🍜 Fri Aug 1 from 9pm till we sell out. Miso Bar, 88 Kent Ave. $18 a bowl, cash only""",
    ""
]


async def extract_and_clean(text):
    if not text or not text.strip():
        raise ValueError("Event information is empty or invalid.")
    start = time.time()      
    response = await analyze(text)
    elapsed = time.time() - start   
    logger.info(f"Time taken to analyze event: {elapsed:.2f} seconds")
    if "ticket_tiers" in response:
        for tier in response["ticket_tiers"]:
            tier["price"] = clean_price(tier["price"])
    return response

def clean_price(raw):
    if isinstance(raw, (int, float)):
        return raw
    
    cleaned = raw.replace("$", "").replace(",", "").strip()
    
    return float(cleaned)

async def analyze(event):
    response = await client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=500,
    tools=[catch_tool],
    tool_choice={"type": "tool", "name": "catch_event"},
    messages=[
        {"role": "user", "content": f"Extract event information from this posts. For the date field, output only the month and day (e.g. Aug 2). Do not include the weekday or year. If a field is not mentioned in the post, omit it directly, do not guess or use placeholder. \n\nPost:\n{event}"}
        
    ])
    logger.info(f"Tokens - input: {response.usage.input_tokens}, output: {response.usage.output_tokens}")
    data = response.content[0].input
    return data

async def main():
    try:
        events = await asyncio.gather(*(analyze(event) for event in event_posts), return_exceptions=True)
        for event in events:
            if (event is None) or (isinstance(event, Exception)):
                print(f"Error occurred while processing event: {event}")
                continue
            if "ticket_tiers" in event:
                for tier in event["ticket_tiers"]:
                    tier["price"] = clean_price(tier["price"])
            for key, value in event.items():
                if isinstance(value, list):
                    print(f"{key}:")
                    for item in value:
                        print(f"  - {item}")
                else:
                    print(key, ":", value)
            print("\n")

    except ValueError as e:
        print(f"Error occurred: {e}")
    except anthropic.APIError as e:
        print(f"API call failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())