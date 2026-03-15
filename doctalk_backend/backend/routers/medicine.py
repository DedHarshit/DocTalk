from fastapi import APIRouter, Query
from models.medicine import (
    MedicineQuestionRequest,
    MedicineQuestionResponse,
    MedicineInteractionRequest,
    MedicineInteractionResponse,
)
from services.rag_service import ask_medicine_question, search_medicines, analyze_interactions
from utils.helpers import error_response
from utils.logger import get_logger

router = APIRouter(prefix="/medicine", tags=["Medicine"])
logger = get_logger("routers.medicine")


@router.post("/ask", response_model=MedicineQuestionResponse)
async def ask_medicine(request: MedicineQuestionRequest):
    try:
        result = await ask_medicine_question(request.question)
        return MedicineQuestionResponse(**result)
    except Exception as e:
        logger.error(f"/medicine/ask error: {e}")
        return error_response(str(e), code="MEDICINE_ASK_ERROR")


@router.post("/interactions", response_model=MedicineInteractionResponse)
async def check_interactions(request: MedicineInteractionRequest):
    try:
        result = await analyze_interactions(request.medicines)
        return MedicineInteractionResponse(**result)
    except Exception as e:
        logger.error(f"/medicine/interactions error: {e}")
        return error_response(str(e), code="INTERACTION_ERROR")


@router.get("/search")
async def search_medicine(q: str = Query(..., min_length=1, description="Search query")):
    try:
        results = await search_medicines(q, n=3)
        return {
            "query": q,
            "results": results,
            "count": len(results),
        }
    except Exception as e:
        logger.error(f"/medicine/search error: {e}")
        return error_response(str(e), code="SEARCH_ERROR")
