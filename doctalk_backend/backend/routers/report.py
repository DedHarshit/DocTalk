import re
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.ai_service import AIService
from services.pdf_service import extract_text_from_pdf, REPORT_ANALYSIS_PROMPT
from utils.helpers import (
    validate_file_extension,
    validate_file_size,
    error_response,
    MAX_FILE_SIZE_BYTES,
)
from utils.logger import get_logger

router = APIRouter(prefix="/report", tags=["Report"])
logger = get_logger("routers.report")

DISCLAIMER = (
    "This analysis is for educational purposes only. "
    "Please discuss your results with a qualified healthcare provider."
)


def parse_sections(raw: str) -> dict:
    section_keys = {
        "SUMMARY": "summary",
        "ABNORMAL_VALUES": "abnormal_values",
        "TERM_EXPLANATIONS": "term_explanations",
        "QUESTIONS_FOR_DOCTOR": "questions_for_doctor",
        "URGENCY_LEVEL": "urgency_level",
    }

    sections = {v: "" for v in section_keys.values()}

    for heading, key in section_keys.items():
        pattern = rf"{heading}[:\s]*(.*?)(?={'|'.join(section_keys.keys())}|$)"
        match = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
        if match:
            sections[key] = match.group(1).strip()

    # fallback: if parsing failed, put everything in summary
    if not any(sections.values()):
        sections["summary"] = raw

    return sections


@router.post("/analyze")
async def analyze_report(file: UploadFile = File(...)):
    filename = file.filename or ""

    if not validate_file_extension(filename):
        raise HTTPException(
            status_code=400,
            detail=error_response(
                "Invalid file type. Allowed: PDF, JPG, JPEG, PNG.",
                code="INVALID_FILE_TYPE",
            ),
        )

    file_bytes = await file.read()

    if not validate_file_size(len(file_bytes)):
        raise HTTPException(
            status_code=413,
            detail=error_response(
                f"File too large. Max allowed: {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB.",
                code="FILE_TOO_LARGE",
            ),
        )

    ext = filename.rsplit(".", 1)[-1].lower()
    ai = AIService()

    try:
        if ext == "pdf":
            text = extract_text_from_pdf(file_bytes)
            if not text.strip():
                raise HTTPException(
                    status_code=422,
                    detail=error_response("Could not extract text from PDF.", code="PDF_EMPTY"),
                )
            raw_analysis = await ai.analyze_document_text(text, REPORT_ANALYSIS_PROMPT)
            file_type = "pdf"
        else:
            raw_analysis = await ai.analyze_image(file_bytes, REPORT_ANALYSIS_PROMPT)
            file_type = "image"

        sections = parse_sections(raw_analysis)

        return {
            **sections,
            "raw_analysis": raw_analysis,
            "file_type": file_type,
            "disclaimer": DISCLAIMER,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/report/analyze error: {e}")
        raise HTTPException(
            status_code=500,
            detail=error_response(str(e), code="ANALYSIS_ERROR"),
        )
