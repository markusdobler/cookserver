from enum import Enum
from typing import Optional
from pydantic import BaseModel, HttpUrl


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    job_id: str
    status: JobStatus
    url: Optional[str] = None
    filename: Optional[str] = None
    error: Optional[str] = None


class ImportRequest(BaseModel):
    url: HttpUrl


class ImportResponse(BaseModel):
    job_id: str
    status: JobStatus
