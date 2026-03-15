import uuid
from datetime import datetime, timezone
from typing import Any


def generate_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def error_response(message: str, code: str = "ERROR", details: Any = None) -> dict:
    return {
        "error": True,
        "message": message,
        "code": code,
        "details": details,
    }


def success_response(data: dict) -> dict:
    return {"error": False, **data}


ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


def validate_file_extension(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_EXTENSIONS


def validate_file_size(size: int) -> bool:
    return size <= MAX_FILE_SIZE_BYTES


EMERGENCY_KEYWORDS = [
    "chest pain",
    "can't breathe",
    "cannot breathe",
    "cant breathe",
    "stroke",
    "unconscious",
    "overdose",
    "anaphylaxis",
    "heart attack",
]


def detect_emergency(text: str) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in EMERGENCY_KEYWORDS)
