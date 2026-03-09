from enum import Enum
from typing import Optional, Literal, Union
from pydantic import BaseModel, HttpUrl, Field


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class InputType(str, Enum):
    URL = "url"
    TEXT = "text"
    PDF = "pdf"


class Job(BaseModel):
    job_id: str
    status: JobStatus
    input_type: InputType
    url: Optional[str] = None
    text: Optional[str] = None
    pdf_data: Optional[str] = None  # Base64 encoded PDF
    filename: Optional[str] = None
    error: Optional[str] = None


class UrlImportRequest(BaseModel):
    type: Literal["url"] = "url"
    url: HttpUrl


class TextImportRequest(BaseModel):
    type: Literal["text"] = "text"
    text: str = Field(..., min_length=1, description="Plain text recipe content")


class PdfImportRequest(BaseModel):
    type: Literal["pdf"] = "pdf"
    pdf_data: str = Field(..., description="Base64 encoded PDF file")


ImportRequest = Union[UrlImportRequest, TextImportRequest, PdfImportRequest]


class ImportResponse(BaseModel):
    job_id: str
    status: JobStatus
