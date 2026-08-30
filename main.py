from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from google import genai

# إعداد قاعدة البيانات الدائمة (SQLite)
DATABASE_URL = "sqlite:///./agricultural_app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PaymentDB(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String, default="USD")
    status = Column(String, default="Completed")
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Smart Agricultural API",
    version="3.0.0",
    description="AI-powered backend API for crop diagnostics and agricultural advisory."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CropDiagnosisRequest(BaseModel):
    crop_name: str
    symptoms: List[str]
    temperature_celsius: float
    humidity_percentage: float

class FertilizationScheduleResponse(BaseModel):
    crop_name: str
    recommended_fertilizer: str
    application_frequency: str
    notes: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "AI Smart Agricultural API is running live!", "status": "active"}

# مسار التشخيص المدعوم بالذكاء الاصطناعي
@app.post("/api/v1/crop/diagnose", response_model=FertilizationScheduleResponse)
def diagnose_crop_with_ai(data: CropDiagnosisRequest):
    try:
        # تهيئة عميل الذكاء الاصطناعي (يأخذ المفتاح تلقائياً من بيئة السيرفر)
        client = genai.Client()
        
        prompt = f"""
        أنت خبير زراعي ذكي ومحترف. قم بتشخيص حالة المحصول التالي بناءً على المعطيات:
        - اسم المحصول: {data.crop_name}
        - الأعراض الظاهرة: {', '.join(data.symptoms)}
        - درجة الحرارة: {data.temperature_celsius} درجة مئوية
        - الرطوبة: {data.humidity_percentage}%

        بناءً على ذلك، أجبني حصرياً وباللغة العربية على شكل نص واضح ودقيق يتضمن:
        1. السماد أو العلاج المقترح بدقة.
        2. معدل وتكرار التطبيق (Frequency).
        3. ملاحظات وتوجيهات علاجية أو وقائية للمزارع.
        """
        
        # استدعاء نموذج الذكاء الاصطناعي
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        ai_text = response.text if response and response.text else "حالة مستقرة، يتابع التسميد المعتاد."

        return FertilizationScheduleResponse(
        	crop_name=data.crop_name,
            recommended_fertilizer="توصية مخصصة بالذكاء الاصطناعي",
            application_frequency="موصى به حسب الحالة",
            notes=ai_text
        )
        
    except Exception as e:
        # في حال حدوث أي ضغط أو نقص في مفتاح الذكاء الاصطناعي، يرجع النظام للتشخيص الاحتياطي تلقائياً
        return FertilizationScheduleResponse(
            crop_name=data.crop_name,
            recommended_fertilizer="Balanced NPK (20-20-20)",
            application_frequency="Every 14 days",
            notes=f"تشخيص احتياطي (خطأ في اتصال AI): المحصول {data.crop_name} يحتاج متابعة رطوبة التربة والعناية العامة."
        )
