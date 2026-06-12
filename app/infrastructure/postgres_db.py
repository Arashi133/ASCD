import time

class PostgresDB:
    async def initialize_job_state(self, job_id: str, minio_url: str):
        # Mô phỏng câu lệnh INSERT dữ liệu vào 2 bảng Images_Meta và Image_Tasks
        print(f"[PostgreSQL] 💾 [INSERT] Images_Meta -> JobID: {job_id} | Status: pending")
        print(f"[PostgreSQL] 💾 [INSERT] Image_Tasks -> task: line_detection (pending)")
        print(f"[PostgreSQL] 💾 [INSERT] Image_Tasks -> task: ocr (pending)")
        return True