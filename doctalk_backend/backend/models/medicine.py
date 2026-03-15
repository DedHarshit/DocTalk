from pydantic import BaseModel, Field
from typing import Optional


class MedicineQuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class MedicineQuestionResponse(BaseModel):
    answer: str
    sources: list
    confidence: str
    disclaimer: str


class MedicineInteractionRequest(BaseModel):
    medicines: list[str] = Field(..., min_length=2)


class MedicineInteractionResponse(BaseModel):
    medicines: list[str]
    pairs_analyzed: list[dict]
    analysis: str
    disclaimer: str


class SearchResult(BaseModel):
    id: str
    content: str
    distance: Optional[float] = None
    relevance: str
