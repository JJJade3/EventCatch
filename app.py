from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import extractor

app = FastAPI()

class ExtractRequest(BaseModel):
    text: str

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)}
    )

@app.post("/extract")
async def extract_event(request: ExtractRequest):
    analyzed_event = await extractor.extract_and_clean(request.text)
    return analyzed_event