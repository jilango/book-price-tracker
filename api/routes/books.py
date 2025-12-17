"""Book endpoints."""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Depends
from api.models import BookResponse, BookListResponse, PriceHistoryResponse
from api.services.book_service import BookService
from api.dependencies import get_database

router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("", response_model=BookListResponse)
async def list_books(
    search: Optional[str] = Query(None, description="Search by title, author, or ISBN"),
    sort: str = Query("id", description="Sort field"),
    order: str = Query("asc", description="Sort order (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    alert_only: bool = Query(False, description="Show only books with active alerts"),
    db=Depends(get_database)
):
    """List all books with filtering, sorting, and pagination."""
    books, total = BookService.get_books(
        search=search,
        sort=sort,
        order=order,
        page=page,
        limit=limit,
        alert_only=alert_only
    )
    
    total_pages = (total + limit - 1) // limit
    
    # Convert to dicts to avoid session issues
    book_dicts = []
    for book in books:
        book_dicts.append({
            'id': book.id,
            'isbn': book.isbn,
            'title': book.title,
            'author': book.author,
            'packt_price': book.packt_price,
            'packt_url': book.packt_url,
            'last_updated': book.last_updated.isoformat() if book.last_updated else None,
            'created_at': book.created_at.isoformat() if book.created_at else None,
        })
    
    return BookListResponse(
        books=[BookResponse(**book_dict) for book_dict in book_dicts],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/{isbn}", response_model=BookResponse)
async def get_book_by_isbn(isbn: str, db=Depends(get_database)):
    """Get book by ISBN."""
    book = BookService.get_book_by_isbn(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookResponse.model_validate(book)


@router.get("/{book_id}/price-history", response_model=list[PriceHistoryResponse])
async def get_price_history(
    book_id: int,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db=Depends(get_database)
):
    """Get price history for a book."""
    book = BookService.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    history = BookService.get_price_history(book_id, limit=limit)
    return [PriceHistoryResponse.model_validate(ph) for ph in history]

