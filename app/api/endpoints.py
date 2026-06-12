from fastapi import APIRouter, UploadFile, File, HTTPException, status
import uuid
import os
import shutil
from app.core.config import settings

# Nạp các module hạ tầng của Giai đoạn 1
from app.infrastructure.minio_client import MinIOClient
from app.infrastructure.postgres_db import PostgresDB
from app.infrastructure.kafka_producer import KafkaJobProducer

router = APIRouter()

# Khởi tạo sẵn các kết nối dịch vụ
minio_client = MinIOClient()
db_client = PostgresDB()
kafka_client = KafkaJobProducer()


@router.post("/upload-blueprint", status_code=status.HTTP_202_ACCEPTED,
             summary="Giai đoạn 1: Tiếp nhận bản vẽ & Giao việc ngầm")
async def upload_blueprint(file: UploadFile = File(...)):
    # 1. Kiểm tra định dạng tệp đầu vào
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in [".png", ".jpg", ".jpeg", ".pdf"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hệ thống chỉ chấp nhận định dạng .png, .jpg, .jpeg, .pdf"
        )

    # 2. Lưu tạm file xuống bộ nhớ đệm cục bộ của server
    tmp_file_path = os.path.join(settings.TMP_UPLOAD_DIR, file.filename)
    try:
        with open(tmp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lưu file tạm: {str(e)}")
    finally:
        await file.close()

    # 3. THỰC THI CHUỖI LOGIC GIAI ĐOẠN 1
    # Bước 3.1: Đẩy file thô lên kho MinIO để lấy link S3 dùng chung
    minio_url = await minio_client.upload_blueprint(tmp_file_path, file.filename)

    # Bước 3.2: Tạo mã Job định danh duy nhất (UUID)
    job_id = str(uuid.uuid4())

    # Bước 3.3: Ghi nhận trạng thái 'pending' ban đầu vào PostgreSQL
    await db_client.initialize_job_state(job_id=job_id, minio_url=minio_url)

    # Bước 3.4: Đóng gói lệnh bài bắn thẳng vào hệ thống hàng đợi Kafka
    await kafka_client.push_job_payload(job_id=job_id, minio_url=minio_url)

    # 4. PHẢN HỒI HTTP 202 ACCEPTED (Hệ thống chưa xử lý AI, giải phóng Client ngay lập tức)
    return {
        "status": "Accepted",
        "message": "Đã nhận file bản vẽ thành công! Tiến trình bóc tách đang được xử lý ngầm.",
        "data": {
            "job_id": job_id,
            "storage_url": minio_url,
            "check_status_endpoint": f"/api/v1/tasks/status/{job_id}"
        }
    }