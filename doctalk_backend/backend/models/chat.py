from pydantic import BaseModel, Field
from typing import Optional


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    history: Optional[list[ChatMessage]] = []


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    is_emergency: bool
    suggested_actions: list[str]
