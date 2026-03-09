from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from typing import Union
from ..models.job import (
    ImportRequest, ImportResponse, Job, 
    UrlImportRequest, TextImportRequest, PdfImportRequest,
    InputType
)
from ..services.import_service import ImportService

router = APIRouter(prefix="/api/import", tags=["import"])

# Dependency to get import service (will be set in main.py)
_import_service: ImportService = None


def get_import_service() -> ImportService:
    if _import_service is None:
        raise HTTPException(status_code=500, detail="Import service not initialized")
    return _import_service


def set_import_service(service: ImportService):
    global _import_service
    _import_service = service


@router.post("", response_model=ImportResponse)
async def create_import(
    request: Union[UrlImportRequest, TextImportRequest, PdfImportRequest],
    background_tasks: BackgroundTasks,
    service: ImportService = Depends(get_import_service)
):
    """Create a new import job"""
    # Create job based on request type
    if isinstance(request, UrlImportRequest):
        job = service.create_job(
            input_type=InputType.URL,
            url=str(request.url)
        )
    elif isinstance(request, TextImportRequest):
        job = service.create_job(
            input_type=InputType.TEXT,
            text=request.text
        )
    elif isinstance(request, PdfImportRequest):
        job = service.create_job(
            input_type=InputType.PDF,
            pdf_data=request.pdf_data
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid request type")
    
    # Add background task to process import
    background_tasks.add_task(service.process_import, job.job_id)
    
    return ImportResponse(job_id=job.job_id, status=job.status)


@router.get("/{job_id}", response_model=Job)
async def get_import_status(
    job_id: str,
    service: ImportService = Depends(get_import_service)
):
    """Get the status of an import job"""
    job = service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job
