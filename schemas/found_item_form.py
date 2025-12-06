from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


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

    @field_validator("item_color", "item_brand", "found_time", "circumstances", "found_by_firstname", "found_by_lastname", "found_by_phonenumber", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v

class FoundItemFormResponse(BaseModel):
    id: str
    registry_number: Optional[str] = None

    item_name: str
    item_color: Optional[str] = None
    item_brand: Optional[str] = None
    found_location: Optional[str] = None

    # zamiast date
    found_date: Optional[datetime] = None

    found_time: Optional[str] = None
    circumstances: Optional[str] = None
    found_by_firstname: Optional[str] = None
    found_by_lastname: Optional[str] = None
    found_by_phonenumber: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
