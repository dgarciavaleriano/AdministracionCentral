import json
import httpx
from typing import AsyncGenerator, List, Dict, Any

class AsyncApiClient:
    """Cliente HTTP asíncrono dedicado al streaming y operaciones no bloqueantes."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url

    async def stream_chat(self, messages: List[Dict[str, Any]]) -> AsyncGenerator[str, None]:
        url = f"{self.base_url}/chat/stream"
        payload = {"messages": messages}

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            parsed = json.loads(data)
                            if "text" in parsed:
                                yield parsed["text"]
                        except json.JSONDecodeError:
                            continue