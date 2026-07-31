from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .extraction import extract_and_clean
from .logging_config import configure_logging
from .schemas import EventRecord, ExtractRequest

configure_logging()

app = FastAPI(title="EventCatch")


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.post("/extract", response_model=EventRecord, response_model_exclude_none=True)
async def extract_event(request: ExtractRequest) -> EventRecord:
    return await extract_and_clean(request.text)
