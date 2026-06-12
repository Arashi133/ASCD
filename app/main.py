import uvicorn
from fastapi import FastAPI
import gradio as gr
from app.api.endpoints import router as api_router
from app.core.config import settings
from app.api.dashboard_endpoints import router as dashboard_router
from app.api.ui_gradio import demo  # Import giao diện Gradio từ file ui_gradio.py

# 1. Khởi tạo ứng dụng FastAPI duy nhất
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Cổng tiếp nhận Gateway & Dashboard tích hợp giao diện trích xuất hình học bản vẽ MEP",
    version="1.0.0"
)

# 2. Đăng ký các tuyến đường API (Routers)
# Cổng nhận file cũ với tiền tố /api/v1 (Giai đoạn Ingestion)
app.include_router(api_router, prefix="/api/v1")

# Cổng xử lý logic CRUD & xuất dữ liệu JSON cho Dashboard mới
app.include_router(dashboard_router) 

# 3. Nhúng (Mount) giao diện Gradio chạy chung một server tại đường dẫn /gui
app = gr.mount_gradio_app(app, demo, path="/gui")

# 4. Định nghĩa hàm kiểm tra trạng thái hệ thống tại đường dẫn gốc
@app.get("/")
async def root():
    return {
        "status": "online", 
        "message": "Hệ thống Backend Xử lý Bản vẽ MEP đã sẵn sàng!",
        "docs_url": "http://127.0.0.1:8000/docs",
        "gui_url": "http://127.0.0.1:8000/gui"
    }

# 5. Khởi chạy Server Uvicorn
if __name__ == "__main__":
    # Sử dụng "app.main:app" vì file main.py nằm bên trong thư mục app
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)