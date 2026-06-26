from datetime import datetime

from pydantic import BaseModel


class ItemBase(BaseModel):
    name: str
    category: str | None = None
    unit: str | None = None
    min_quantity: int = 0
    current_quantity: int = 0
    is_favorite: bool = False


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    unit: str | None = None
    min_quantity: int | None = None
    current_quantity: int | None = None
    is_favorite: bool | None = None


class ItemResponse(ItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BulkUpdateRequest(BaseModel):
    text_input: str


class OrderResponse(BaseModel):
    id: int
    item_id: int
    order_quantity: int
    status: str
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True
