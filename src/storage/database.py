"""Database operations and session management."""

import os
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from src.storage.models import Base, Book, PriceHistory, CSVSyncLog, Alert
from src.config import config


class Database:
    """Database manager for SQLite operations."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection."""
        self.db_path = db_path or config.db_path
        self._ensure_db_directory()
        self.engine = create_engine(
            f'sqlite:///{self.db_path}',
            echo=False,
            connect_args={'check_same_thread': False}
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._create_tables()
    
    def _ensure_db_directory(self) -> None:
        """Ensure the database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def get_session(self):
        """Get a database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Book operations
    def get_book_by_isbn(self, isbn: str) -> Book | None:
        """Get a book by ISBN."""
        with self.get_session() as session:
            return session.query(Book).filter(Book.isbn == isbn).first()
    
    def create_book(self, isbn: str, title: str = None, author: str = None,
                   packt_price: float = None, packt_url: str = None,
                   csv_row_hash: str = None) -> Book:
        """Create a new book."""
        with self.get_session() as session:
            book = Book(
                isbn=isbn,
                title=title,
                author=author,
                packt_price=packt_price,
                packt_url=packt_url,
                csv_row_hash=csv_row_hash
            )
            session.add(book)
            session.commit()
            session.refresh(book)
            return book
    
    def update_book(self, book_id: int, **kwargs) -> Book | None:
        """Update book fields."""
        with self.get_session() as session:
            book = session.query(Book).filter(Book.id == book_id).first()
            if book:
                for key, value in kwargs.items():
                    if hasattr(book, key):
                        setattr(book, key, value)
                book.last_updated = datetime.utcnow()
                session.commit()
                session.refresh(book)
            return book
    
    def get_all_books(self) -> list[Book]:
        """Get all books from database."""
        with self.get_session() as session:
            return session.query(Book).all()
    
    # Price history operations
    def add_price_history(self, book_id: int, source: str, price: float) -> PriceHistory:
        """Add a price history entry."""
        with self.get_session() as session:
            price_history = PriceHistory(
                book_id=book_id,
                source=source,
                price=price
            )
            session.add(price_history)
            session.commit()
            session.refresh(price_history)
            return price_history
    
    # CSV sync log operations
    def get_latest_sync_log(self, filename: str) -> CSVSyncLog | None:
        """Get the latest sync log for a filename."""
        with self.get_session() as session:
            sync_log = session.query(CSVSyncLog).filter(
                CSVSyncLog.filename == filename
            ).order_by(CSVSyncLog.last_processed_time.desc()).first()
            if sync_log:
                # Expunge to avoid detached instance errors
                session.expunge(sync_log)
            return sync_log
    
    def create_sync_log(self, filename: str, last_processed_hash: str,
                       rows_processed: int, rows_inserted: int,
                       rows_updated: int) -> CSVSyncLog:
        """Create a new sync log entry."""
        with self.get_session() as session:
            sync_log = CSVSyncLog(
                filename=filename,
                last_processed_hash=last_processed_hash,
                rows_processed=rows_processed,
                rows_inserted=rows_inserted,
                rows_updated=rows_updated
            )
            session.add(sync_log)
            session.commit()
            session.refresh(sync_log)
            return sync_log
    
    # Alert operations
    def create_alert(self, book_id: int, threshold_type: str, threshold_value: float,
                    packt_price: float, third_party_price: float,
                    third_party_source: str, status: str = 'pending') -> Alert:
        """Create a new alert."""
        with self.get_session() as session:
            alert = Alert(
                book_id=book_id,
                threshold_type=threshold_type,
                threshold_value=threshold_value,
                packt_price=packt_price,
                third_party_price=third_party_price,
                third_party_source=third_party_source,
                status=status
            )
            session.add(alert)
            session.commit()
            session.refresh(alert)
            return alert
    
    def get_recent_alerts(self, book_id: int, hours: int) -> list[Alert]:
        """Get recent alerts for a book within the specified hours."""
        from datetime import datetime, timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        with self.get_session() as session:
            return session.query(Alert).filter(
                Alert.book_id == book_id,
                Alert.notified_at >= cutoff_time
            ).all()
    
    def update_alert_status(self, alert_id: int, status: str) -> Alert | None:
        """Update alert status."""
        with self.get_session() as session:
            alert = session.query(Alert).filter(Alert.id == alert_id).first()
            if alert:
                alert.status = status
                session.commit()
                session.refresh(alert)
            return alert


# Global database instance
db = Database()

