"""SQLAlchemy database models."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Book(Base):
    """Book model representing Packt books."""
    
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    isbn = Column(String, unique=True, nullable=False, index=True)
    title = Column(Text)
    author = Column(Text)
    packt_price = Column(Float)
    packt_url = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    csv_row_hash = Column(String)  # For change detection
    
    # Relationships
    price_history = relationship("PriceHistory", back_populates="book", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="book", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Book(isbn='{self.isbn}', title='{self.title}', price={self.packt_price})>"


class PriceHistory(Base):
    """Price history model for tracking price changes over time."""
    
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False, index=True)
    source = Column(String)  # 'packt', 'google_books', 'open_library'
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    book = relationship("Book", back_populates="price_history")
    
    def __repr__(self):
        return f"<PriceHistory(book_id={self.book_id}, source='{self.source}', price={self.price})>"


class CSVSyncLog(Base):
    """Log of CSV synchronization operations."""
    
    __tablename__ = 'csv_sync_log'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    last_processed_hash = Column(String)
    last_processed_time = Column(DateTime, default=datetime.utcnow)
    rows_processed = Column(Integer, default=0)
    rows_inserted = Column(Integer, default=0)
    rows_updated = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<CSVSyncLog(filename='{self.filename}', processed={self.rows_processed})>"


class Alert(Base):
    """Alert model for price drop notifications."""
    
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False, index=True)
    threshold_type = Column(String)  # 'percentage' or 'absolute'
    threshold_value = Column(Float)
    packt_price = Column(Float)
    third_party_price = Column(Float)
    third_party_source = Column(String)
    notified_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='pending')  # 'pending', 'sent', 'failed'
    
    # Relationships
    book = relationship("Book", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert(book_id={self.book_id}, status='{self.status}', packt={self.packt_price}, third_party={self.third_party_price})>"

