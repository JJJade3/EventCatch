import pytest
from pydantic import ValidationError

from eventcatch.extraction import extract_and_clean
from eventcatch.schemas import EventRecord


async def test_extract_and_clean_rejects_empty_text():
    with pytest.raises(ValueError):
        await extract_and_clean("   ")


async def test_extract_and_clean_returns_validated_record(fake_claude):
    fake_claude(
        {
            "event_name": "Sunset Rooftop Yoga",
            "date": "Aug 2",
            "ticket_tiers": [{"tier_name": "early bird", "price": "$25"}],
        }
    )

    record = await extract_and_clean("Sunset Rooftop Yoga Sat Aug 2, 6pm. $25 early bird")

    assert isinstance(record, EventRecord)
    assert record.event_name == "Sunset Rooftop Yoga"
    assert record.ticket_tiers[0].price == 25.0


async def test_extract_and_clean_requires_event_name_and_date(fake_claude):
    fake_claude({"location": "Somewhere"})

    with pytest.raises(ValidationError):
        await extract_and_clean("some post")
