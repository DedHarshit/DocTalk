from fastapi import APIRouter
from models.chat import ChatRequest, ChatResponse, ChatMessage
from services.ai_service import AIService
from utils.helpers import generate_id, detect_emergency, error_response
from utils.logger import get_logger

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = get_logger("routers.chat")

SYSTEM_PROMPT = """You are DocTalk, a compassionate and knowledgeable medical health navigator AI assistant.

Your role is to:
- Explain medical concepts clearly in plain language
- Help users understand their medicines and dosages
- Help interpret medical reports in understandable terms
- Track and discuss health trends and metrics
- Remind users about medication schedules
- Provide general health education

STRICT RULES — You MUST follow these at all times:
- NEVER diagnose any medical condition
- NEVER prescribe medication or suggest changing doses
- ALWAYS recommend consulting a licensed doctor or healthcare provider
- ALWAYS clarify that your responses are educational only

If the user mentions an emergency (chest pain, stroke, can't breathe, heart attack, overdose, unconscious, anaphylaxis):
- Immediately advise them to call emergency services (112 / 911 / local emergency number)
- Stay calm and supportive
- Provide basic safety instructions while help is on the way

Be warm, empathetic, and helpful."""


def build_messages(system: str, history: list[ChatMessage], user_message: str) -> list[dict]:
    messages = [{"role": "system", "content": system}]
    for h in history:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": user_message})
    return messages


def get_emergency_actions() -> list[str]:
    return [
        "Call emergency services immediately (112 / 911)",
        "Do NOT leave the patient alone",
        "Stay on the line with emergency services",
        "Follow dispatcher instructions",
        "Locate the nearest emergency room",
    ]


def get_standard_actions(message: str) -> list[str]:
    lower = message.lower()
    actions = []
    if any(w in lower for w in ["medicine", "drug", "tablet", "dose"]):
        actions.append("Search our medicine database for more details")
    if any(w in lower for w in ["report", "test", "result", "scan"]):
        actions.append("Upload your report for AI-powered analysis")
    if any(w in lower for w in ["remind", "schedule", "alarm"]):
        actions.append("Set a medication reminder")
    if any(w in lower for w in ["blood", "sugar", "pressure", "weight", "heart"]):
        actions.append("Log this metric in your health tracker")
    actions.append("Consult a healthcare professional for personalised advice")
    return actions


@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    try:
        session_id = request.session_id or generate_id()
        is_emergency = detect_emergency(request.message)

        messages = build_messages(SYSTEM_PROMPT, request.history or [], request.message)
        ai = AIService()
        reply = await ai.generate_with_history(messages)

        suggested_actions = (
            get_emergency_actions() if is_emergency else get_standard_actions(request.message)
        )

        return ChatResponse(
            reply=reply,
            session_id=session_id,
            is_emergency=is_emergency,
            suggested_actions=suggested_actions,
        )

    except Exception as e:
        logger.error(f"/chat/message error: {e}")
        return error_response(str(e), code="CHAT_ERROR")
