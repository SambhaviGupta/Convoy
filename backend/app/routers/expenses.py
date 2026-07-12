from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("", response_model=List[schemas.ExpenseOut])
def list_expenses(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(models.Expense).order_by(models.Expense.id.desc()).all()


@router.post("", response_model=schemas.ExpenseOut)
def create_expense(
    payload: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == payload.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    expense = models.Expense(
        vehicle_id=payload.vehicle_id,
        type=payload.type,
        amount=payload.amount,
        date=payload.date or date.today(),
        notes=payload.notes,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense
