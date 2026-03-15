import io
from utils.logger import get_logger

logger = get_logger("services.pdf_service")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        import PyPDF2

        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts).strip()
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise ValueError(f"Failed to extract text from PDF: {e}")


REPORT_ANALYSIS_PROMPT = """You are a medical report analyst helping patients understand their health reports in plain language.

Analyze the medical report and provide a structured response with the following sections:

1. SUMMARY: Plain language summary of the report (avoid medical jargon).
2. ABNORMAL_VALUES: List any values that are outside normal ranges, with explanation.
3. TERM_EXPLANATIONS: Explain any medical terms used in the report.
4. QUESTIONS_FOR_DOCTOR: Suggest 3-5 important questions the patient should ask their doctor.
5. URGENCY_LEVEL: Rate the urgency as one of: routine / soon / urgent / emergency, with brief reasoning.

Format your response clearly with these exact section headers.

IMPORTANT: You are providing educational information only. This is not a medical diagnosis. 
Always advise the patient to discuss results with their healthcare provider."""
