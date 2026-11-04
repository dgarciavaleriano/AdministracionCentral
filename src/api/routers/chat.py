import json
from functools import lru_cache
from typing import List, AsyncGenerator
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_core.runnables import Runnable

from api.schema.chat import ChatRequest, Message
from services.ai.llm import InferenceOrchestrator

router = APIRouter()

# Decorador caché last-recently-used. Sin el decorador, get_llm() reconstruye
# el InferenceOrchestrator y parsea el JSON de LLM_PROVIDERS en cada petición HTTP.
# Decorar la función con @lru_cache de la librería estándar functools convierte
# la dependencia en un Singleton en memoria.
@lru_cache
def get_llm() -> Runnable:
    """Instancia el modelo orquestado una única vez en memoria."""
    return InferenceOrchestrator().build_robust_llm()

async def sse_stream_generator(
    messages: List[Message], 
    llm: Runnable
) -> AsyncGenerator[str, None]:
    formatted_messages = [(m.role, m.content) for m in messages]
    
    async for chunk in llm.astream(formatted_messages):
        if chunk.content:
            payload = json.dumps({"text": chunk.content})
            yield f"data: {payload}\n\n"
            
    yield "data: [DONE]\n\n"

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    llm: Runnable = Depends(get_llm)
):
    return StreamingResponse(
        sse_stream_generator(request.messages, llm),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )