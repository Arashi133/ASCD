from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Chuỗi kết nối đến PostgreSQL (Bạn có thể sửa lại user, password, db_name theo máy của bạn)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/xuly_banve"

# Khởi tạo Engine và Session để kết nối và truy vấn DB
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Hàm get_db (Yield) để FastAPI Dependency Injection gọi mỗi khi cần CRUD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()