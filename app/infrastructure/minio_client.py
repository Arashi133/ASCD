import os
import time

class MinIOClient:
    def __init__(self):
        self.bucket_name = "raw-images"

    async def upload_blueprint(self, local_file_path: str, filename: str) -> str:
        # Mô phỏng quá trình stream dữ liệu từ local server lên Cloud Object Storage
        print(f"[MinIO Storage] 📦 Đang tải {filename} lên bucket '{self.bucket_name}'...")
        time.sleep(0.4)  # Giả lập mạng
        return f"s3://{self.bucket_name}/{filename}"