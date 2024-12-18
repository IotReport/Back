from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/iotproject"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 요청마다 DB 세션 열고 닫기
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
