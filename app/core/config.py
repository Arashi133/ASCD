import os


class Settings:
    PROJECT_NAME: str = "MEP Blueprint Async Processing System"
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Thư mục tạm để lưu file client gửi lên trước khi đẩy qua MinIO
    TMP_UPLOAD_DIR: str = os.path.join(BASE_DIR, "storage", "tmp")

    def __init__(self):
        os.makedirs(self.TMP_UPLOAD_DIR, exist_ok=True)


settings = Settings()