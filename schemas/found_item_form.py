from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class FoundItemFormRequest(BaseModel):
    item_name: str = Field(..., min_length=1)
    item_color: Optional[str] = None
    item_brand: Optional[str] = None
    found_location: str = Field(..., min_length=1)
    found_date: date
    found_time: Optional[str] = None
    circumstances: Optional[str] = None
    found_by_firstname: Optional[str] = None
    found_by_lastname: Optional[str] = None
    found_by_phonenumber: Optional[str] = None


class FoundItemFormResponse(BaseModel):
    id: str
    item_name: str
    item_color: Optional[str] = None
    item_brand: Optional[str] = None
    found_location: Optional[str] = None
    found_date: Optional[date] = None
    found_time: Optional[str] = None
    circumstances: Optional[str] = None
    found_by_firstname: Optional[str] = None
    found_by_lastname: Optional[str] = None
    found_by_phonenumber: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
