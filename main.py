from contextlib import asynccontextmanager
from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Expense
from .schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate, ExpenseSummary

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Creates tables for this starter project. For production, use migrations.
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Expense Tracker API",
    description="A REST API to create, manage, filter, and summarize expenses.",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/", tags=["Health"])
def root():
    return {"message": "Expense Tracker API is running", "docs": "/docs"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

@app.post("/expenses", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED, tags=["Expenses"])
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    expense = Expense(**payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

@app.get("/expenses", response_model=list[ExpenseRead], tags=["Expenses"])
def list_expenses(
    category: str | None = Query(default=None, min_length=1, max_length=50),
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be on or before end_date")

    query = select(Expense)
    if category:
        query = query.where(func.lower(Expense.category) == category.lower())
    if start_date:
        query = query.where(Expense.expense_date >= start_date)
    if end_date:
        query = query.where(Expense.expense_date <= end_date)
    query = query.order_by(Expense.expense_date.desc(), Expense.id.desc()).limit(limit).offset(offset)
    return list(db.scalars(query).all())

@app.get("/expenses/{expense_id}", response_model=ExpenseRead, tags=["Expenses"])
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@app.put("/expenses/{expense_id}", response_model=ExpenseRead, tags=["Expenses"])
def update_expense(expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense

@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Expenses"])
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return None

@app.get("/summary", response_model=ExpenseSummary, tags=["Reports"])
def expense_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be on or before end_date")

    conditions = []
    if start_date:
        conditions.append(Expense.expense_date >= start_date)
    if end_date:
        conditions.append(Expense.expense_date <= end_date)

    total = db.scalar(select(func.coalesce(func.sum(Expense.amount), 0)).where(*conditions))
    count = db.scalar(select(func.count(Expense.id)).where(*conditions)) or 0
    rows = db.execute(
        select(Expense.category, func.sum(Expense.amount))
        .where(*conditions)
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
    ).all()

    return ExpenseSummary(
        total_amount=Decimal(str(total)),
        expense_count=count,
        category_totals=[{"category": category, "total": Decimal(str(amount))} for category, amount in rows],
    )
