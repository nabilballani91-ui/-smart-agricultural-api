from datetime import datetime
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
    description="Backend API with Persistent DB for Smart Agriculture and Payments"
)

# نموذج البيانات (Pydantic Schema)
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
        "database": DATABASE_URL,
        "framework": "FastAPI 2.0.0 & SQLAlchemy Engine",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# مسار إضافة معاملة أو مدفوعات جديدة
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
