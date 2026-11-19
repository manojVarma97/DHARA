from datetime import date
from pydantic import BaseModel, Field

class ItemIn(BaseModel):
    sku: str
    quantity: int = Field(ge=1, le=100)

class OrderIn(BaseModel):
    customer_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=8, max_length=20)
    city: str = Field(min_length=2, max_length=100)
    address: str = Field(min_length=5, max_length=500)
    delivery_date: date
    delivery_slot_id: int | None = None
    items: list[ItemIn] = Field(min_length=1)

class QuoteIn(BaseModel):
    customer_name: str
    phone: str
    city: str
    address: str
    items: list[ItemIn] = Field(min_length=1)
