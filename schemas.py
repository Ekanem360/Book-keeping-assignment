from typing import Optional
from pydantic import BaseModel

class BookBase(BaseModel):
    title: str
    author: str
    price: float
    category: str
    in_stock: bool = True
    published_year: Optional[int] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    in_stock: Optional[bool] = None
    published_year: Optional[int] = None

class BookResponse(BookBase):
    id: int
    class Config:
        from_attributes = True