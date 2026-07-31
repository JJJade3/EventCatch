from pydantic import BaseModel, field_validator


class ExtractRequest(BaseModel):
    text: str


class TicketTier(BaseModel):
    tier_name: str
    price: float

    @field_validator("price", mode="before")
    @classmethod
    def parse_price(cls, value: float | str) -> float:
        if isinstance(value, (int, float)):
            return value
        cleaned = value.replace("$", "").replace(",", "").strip()
        return float(cleaned)


class EventRecord(BaseModel):
    event_name: str
    date: str
    location: str | None = None
    host: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    ticket_tiers: list[TicketTier] | None = None
    registration_link: str | None = None
