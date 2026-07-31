from fastapi import FastAPI
from pydantic import BaseModel
import extractor

app = FastAPI()

class ExtractRequest(BaseModel):
    text: str


@app.post("/extract")
async def extract_event(request: ExtractRequest):
    analyzed_event = await extractor.extract_and_clean(request.text)
    return analyzed_event