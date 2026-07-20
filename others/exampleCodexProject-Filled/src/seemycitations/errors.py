from enum import StrEnum


class UserErrorCode(StrEnum):
    RATE_LIMIT = "rate_limit"
    NETWORK = "network"
    NO_MATCHES = "no_matches"
    PDF_UNAVAILABLE = "pdf_unavailable"
    INVALID_PDF = "invalid_pdf"
    UNREADABLE_PDF = "unreadable_pdf"
    EXTRACTION_FAILED = "extraction_failed"


ERROR_ACTIONS: dict[UserErrorCode, str] = {
    UserErrorCode.RATE_LIMIT: "Wait, then retry.",
    UserErrorCode.NETWORK: "Check the connection and retry.",
    UserErrorCode.NO_MATCHES: "Edit the author query.",
    UserErrorCode.PDF_UNAVAILABLE: "Upload a PDF you are authorized to use.",
    UserErrorCode.INVALID_PDF: "Choose a valid PDF within the upload limit.",
    UserErrorCode.UNREADABLE_PDF: "Choose a text-based PDF or another document.",
    UserErrorCode.EXTRACTION_FAILED: "Retry extraction or replace the PDF.",
}
