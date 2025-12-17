"""Business logic for book operations."""

from typing import List, Optional, Tuple
from sqlalchemy import or_, func
from src.storage.models import Book, PriceHistory
from src.storage.database import db


class BookService:
    """Service for book-related operations."""
    
    @staticmethod
    def get_books(
        search: Optional[str] = None,
        sort: str = "id",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
        alert_only: bool = False
    ) -> Tuple[List[Book], int]:
        """
        Get books with filtering, sorting, and pagination.
        
        Returns:
            Tuple of (books list, total count)
        """
        with db.get_session() as session:
            query = session.query(Book)
            
            # Search filter
            if search:
                search_filter = or_(
                    Book.title.ilike(f"%{search}%"),
                    Book.author.ilike(f"%{search}%"),
                    Book.isbn.ilike(f"%{search}%")
                )
                query = query.filter(search_filter)
            
            # Alert-only filter (books with active alerts)
            if alert_only:
                from src.storage.models import Alert
                from datetime import datetime, timedelta
                from src.config import config
                
                cooldown_hours = config.notification_cooldown_hours
                cutoff_time = datetime.utcnow() - timedelta(hours=cooldown_hours)
                
                query = query.join(Alert).filter(
                    Alert.notified_at >= cutoff_time,
                    Alert.status == 'sent'
                )
            
            # Get total count before pagination
            total = query.count()
            
            # Sorting
            sort_column = getattr(Book, sort, Book.id)
            if order.lower() == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
            
            # Pagination
            offset = (page - 1) * limit
            books = query.offset(offset).limit(limit).all()
            
            # Expunge books from session so they can be used after session closes
            # This prevents DetachedInstanceError
            for book in books:
                session.expunge(book)
            
            return books, total
    
    @staticmethod
    def get_book_by_isbn(isbn: str) -> Optional[Book]:
        """Get book by ISBN."""
        return db.get_book_by_isbn(isbn)
    
    @staticmethod
    def get_book_by_id(book_id: int) -> Optional[Book]:
        """Get book by ID."""
        with db.get_session() as session:
            book = session.query(Book).filter(Book.id == book_id).first()
            if book:
                session.expunge(book)
            return book
    
    @staticmethod
    def get_price_history(book_id: int, limit: int = 100) -> List[PriceHistory]:
        """Get price history for a book."""
        with db.get_session() as session:
            history = session.query(PriceHistory).filter(
                PriceHistory.book_id == book_id
            ).order_by(PriceHistory.timestamp.desc()).limit(limit).all()
            
            # Expunge from session
            for ph in history:
                session.expunge(ph)
            
            return history

