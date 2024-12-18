from fastapi import FastAPI, Depends, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from typing import List
from app.api import models, database
from app.api.database import get_db, engine, SessionLocal
from app.api.models import Report, Base
from app.api.schemas import ReportInfoSchema, ReportCreateSchema, UpdateReceiveSchema
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI()

# 데이터베이스 초기화 (테이블 생성)
models.Base.metadata.create_all(bind=database.engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.0.3:3000"],  # React 앱의 주소
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

def delete_expired_reports():
    db: Session = SessionLocal()
    try:
        # 현재 시간 기준으로 30분 초과된 보고서를 삭제
        threshold_time = datetime.utcnow() - timedelta(seconds=30)
        expired_reports = db.query(Report).filter(Report.receive == True, Report.updated_at < threshold_time).all()
        for report in expired_reports:
            db.delete(report)
        db.commit()
    finally:
        db.close()

# 스케줄러 설정
scheduler = BackgroundScheduler()
scheduler.add_job(delete_expired_reports, "interval", seconds=30)  # 30분마다 실행
scheduler.start()

# FastAPI 종료 이벤트에 스케줄러 종료 추가
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/reportInfo/{reportId}", response_model=ReportInfoSchema)
def get_report(reportId: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.reportId == reportId).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@app.get("/reports", response_model=List[ReportInfoSchema])
def read_report_info(db: Session = Depends(get_db)):
    # 데이터베이스에서 필요한 필드만 선택
    reports = db.query(Report).all()
    return reports

@app.post("/reporting")
def create_report(report: ReportCreateSchema, db: Session = Depends(get_db)):
    # 중복 검증 (선택 사항)
    existing_report = db.query(Report).filter(Report.address == report.address, Report.date == report.date).first()
    if existing_report:
        raise HTTPException(status_code=400, detail="Report already exists")

    # 새 보고서 추가
    new_report = Report(
        address=report.address,
        password=report.password,
        name=report.name,
        date=report.date,
        receive=False  # 기본값 설정
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

@app.patch("/reports/{reportId}")
def update_receive_status(reportId: int, payload: UpdateReceiveSchema, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.reportId == reportId).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # receive 값 업데이트
    report.receive = payload.receive
    db.commit()
    db.refresh(report)
    return report