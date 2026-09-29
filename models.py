from database import Base
from sqlalchemy import Boolean, Column, Float, Integer, String


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False, index=True)
    in_stock = Column(Boolean, default=True)
    published_year = Column(Integer, nullable=True)
