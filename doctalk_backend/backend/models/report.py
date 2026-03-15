from pydantic import BaseModel
from typing import Optional


class ReportAnalysisResponse(BaseModel):
    summary: str
    abnormal_values: str
    term_explanations: str
    questions_for_doctor: str
    urgency_level: str
    raw_analysis: str
    file_type: str
    disclaimer: str


class ParsedReportSections(BaseModel):
    summary: str = ""
    abnormal_values: str = ""
    term_explanations: str = ""
    questions_for_doctor: str = ""
    urgency_level: str = "routine"
