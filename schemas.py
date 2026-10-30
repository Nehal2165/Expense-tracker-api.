from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class ExpenseBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: str = Field(min_length=1, max_length=50)
    expense_date: date
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("title", "category")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    expense_date: date | None = None
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("title", "category")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value

class ExpenseRead(ExpenseBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CategoryTotal(BaseModel):
    category: str
    total: Decimal

class ExpenseSummary(BaseModel):
    total_amount: Decimal
    expense_count: int
    category_totals: list[CategoryTotal]
