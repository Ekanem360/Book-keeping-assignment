from typing import List, Optional
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException, Query, status
import models
from sqlalchemy import distinct
from sqlalchemy.orm import Session
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bookstore API")


@app.post(
    "/books/",
    response_model=schemas.BookResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@app.get("/books/", response_model=List[schemas.BookResponse])
def get_books(
    category: Optional[str] = None,
    published_after: Optional[int] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = Query(
        None,
        description="Sort field options: 'price', 'published_year', 'title', etc.",
    ),
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(models.Book)

    if category:
        query = query.filter(models.Book.category.ilike(category))
    if published_after is not None:
        query = query.filter(models.Book.published_year > published_after)
    if max_price is not None:
        query = query.filter(models.Book.price <= max_price)

    if sort_by:
        if hasattr(models.Book, sort_by):
            query = query.order_by(getattr(models.Book, sort_by))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort field '{sort_by}'",
            )

    return query.offset(skip).limit(limit).all()


@app.get("/categories/", response_model=List[str])
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(distinct(models.Book.category)).all()
    return [c[0] for c in categories if c[0] is not None]


@app.get("/categories/{category}", response_model=List[schemas.BookResponse])
def get_books_by_category(category: str, db: Session = Depends(get_db)):
    return (
        db.query(models.Book)
        .filter(models.Book.category.ilike(category))
        .all()
    )


@app.get("/books/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return book


@app.put("/books/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int,
    updated_book: schemas.BookCreate,
    db: Session = Depends(get_db),
):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    for key, value in updated_book.model_dump().items():
        setattr(db_book, key, value)

    db.commit()
    db.refresh(db_book)
    return db_book


@app.patch("/books/{book_id}", response_model=schemas.BookResponse)
def patch_book(
    book_id: int,
    book_update: schemas.BookUpdate,
    db: Session = Depends(get_db),
):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    update_data = book_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_book, key, value)

    db.commit()
    db.refresh(db_book)
    return db_book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    db.delete(db_book)
    db.commit()
    return None
