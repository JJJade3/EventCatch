from dotenv import load_dotenv
load_dotenv()

import anthropic

client = anthropic.Anthropic()

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
event_info = """
Sunset Rooftop Yoga + Chill 🧘‍♀️🌅
this Saturday (Aug 2) come thru around 6pm, we'll go till sunset 8pm
@ The Nest rooftop, 445 Grand Ave, 4th floor
$25 early bird / $35 at the door / $1,200 for a private rooftop yoga session for you and your friends (up to 10 ppl)
DM to reserve or grab tickets → linktr.ee/nestyoga
"""
def clean_price(raw):
    if isinstance(raw, (int, float)):
        return raw
    
    cleaned = raw.replace("$", "").replace(",", "").strip()
    
    return float(cleaned)

def analyze(event):
    response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=500,
    tools=[catch_tool],
    tool_choice={"type": "tool", "name": "catch_event"},
    messages=[
        {"role": "user", "content": f"Extract event information from this posts. If a field is not mentioned in the post, omit it directly, do not guess or use placeholder.\n\nPost:\n{event}"}
    ])
    data = response.content[0].input
    return data

def main():
    event = analyze(event_info)
    if "ticket_tiers" in event:
        for tier in event["ticket_tiers"]:
            tier["price"] = clean_price(tier["price"])

    for key, value in event.items():
        if isinstance(value, list):
            print(f"{key}:")
            for item in value:
                print(f"  - {item}")
        else:print(key, ":", value)
main()