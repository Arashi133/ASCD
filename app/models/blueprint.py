import uuid
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.core.database import Base
Base = declarative_base()

# SQLAlchemy Model (Database Table)
class DetailedMappingModel(Base):
    __tablename__ = "line_text_mappings"

    mapping_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), index=True, nullable=False)
    blueprint_name = Column(String(255), nullable=True)
    # Lưu trữ toàn bộ mảng JSON chứa các cặp ống-chữ đã map vị trí không gian
    mapped_results = Column(JSON, nullable=False) 
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Schemas (Data Validation)
class MappingItemSchema(BaseModel):
    line_id: str = Field(..., description="ID của đoạn ống kỹ thuật")
    line_coordinates: List[float] = Field(..., description="Tọa độ [x1, y1, x2, y2] của ống")
    assigned_text: str = Field(..., description="Nội dung chữ kỹ thuật được map vào ống")
    confidence: float = Field(..., description="Độ tin cậy của thuật toán spatial matching")

class CreateMappingRequest(BaseModel):
    job_id: str
    blueprint_name: str
    mapped_results: List[MappingItemSchema]

class MappingResponseSchema(BaseModel):
    mapping_id: str
    job_id: str
    blueprint_name: str
    mapped_results: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True