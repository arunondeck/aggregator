from typing import Any

from pydantic import BaseModel


class ListingCreate(BaseModel):
    product_family: str
    state: str
    district: str
    city: str
    title: str
    description: str | None = None
    price: float | None = None
    source_name: str
    source_url: str
    attributes: dict[str, Any] = {}


class ListingOut(BaseModel):
    id: int
    product_family: str
    title: str
    price: float | None
    source_name: str
    source_url: str
    location: dict[str, str]
    attributes: dict[str, Any]

    class Config:
        from_attributes = True
