"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# Book Models
class BookResponse(BaseModel):
    """Book response model."""
    id: int
    isbn: str
    title: Optional[str] = None
    author: Optional[str] = None
    packt_price: Optional[float] = None
    packt_url: Optional[str] = None
    last_updated: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class BookListResponse(BaseModel):
    """Book list response with pagination."""
    books: List[BookResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# Price History Models
class PriceHistoryResponse(BaseModel):
    """Price history response model."""
    id: int
    book_id: int
    source: str
    price: Optional[float] = None
    timestamp: datetime
    
    model_config = {"from_attributes": True}


# Alert Models
class AlertResponse(BaseModel):
    """Alert response model."""
    id: int
    book_id: int
    book: Optional[BookResponse] = None
    threshold_type: str
    threshold_value: float
    packt_price: float
    third_party_price: float
    third_party_source: str
    notified_at: datetime
    status: str
    
    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    """Alert list response with pagination."""
    alerts: List[AlertResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# Statistics Models
class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response."""
    # Legacy alert fields (kept for backward compatibility)
    total_books: int
    active_alerts: int
    average_price_difference: Optional[float] = None
    total_savings_opportunity: Optional[float] = None
    books_with_alerts: int
    
    # New catalog overview fields
    total_catalog_value: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    average_price: Optional[float] = None
    
    # Data quality fields
    books_missing_authors: int = 0
    books_missing_urls: int = 0
    books_without_price_history: int = 0
    data_completeness_percentage: Optional[float] = None


class PriceTrendDataPoint(BaseModel):
    """Price trend data point."""
    date: str
    packt_price: Optional[float] = None
    third_party_price: Optional[float] = None
    difference: Optional[float] = None


class PriceTrendsResponse(BaseModel):
    """Price trends response."""
    trends: List[PriceTrendDataPoint]
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class ComparisonStatsResponse(BaseModel):
    """Price comparison statistics."""
    total_comparisons: int
    packt_cheaper: int
    third_party_cheaper: int
    average_difference: Optional[float] = None


# Sync Status Models
class SyncStatusResponse(BaseModel):
    """CSV sync status response."""
    last_sync_time: Optional[datetime] = None
    last_sync_hash: Optional[str] = None
    rows_processed: int = 0
    rows_inserted: int = 0
    rows_updated: int = 0
    filename: Optional[str] = None


class SyncHistoryResponse(BaseModel):
    """Sync history response."""
    id: int
    filename: str
    last_processed_time: datetime
    rows_processed: int
    rows_inserted: int
    rows_updated: int
    
    model_config = {"from_attributes": True}


class SyncHistoryListResponse(BaseModel):
    """Sync history list response."""
    history: List[SyncHistoryResponse]
    total: int


# New Statistics Models
class PriceBucket(BaseModel):
    """Price bucket for distribution."""
    range: str  # e.g., "$0-5", "$5-10", etc.
    count: int
    percentage: float


class PriceDistributionResponse(BaseModel):
    """Price distribution response."""
    buckets: List[PriceBucket]
    total_books: int


class DataQualityResponse(BaseModel):
    """Data quality metrics response."""
    total_books: int
    books_missing_authors: int
    books_missing_urls: int
    books_missing_prices: int
    books_without_price_history: int
    books_stale: int  # Not updated in 90+ days
    data_completeness_percentage: float
    books_needing_attention: List[BookResponse]  # Books with issues


class ActivityDataPoint(BaseModel):
    """Recent activity data point."""
    date: str
    books_added: int = 0
    books_updated: int = 0
    total_changes: int = 0


class RecentActivityResponse(BaseModel):
    """Recent activity response."""
    activity: List[ActivityDataPoint]
    date_from: Optional[str] = None
    date_to: Optional[str] = None

