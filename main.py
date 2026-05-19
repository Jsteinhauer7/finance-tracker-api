from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, Float, String, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel
from datetime import date
from typing import Optional
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///finance.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class TransactionModel(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)       # 'income' or 'expense'
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, default='')
    date = Column(Date, default=date.today)

Base.metadata.create_all(bind=engine)

class TransactionCreate(BaseModel):
    type: str
    amount: float
    category: str
    description: Optional[str] = ''
    date: Optional[date] = None

class TransactionResponse(BaseModel):
    id: int
    type: str
    amount: float
    category: str
    description: str
    date: date

    class Config:
        from_attributes = True

app = FastAPI(title='Finance Tracker API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/transactions', response_model=list[TransactionResponse])
def get_transactions():
    db = SessionLocal()
    try:
        return db.query(TransactionModel).order_by(TransactionModel.date.desc()).all()
    finally:
        db.close()

@app.post('/transactions', response_model=TransactionResponse, status_code=201)
def add_transaction(body: TransactionCreate):
    if body.type not in ('income', 'expense'):
        raise HTTPException(status_code=400, detail='type must be income or expense')
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail='amount must be positive')
    db = SessionLocal()
    try:
        t = TransactionModel(
            type=body.type,
            amount=body.amount,
            category=body.category,
            description=body.description or '',
            date=body.date or date.today()
        )
        db.add(t)
        db.commit()
        db.refresh(t)
        return t
    finally:
        db.close()

@app.delete('/transactions/{transaction_id}', status_code=204)
def delete_transaction(transaction_id: int):
    db = SessionLocal()
    try:
        t = db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
        if not t:
            raise HTTPException(status_code=404, detail='Transaction not found')
        db.delete(t)
        db.commit()
    finally:
        db.close()

@app.get('/summary')
def get_summary():
    db = SessionLocal()
    try:
        transactions = db.query(TransactionModel).all()
        income = sum(t.amount for t in transactions if t.type == 'income')
        expenses = sum(t.amount for t in transactions if t.type == 'expense')

        category_totals = {}
        for t in transactions:
            if t.type == 'expense':
                category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

        return {
            'income': round(income, 2),
            'expenses': round(expenses, 2),
            'balance': round(income - expenses, 2),
            'by_category': [{'category': k, 'amount': round(v, 2)} for k, v in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)]
        }
    finally:
        db.close()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
