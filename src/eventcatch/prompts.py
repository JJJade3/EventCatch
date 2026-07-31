CATCH_EVENT_TOOL = {
    "name": "catch_event",
    "description": "Record structured event details extracted from a social-media event post.",
    "input_schema": {
        "type": "object",
        "properties": {
            "event_name": {"type": "string", "description": "Event name"},
            "date": {"type": "string", "description": "Event date"},
            "location": {"type": "string", "description": "Event location"},
            "host": {"type": "string", "description": "Event host"},
            "start_time": {"type": "string", "description": "Event start time"},
            "end_time": {"type": "string", "description": "Event end time"},
            "ticket_tiers": {
                "type": "array",
                "description": "All event ticket price tiers",
                "items": {
                    "type": "object",
                    "properties": {
                        "tier_name": {"type": "string", "description": "Ticket tier name"},
                        "price": {"type": "number", "description": "Ticket price"},
                    },
                },
            },
            "registration_link": {"type": "string", "description": "Event registration link"},
        },
        "required": ["event_name", "date"],
    },
}


def build_extraction_prompt(post_text: str) -> str:
    return (
        "Extract event information from this post. For the date field, output "
        "only the month and day (e.g. Aug 2). Do not include the weekday or "
        "year. If a field is not mentioned in the post, omit it directly, do "
        "not guess or use a placeholder.\n\nPost:\n"
        f"{post_text}"
    )
