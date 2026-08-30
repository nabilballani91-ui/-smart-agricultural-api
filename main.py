from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# إعداد قاعدة البيانات الدائمة (SQLite)
DATABASE_URL = "sqlite:///./agricultural_app.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# تعريف جدول المعاملات والمدفوعات في قاعدة البيانات
class PaymentDB(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String, default="USD")
    status = Column(String, default="Completed")
    created_at = Column(DateTime, default=datetime.utcnow)

# إنشاء الجداول تلقائياً
Base.metadata.create_all(bind=engine)

# تهيئة تطبيق FastAPI
app = FastAPI(
    title="Smart Agricultural & Payment API",
    version="2.0.0",
    description="Backend API designed for crop diagnostics, fertilization tracking, and streamlined payment processing."
)

# نماذج البيانات (Pydantic Models)
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

class PaymentCreate(BaseModel):
    customer_name: str
    amount: float
    currency: str = "USD"
    status: str = "Completed"

# Dependency لجلب جلسة قاعدة البيانات
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# المسار الرئيسي (Root Endpoint)
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Smart Agricultural & Payment API with Persistent DB",
        "docs_url": "/docs",
        "version": "2.0.0",
        "framework": "FastAPI & SQLAlchemy"
    }

@app.get("/health")
def health_check():
    return {"status": "active", "server": "running"}

# مسار التشخيص الزراعي وجدولة التسميد
@app.post("/api/v1/crop/diagnose", response_model=FertilizationScheduleResponse)
def diagnose_crop(data: CropDiagnosisRequest):
    symptoms_lower = [s.lower() for s in data.symptoms]
    
    # منطق التشخيص والمحاكاة الزراعية
    if "yellow leaves" in symptoms_lower or "yellowing" in symptoms_lower:
        fertilizer = "Nitrogen-rich Urea (46-0-0)"
        frequency = "Every 7-10 days"
        notes = f"Detected nitrogen deficiency in {data.crop_name}. Recommended immediate application with adequate irrigation."
    elif "wilting" in symptoms_lower or "dry" in symptoms_lower:
        fertilizer = "Balanced NPK (20-20-20) with Potassium humate"
        frequency = "Every 14 days"
        notes = f"Wilting observed at {data.temperature_celsius}°C. Ensure proper soil moisture balance."
    else:
        fertilizer = "Standard Organic Compost & Micronutrients"
        frequency = "Once a month"
        notes = f"Crop {data.crop_name} is in stable condition. Maintain regular preventive care routine."
        
    return FertilizationScheduleResponse(
        crop_name=data.crop_name,
        recommended_fertilizer=fertilizer,
        application_frequency=frequency,
        notes=notes
    )

# مسار إضافة معاملة أو مدفوعات جديدة (محفوظة بقاعدة البيانات)
@app.post("/api/v1/payments/", status_code=status.HTTP_201_CREATED)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    db_payment = PaymentDB(
        customer_name=payment.customer_name,
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return {
        "message": "Payment recorded successfully in persistent database",
        "data": {
            "id": db_payment.id,
            "customer_name": db_payment.customer_name,
            "amount": db_payment.amount,
            "currency": db_payment.currency,
            "status": db_payment.status,
            "created_at": db_payment.created_at
        }
    }

# مسار جلب كافة المعاملات والمدفوعات المسجلة
@app.get("/api/v1/payments/")
def get_payments(db: Session = Depends(get_db)):
    payments = db.query(PaymentDB).all()
    return payments
