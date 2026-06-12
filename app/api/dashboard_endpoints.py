from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.models.blueprint import MappingResponseSchema, CreateMappingRequest
from app.services.mapping_service import MappingService
from app.core.database import get_db  # Dòng này sẽ hết lỗi sau khi bạn tạo file database.py

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])

@router.post("/mappings", response_model=MappingResponseSchema)
def create_new_mapping(payload: CreateMappingRequest, db: Session = Depends(get_db)):
    return MappingService.save_mapped_result(db=db, request_data=payload)

@router.get("/blueprints", response_model=List[MappingResponseSchema])
def get_dashboard_list(skip: int = Query(0, ge=0), limit: int = Query(10, le=100), db: Session = Depends(get_db)):
    return MappingService.get_all_mappings(db=db, skip=skip, limit=limit)

@router.get("/download-result/{job_id}")
def download_clean_json_file(job_id: str, db: Session = Depends(get_db)):
    mapping_data = MappingService.get_mapping_by_job(db=db, job_id=job_id)
    custom_headers = {"Content-Disposition": f"attachment; filename=result_{job_id}.json"}
    content = {
        "job_id": mapping_data.job_id,
        "blueprint_name": mapping_data.blueprint_name,
        "total_elements": len(mapping_data.mapped_results),
        "data": mapping_data.mapped_results,
        "exported_at": mapping_data.created_at.isoformat()
    }
    return JSONResponse(content=content, headers=custom_headers)