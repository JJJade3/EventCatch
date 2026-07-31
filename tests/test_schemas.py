import pytest
from pydantic import ValidationError

from eventcatch.schemas import EventRecord, TicketTier


def test_ticket_tier_price_strips_currency_formatting():
    tier = TicketTier(tier_name="door", price="$35.00")
    assert tier.price == 35.0


def test_ticket_tier_price_accepts_numeric():
    tier = TicketTier(tier_name="door", price=35)
    assert tier.price == 35.0


def test_event_record_requires_event_name_and_date():
    with pytest.raises(ValidationError):
        EventRecord(location="Somewhere")


def test_event_record_dump_omits_unset_fields():
    record = EventRecord(event_name="Test", date="Aug 2")
    dumped = record.model_dump(exclude_none=True)
    assert dumped == {"event_name": "Test", "date": "Aug 2"}
