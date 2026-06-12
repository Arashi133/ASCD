from sqlalchemy.orm import Session
from app.models.blueprint import DetailedMappingModel, CreateMappingRequest
from fastapi import HTTPException

class MappingService:
    
    @staticmethod
    def save_mapped_result(db: Session, request_data: CreateMappingRequest) -> DetailedMappingModel:
        """C - Lưu trữ kết quả trích xuất đã map hoàn chỉnh vào Database"""
        # Chuyển đổi dữ liệu Pydantic sang cấu trúc lưu trữ của SQLAlchemy
        db_mapping = DetailedMappingModel(
            job_id=request_data.job_id,
            blueprint_name=request_data.blueprint_name,
            mapped_results=[item.model_dump() for item in request_data.mapped_results]
        )
        db.add(db_mapping)
        db.commit()
        db.refresh(db_mapping)
        return db_mapping

    @staticmethod
    def get_mapping_by_job(db: Session, job_id: str) -> DetailedMappingModel:
        """R - Lấy dữ liệu chi tiết theo Job ID phục vụ xuất file JSON"""
        result = db.query(DetailedMappingModel).filter(DetailedMappingModel.job_id == job_id).first()
        if not result:
            raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu map cho Job ID này.")
        return result

    @staticmethod
    def get_all_mappings(db: Session, skip: int = 0, limit: int = 10):
        """R - Lấy danh sách phân trang hiển thị lên Dashboard"""
        return db.query(DetailedMappingModel).offset(skip).limit(limit).all()

    @staticmethod
    def update_mapping(db: Session, mapping_id: str, updated_results: list) -> DetailedMappingModel:
        """U - Cập nhật lại dữ liệu chỉnh sửa (nếu User sửa trên Dashboard)"""
        db_mapping = db.query(DetailedMappingModel).filter(DetailedMappingModel.mapping_id == mapping_id).first()
        if not db_mapping:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi để cập nhật.")
        
        db_mapping.mapped_results = updated_results
        db.commit()
        db.refresh(db_mapping)
        return db_mapping

    @staticmethod
    def delete_mapping(db: Session, mapping_id: str) -> bool:
        """D - Xóa bản ghi khỏi hệ thống"""
        db_mapping = db.query(DetailedMappingModel).filter(DetailedMappingModel.mapping_id == mapping_id).first()
        if not db_mapping:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi để xóa.")
        
        db.delete(db_mapping)
        db.commit()
        return True 