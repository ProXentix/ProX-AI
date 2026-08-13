from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.models.registry import registry

@app.get("/v1/models")
async def list_models():
    return JSONResponse(content={"data": registry.get_model_info_list()})

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    model_id = body.get("model", "neurix")
    
    if not messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    last_prompt = messages[-1].get("content", "")

    return StreamingResponse(
        registry.generate_stream(model_id, last_prompt, messages=messages),
        media_type="text/event-stream"
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}
